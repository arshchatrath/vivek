"""Regression coverage for product-specific source association."""

import hashlib
import json

import pytest

from services.ingestion.extract_ingredients import extract_ingredients, process_all_artifacts


def test_extractor_uses_own_capture_and_ignores_other_product_links(tmp_path):
    artifacts = tmp_path / "artifacts"
    captures = artifacts / "example-brand"
    captures.mkdir(parents=True)
    products = [
        {"id": product_id, "brand": "Example Brand", "source_url": f"https://example.test/product/{product_id}",
         "review_status": "source_observed"}
        for product_id in ("a", "b")
    ]
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"products": products}), encoding="utf-8")
    capture = captures / "a.md"
    capture.write_text(
        "[Related product](https://example.test/product/b)\n"
        "Full list of ingredients\n**Ingredient Names**\n"
        "Water, Compound (A, B), Glycerin\n**Formulated Without**\n",
        encoding="utf-8",
    )
    (captures / "b.md").write_text("View Full List of Ingredients\n## Frequently Bought Together\n", encoding="utf-8")
    output = tmp_path / "seed.json"

    assert process_all_artifacts(artifacts, catalog, output) == 1
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "a": {
            "source_url": products[0]["source_url"],
            "capture_file": capture.name,
            "capture_sha256": hashlib.sha256(capture.read_bytes()).hexdigest(),
            "ingredients": ["Water", "Compound (A, B)", "Glycerin"],
        },
    }


@pytest.mark.parametrize("text", [
    "Full list of ingredients\n**Ingredient Names**\n## Questions you should be asking\nHow to Use",
    "Full list of ingredients\n**Ingredient Names**\nSerum: Water, Glycerin\nHow to Use",
    "Full list of ingredients\n**Ingredient Names**\nWater, Glycerin\nVitamins: A, B\nHow to Use",
    [
        "Full list of ingredients\n**Ingredient Names**\nWater, Aloe\nHow to Use",
        "Full list of ingredients\n**Ingredient Names**\nWater, Glycerin\nHow to Use",
    ],
])
def test_extractor_skips_incomplete_or_ambiguous_sections(text):
    markdown = "\n".join(text) if isinstance(text, list) else text
    assert extract_ingredients(markdown) == []
