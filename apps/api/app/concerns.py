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

from .embeddings import question_embedding


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
    r"swollen|allergic|allergy|burning|patchy|sudden\w*|blisters?|"
    r"dosage|what dose|how much should i take|drug interactions?|"
    r"can i (?:mix|combine)|can i take .+ together)\b"
    r"|बच्च[ाेी]|गर्भ|bacha|bachcha",
    re.I,
)
CONTEXT_FOLLOWUP = re.compile(
    r"(?:when should i (?:seek care|see (?:a doctor|a clinician|a dermatologist)|get (?:this|it) checked)"
    r"|what (?:can|should) i (?:do|try)(?: about (?:it|this))?|why does (?:it|this) happen"
    r"|how long (?:will|does) (?:it|this) last)[?.!]*",
)
URGENT_SPELLINGS = (
    "chest pain", "can't breathe", "cannot breathe", "difficulty breathing", "trouble breathing",
    "shortness of breath", "swollen tongue", "anaphylaxis", "seizures", "suicidal",
)
ENGLISH_WORDS = re.compile(r"[a-z]+(?:'[a-z]+)?")
URGENT_MESSAGE = "These symptoms can need urgent help. Contact your local emergency service now."
CARE_FIRST_MESSAGE = "Discuss this concern with a qualified clinician before choosing a product."


class ConcernRequest(BaseModel):
    concern: str = Field(min_length=3, max_length=1000)
    topic: str | None = Field(default=None, max_length=50, pattern=r"^[a-z-]+$")
    share_followup: bool = False
    share_routing: bool = False

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


def one_edit(observed: str, expected: str, allow_substitution: bool) -> bool:
    if observed == expected or abs(len(observed) - len(expected)) > 1:
        return False
    if len(observed) > len(expected):
        observed, expected = expected, observed
    index = next((i for i, (a, b) in enumerate(zip(observed, expected)) if a != b), len(observed))
    if len(observed) < len(expected):
        return observed[index:] == expected[index + 1:]
    if allow_substitution and observed[index + 1:] == expected[index + 1:]:
        return True
    return (observed[index:index + 2] == expected[index:index + 2][::-1]
            and observed[index + 2:] == expected[index + 2:])


def typo_near_alias(words: list[str], alias: str) -> bool:
    expected = alias.split()
    if not all(ENGLISH_WORDS.fullmatch(word) for word in expected):
        return False
    for start in range(len(words) - len(expected) + 1):
        window = words[start:start + len(expected)]
        differences = [(a, b) for a, b in zip(window, expected) if a != b]
        if len(differences) == 1:
            observed, original = differences[0]
            if len(original) >= 4 and len(observed) >= 3 and one_edit(
                observed, original, allow_substitution=len(original) >= 5 or len(expected) > 1,
            ):
                return True
    return False


def related_topics(question: str):
    words = ENGLISH_WORDS.findall(question)
    return [
        guide["id"] for guide in guides().values()
        if any(
            re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", question) or typo_near_alias(words, alias)
            for alias in map(normalize_concern, guide["aliases"])
        )
    ]


def search_topics(question: str) -> tuple[str | None, list[str]]:
    """Use the checked topic profiles for meaning and word overlap."""
    url = os.getenv("DATABASE_URL")
    if not url:
        return None, []
    try:
        vector = question_embedding(question)
        with psycopg.connect(url, connect_timeout=3) as connection:
            rows = connection.execute("""
                WITH query AS (
                    SELECT %s::vector AS embedding,
                           tsvector_to_array(to_tsvector('english', %s)) AS words
                )
                SELECT topic, 1 - (concern_topics.embedding <=> query.embedding) AS similarity,
                       cardinality(ARRAY(
                           SELECT unnest(tsvector_to_array(search_vector))
                           INTERSECT SELECT unnest(query.words)
                       )) AS word_matches
                FROM concern_topics CROSS JOIN query
            """, (vector, question)).fetchall()
    except Exception as exc:
        log.warning("Concern topic lookup unavailable (%s)", type(exc).__name__)
        return None, []

    ranked = sorted(
        ((similarity + 0.03 * min(words, 4), topic, similarity, words)
         for topic, similarity, words in rows if topic in guides()),
        reverse=True,
    )
    if not ranked:
        return None, []
    score, topic, similarity, words = ranked[0]
    margin = score - ranked[1][0] if len(ranked) > 1 else score
    # A clear lead and multiple matched words are required before opening a guide.
    if similarity >= 0.43 and words >= 2 and score >= 0.54 and margin >= 0.08:
        return topic, []
    candidates = [topic for _, topic, similarity, words in ranked if similarity >= 0.38 and words >= 2]
    return None, candidates[:3]


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
    words = ENGLISH_WORDS.findall(question)
    if URGENT.search(question) or any(typo_near_alias(words, alias) for alias in URGENT_SPELLINGS):
        return {"status": "urgent", "message": URGENT_MESSAGE}
    matches = related_topics(question)
    multiple_concerns = len(matches) > 1
    context = request.topic if request.topic in guides() else None
    care_first = bool(CARE_FIRST.search(question))
    selected = context if context and not request.share_followup and (not matches or context in matches) else None
    if not selected and len(matches) == 1:
        selected = matches[0]
    if not selected and not matches and not care_first:
        selected, matches = search_topics(question)
        if not selected and context and request.share_followup and CONTEXT_FOLLOWUP.fullmatch(question):
            selected = context
    if not selected:
        if care_first:
            return {"status": "care_first", "message": CARE_FIRST_MESSAGE}
        options = [topic for topic in covered_topics() if not matches or topic["id"] in matches]
        if matches:
            return {
                "status": "clarify",
                "message": "Which option best describes what you’re noticing?",
                "topics": options,
                "can_retry_with_groq": not multiple_concerns,
            }
        return {
            "status": "outside_coverage",
            "message": "Vivek couldn’t find a supported topic for that description. What changes have you noticed, and where?",
            "topics": options,
            "can_retry_with_groq": True,
        }

    guide = guides()[selected]
    cards, retrieval = guidance_for(guide, question)
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
