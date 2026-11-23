"""Extract explicit ingredient disclosures from each product's own Markdown capture."""

import hashlib
import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

ROOT = Path(__file__).resolve().parents[2]
LIST_HEADING = re.compile(r"full list of ingredients:?", re.I)
NAMES_HEADING = re.compile(r"ingredient names:?", re.I)
NEXT_SECTION = re.compile(r"(?:formulated without|important information|how to use)\b", re.I)


def heading_text(line: str) -> str:
    return line.strip(" #*\t")


def extract_ingredients(markdown: str) -> list[str]:
    """Read explicit, single-paragraph ingredient notices for single listings."""
    lines = [line.strip() for line in markdown.splitlines() if line.strip()]
    disclosures = set()
    for heading, names, text, following in zip(lines, lines[1:], lines[2:], lines[3:]):
        if not LIST_HEADING.fullmatch(heading_text(heading)) or not NAMES_HEADING.fullmatch(heading_text(names)):
            continue
        if not NEXT_SECTION.match(heading_text(following)) or any(char in text for char in ":#![]*<>"):
            continue
        # Split at top-level commas so a compound ingredient keeps its qualifiers.
        if text.count("(") != text.count(")"):
            continue
        ingredients = tuple(part.strip() for part in re.split(r",\s*(?![^()]*\))", text))
        if len(ingredients) >= 2 and all(2 <= len(part) <= 180 for part in ingredients):
            disclosures.add(ingredients)
    # Different lists on one page can mean the listing is a multi-product kit.
    return list(disclosures.pop()) if len(disclosures) == 1 else []


def process_all_artifacts(artifacts_dir: Path, catalog_path: Path, output_path: Path) -> int:
    products = json.loads(catalog_path.read_text(encoding="utf-8"))["products"]
    results = {}
    for product in products:
        if product["review_status"] not in {"source_observed", "approved"}:
            continue
        brand_dir = product["brand"].lower().replace(" ", "-")
        capture = artifacts_dir / brand_dir / f"{product['id']}.md"
        if not capture.is_file():
            continue
        raw = capture.read_bytes()
        if ingredients := extract_ingredients(raw.decode("utf-8")):
            results[product["id"]] = {
                "source_url": product["source_url"],
                "capture_file": capture.name,
                "capture_sha256": hashlib.sha256(raw).hexdigest(),
                "ingredients": ingredients,
            }

    # A run without captures must not overwrite an existing seed.
    if not results:
        raise SystemExit("No explicit ingredient disclosures found in the product captures.")
    stream = NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=output_path.parent, delete=False)
    staged = Path(stream.name)
    try:
        with stream:
            json.dump(results, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
        staged.replace(output_path)
    finally:
        staged.unlink(missing_ok=True)
    return len(results)


if __name__ == "__main__":
    count = process_all_artifacts(
        ROOT / "data/artifacts",
        ROOT / "data/seeds/catalog.json",
        ROOT / "data/seeds/product_ingredients.json",
    )
    print(f"Extracted ingredient disclosures for {count} product listings.")
