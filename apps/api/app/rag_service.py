"""Retrieve product listings and scoped ingredient notes for general chat."""

from __future__ import annotations

import json
import logging
import os
import re
from collections.abc import Iterable
from pathlib import Path

import psycopg

from .concerns import normalize_concern
from .embeddings import question_embedding

ROOT = Path(__file__).resolve().parents[3] / "data/seeds"
LISTING_STATUSES = {"source_observed", "approved"}
WORD = re.compile(r"[^\W_]+")
STOP_WORDS = frozenset("""
    about am an and are at be but by can could do does for from good have help helps how
    i if in is it me my of on or product products recommend should show some tell that
    the their this to use want was what when where which who why will with would you
""".split())
logger = logging.getLogger(__name__)


def words(text: str) -> set[str]:
    return set(WORD.findall(normalize_concern(text)))


def mentions(text: str, phrase: str) -> bool:
    return bool(re.search(rf"(?<!\w){re.escape(normalize_concern(phrase))}(?!\w)", text))


def load_seed(filename: str, default):
    try:
        return json.loads((ROOT / filename).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        logger.warning("Could not load %s (%s)", filename, type(exc).__name__)
        return default


def rank_listing_urls(
    database_url: str, query: str, limit: int, candidates: list[str] | None = None,
) -> list[str]:
    """Rank indexed product passages within the given listing URLs."""
    vector = question_embedding(query)
    with psycopg.connect(database_url, connect_timeout=3) as connection:
        rows = connection.execute("""
            WITH eligible AS (
                SELECT d.source_url, p.search_vector, p.embedding
                FROM source_passages p
                JOIN source_documents d ON d.id = p.document_id
                WHERE d.source_kind = 'official_product_listing'
                  AND (%(candidates)s::text[] IS NULL OR d.source_url = ANY(%(candidates)s::text[]))
            ), lexical AS (
                SELECT source_url, row_number() OVER (ORDER BY
                    ts_rank_cd(search_vector, plainto_tsquery('english', %(query)s)) DESC, source_url) AS rank
                FROM eligible
                WHERE search_vector @@ plainto_tsquery('english', %(query)s)
                ORDER BY rank LIMIT 12
            ), semantic AS (
                SELECT source_url, row_number() OVER (ORDER BY embedding <=> %(vector)s::vector, source_url) AS rank
                FROM eligible
                WHERE embedding IS NOT NULL AND (embedding <=> %(vector)s::vector) < 0.68
                ORDER BY rank LIMIT 12
            )
            SELECT source_url, sum(score) AS score FROM (
                SELECT source_url, 1.0 / (60 + rank) AS score FROM lexical
                UNION ALL SELECT source_url, 1.0 / (60 + rank) AS score FROM semantic
            ) ranked GROUP BY source_url ORDER BY score DESC, source_url LIMIT %(limit)s
        """, {"query": query, "vector": vector, "limit": limit, "candidates": candidates}).fetchall()
    return [url for url, _ in rows]


class ProductRAG:
    def __init__(self):
        self.ingredients = load_seed("ingredient_knowledge.json", [])
        self.disclosures = {
            product_id: record
            for product_id, record in load_seed("product_ingredients.json", {}).items()
            if record.get("capture_sha256")
        }
        self.nutrition = {
            record["product_id"]: record
            for record in load_seed("nutritional_facts.json", {}).get("products", [])
            if record.get("capture_sha256")
        }

    def disclosed_ingredients(self, item: dict) -> list[str]:
        if item.get("ingredients"):
            return item["ingredients"]
        record = self.disclosures.get(item["id"], {})
        return record["ingredients"] if record.get("source_url") == item["source_url"] else []

    def named_ingredients(self, query: str) -> list[str]:
        normalized = normalize_concern(query)
        return [
            row["name"] for row in self.ingredients
            if mentions(normalized, row["name"]) or any(
                mentions(normalized, alias) for alias in row.get("aliases", [])
            )
        ]

    def listing_score(
        self, item: dict, query: str, terms: set[str], ingredients: list[str],
    ) -> tuple[int, int] | None:
        if item["review_status"] not in LISTING_STATUSES:
            return None
        name = normalize_concern(item["name"])
        if ingredients:
            disclosure = normalize_concern(" ".join(self.disclosed_ingredients(item)))
            if not any(mentions(name, word) or mentions(disclosure, word) for word in ingredients):
                return None

        name_matches = words(name) & terms
        category_matches = words(item.get("category") or "") & terms
        brand = normalize_concern(item["brand"])
        # Brand words refine a listing match. Brand-only searches require an exact brand name.
        if not (name_matches or category_matches or ingredients or query == brand):
            return None
        coverage = len(name_matches | category_matches)
        score = 4 * len(name_matches) + 2 * len(category_matches - name_matches) + len(words(brand) & terms)
        return coverage, score

    def search_products(self, query: str, items: Iterable[dict], limit: int, *, hybrid: bool = False) -> list[dict]:
        terms = {term for term in words(query) if len(term) > 2 and term not in STOP_WORDS}
        ingredient_names = self.named_ingredients(query)
        normalized_query = normalize_concern(query)
        if not terms and not ingredient_names:
            return []
        scored = [
            (*score, item) for item in items
            if (score := self.listing_score(item, normalized_query, terms, ingredient_names)) is not None
        ]

        # Use the most specific title/category matches, even when a query contains other words.
        best_coverage = max((coverage for coverage, _, _ in scored), default=0)
        scored = [(score, item) for coverage, score, item in scored if coverage == best_coverage]
        if not scored:
            return []

        indexed_positions = {}
        database_url = os.getenv("DATABASE_URL") if hybrid else None
        if database_url:
            try:
                urls = [item["source_url"] for _, item in scored]
                ranked = rank_listing_urls(database_url, query, max(limit, 12), urls)
                indexed_positions = {url: i for i, url in enumerate(ranked)}
            except Exception as exc:
                logger.warning("Product hybrid ranking unavailable (%s)", type(exc).__name__)

        scored.sort(key=lambda row: (
            -row[0],
            indexed_positions.get(row[1]["source_url"], len(indexed_positions)),
            row[1]["name"],
            row[1]["id"],
        ))
        return [item for _, item in scored[:limit]]

    def build_context(self, query: str, items: list[dict]) -> dict:
        normalized = normalize_concern(query)
        names = self.named_ingredients(query)
        related = [
            row for row in self.ingredients
            if any(mentions(normalized, concern) for concern in row.get("concerns", []))
        ]
        matched = [row for row in self.ingredients if row["name"] in names]
        notes = (matched + [row for row in related if row not in matched])[:5]
        ingredients = [
            {key: row[key] for key in ("name", "category", "benefits", "evidence_level", "source") if key in row}
            for row in notes
        ]
        products = []
        for item in self.search_products(query, items, limit=4, hybrid=True):
            facts = {key: item.get(key) for key in (
                "id", "name", "brand", "price", "currency", "image_url", "source_url",
            )}
            labels = self.disclosed_ingredients(item)
            # Only use an explicit disclosure for ingredient claims.
            matching = [label for label in labels if any(mentions(normalize_concern(label), name) for name in names)]
            facts["key_ingredients"] = (matching + [label for label in labels if label not in matching])[:4]
            if (nutrition := self.nutrition.get(item["id"])) and nutrition.get("source_url") == item["source_url"]:
                facts["nutritional_facts"] = {
                    key: nutrition[key] for key in ("serving_size", "nutrients") if key in nutrition
                }
            products.append(facts)
        return {"products": products, "ingredients": ingredients}


rag_service = ProductRAG()
