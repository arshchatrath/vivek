"""Route concerns to sourced educational guidance and checked listing facts."""

from functools import lru_cache
import json
import logging
import os
from pathlib import Path
import re
from unicodedata import normalize

import psycopg
from pydantic import BaseModel, Field, field_validator


SEED = Path(__file__).resolve().parents[3] / "data/seeds/concerns.json"
log = logging.getLogger(__name__)
URGENT = re.compile(
    r"\b(chest pain|can(?:not|'t) breathe|(?:difficulty|trouble) breathing|shortness of breath|"
    r"(?:lips?|tongue|throat) (?:are |is )?(?:swelling|swollen)|swollen (?:lips?|tongue|throat)|"
    r"throat (?:is )?closing|severe allergic reaction|anaphylaxis|vomiting blood|blood in (?:my )?vomit|"
    r"suicid\w*|(?:kill|harm) myself|unconscious|seizures?)\b"
    r"|सांस नहीं|साँस नहीं|saans (?:nahi|nahin|lene mein)",
    re.I,
)
CARE_FIRST = re.compile(
    r"\b(pregnan\w*|breastfeed\w*|child|kid|baby|infant|teen\w*|minor|under 18|"
    r"(?:[1-9]|1[0-7])\s*(?:years?\s*old|yr\s*old)|"
    r"bleeding|blood in (?:my |the )?(?:stool|poo)|(?:cannot|can't) pass gas|vomiting|pus|fever|painful|pain|"
    r"swollen|allergic|allergy|burning|patchy|sudden\w*|blisters?)\b"
    r"|बच्च[ाेी]|गर्भ|bacha|bachcha",
    re.I,
)
CLARIFY = (
    "Describe what you notice, where it is, and how long it has been happening. "
    "If several concerns match, choose one to explore first."
)


class ConcernRequest(BaseModel):
    concern: str = Field(min_length=3, max_length=1000)
    topic: str | None = Field(default=None, max_length=50, pattern=r"^[a-z-]+$")
    share_followup: bool = False

    @field_validator("concern", mode="before")
    @classmethod
    def trim_concern(cls, value):
        return value.strip() if isinstance(value, str) else value


@lru_cache(maxsize=1)
def guides() -> dict:
    return {guide["id"]: guide for guide in json.loads(SEED.read_text(encoding="utf-8"))}


def normalize_concern(value: str) -> str:
    text = normalize("NFKC", value).casefold().replace("’", "'").translate(str.maketrans("-‐‑", "   "))
    return " ".join(text.split())


def covered_topics():
    return [{"id": guide["id"], "title": guide["title"]} for guide in guides().values()]


def related_topics(question: str):
    return [
        guide["id"] for guide in guides().values()
        if any(re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", question) for alias in guide["aliases"])
    ]


def guidance_for(guide: dict, question: str) -> tuple[list[dict], str]:
    """Retrieve sources within the matched topic. The seed also works without a DB."""
    cards = guide["guidance"]
    retrieval = "local_guidance"
    if (url := os.getenv("DATABASE_URL")):
        try:
            with psycopg.connect(url, connect_timeout=3) as connection:
                ranked = connection.execute("""
                    SELECT passage_key FROM concern_passages WHERE topic = %s
                    ORDER BY ts_rank_cd(search_vector, websearch_to_tsquery('english', %s)) DESC, position
                """, (guide["id"], question)).fetchall()
            if ranked:
                indexed = {card["id"]: card for card in cards}
                cards = [indexed[key] for (key,) in ranked if key in indexed]
                if len(cards) == len(indexed):
                    retrieval = "postgres_guidance"
                else:
                    cards = guide["guidance"]
        except psycopg.Error as exc:
            log.warning("Concern guidance DB lookup failed (%s)", type(exc).__name__)
    return [{**card, "source": guide["sources"][card["source"]]} for card in cards], retrieval


def checked_products(ingredient: dict, by_url: dict) -> list[dict]:
    matches = []
    for candidate in ingredient["matches"]:
        item = by_url.get(candidate["url"])
        if item is None or item.get("review_status") not in {"source_observed", "approved"}:
            continue
        listing = f"{item['name']} {item.get('description') or ''}".casefold()
        if not all(term in listing for term in candidate["terms"]):
            continue
        matches.append({key: item.get(key) for key in (
            "id", "brand", "name", "source_url", "captured_at", "availability",
        )})
    return matches


def ingredient_options(guide: dict, products: list[dict]) -> list[dict]:
    by_url = {product["source_url"]: product for product in products}
    return [
        {"name": ingredient["name"], "form": ingredient["form"],
         "evidence": guide["sources"][ingredient["source"]],
         "products": checked_products(ingredient, by_url)}
        for ingredient in guide["ingredients"]
    ]


def resolve_concern(request: ConcernRequest, load_products) -> dict:
    question = normalize_concern(request.concern)
    if URGENT.search(question):
        return {"status": "urgent", "message": "These symptoms can need urgent help. Contact your local emergency service now."}
    matches = related_topics(question)
    if request.topic and request.topic in guides() and (not matches or request.topic in matches):
        guide = guides()[request.topic]
    elif len(matches) == 1:
        guide = guides()[matches[0]]
    else:
        options = [topic for topic in covered_topics() if not matches or topic["id"] in matches]
        if CARE_FIRST.search(question):
            return {"status": "care_first", "message": "Discuss this concern with a qualified clinician before choosing a product."}
        if matches:
            return {"status": "clarify", "message": CLARIFY, "topics": options}
        return {"status": "outside_coverage", "message": "Vivek has no reviewed guidance for this description yet. If symptoms persist or concern you, contact a qualified clinician.", "topics": options}

    cards, retrieval = guidance_for(guide, question)
    care_first = bool(CARE_FIRST.search(question))
    message = "Speak with a qualified clinician before choosing a product." if care_first else None
    ingredients = []
    if not care_first and guide["ingredients"]:
        try:
            ingredients = ingredient_options(guide, load_products())
        except psycopg.Error as exc:
            log.warning("Concern catalog lookup failed (%s)", type(exc).__name__)
            message = "Product listings are temporarily unavailable. The guidance is below."
    return {
        "status": "care_first" if care_first else "guidance",
        "message": message,
        "topic": {"id": guide["id"], "title": guide["title"]},
        "reviewed_on": guide["reviewed_on"],
        "retrieval": retrieval,
        "guidance": [card for card in cards if card["id"] in {"cause", "care"}] if care_first else cards,
        "ingredients": ingredients,
    }
