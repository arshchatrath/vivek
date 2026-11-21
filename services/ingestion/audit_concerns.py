"""Scan catalog text for stated-use candidates for a human review queue."""

from collections import Counter
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
USES = {
    "scalp flaking": r"dandruff|scalp flakes?|flaky scalp|scalp itch",
    "hair shedding or thinning": r"hair fall|hair loss|hair thinning|receding hairline|hair regrowth",
    "dry or damaged hair": r"dry hair|frizz|hair damage|damaged hair|split ends?|hair breakage",
    "beard care": r"beard|moustache|mustache",
    "head lice": r"head lice|nit comb|anti[ -]lice",
    "acne or clogged pores": r"acne|pimples?|breakouts?|comedones?|blackheads?|whiteheads?|clogged pores",
    "dry skin": r"dry skin|skin dryness|flaky skin|dry patches|dehydrated skin",
    "rough bumps": r"keratosis pilaris|strawberry (?:legs|skin)|rough bumps|bumpy skin|skin texture",
    "sun protection": r"sunscreen|sun protection|sunburn|spf ?[0-9]+|broad[ -]spectrum",
    "dark spots or uneven tone": r"pigmentation|dark spots?|dark patches|uneven (?:skin )?tone|hyperpigmentation",
    "underarm care and body odor": r"underarm|body odou?r|antiperspirant|deodorant",
    "ingrown hair and shaving": r"ingrown hairs?|razor bumps?|shav(?:e|ing)|face razor",
    "fine lines or wrinkles": r"fine lines|wrinkles|anti[ -]ag(?:e|i)ing|signs of ag(?:e|i)ing",
    "skin barrier care": r"skin barrier|barrier repair|ceramides?",
    "eczema or irritated skin": r"eczema|skin irritation|irritated skin|itchy skin|sensitive skin",
    "scarring or marks": r"stretch marks?|acne scars?|scar(?:ring)?|acne marks?",
    "oral care and cavity prevention": r"toothpaste|tooth decay|cavit(?:y|ies)|oral hygiene|fluoride(?:[ -]free)?",
    "sleep": r"sleep|insomnia|fall asleep|restless nights?",
    "stress or relaxation": r"stress|relaxation|calming|anxiety",
    "digestion and gut health": r"gut health|digestion|digestive|bloating|constipation|acidity|probiotic",
    "dietary protein": r"protein(?:mix)?|protein intake",
    "vitamin or mineral intake": r"multivitamin|vitamin [abcdke]|iron|magnesium|calcium|mineral",
    "nutritional support": r"nutrition(?:al)?|dietary|nutrimix|milkmix|balanced diet|picky eaters?",
    "energy or fatigue": r"fatigue|tiredness|energy levels?|low energy|stamina",
    "immune support": r"immunity|immune support|immune system",
    "bone or joint health": r"bone health|strong bones|joint pain|joint support|joint mobility",
    "child growth or development": r"height growth|healthy growth|brain development|growth and development|height gain",
    "sexual wellness": r"sexual wellness|erectile|erection|libido|premature ejaculation|sexual health",
    "menstrual or hormonal concerns": r"period pain|menstrual|pcos|hormonal balance|pms",
    "exercise recovery": r"muscle recovery|post[ -]workout|exercise recovery|muscle cramps?",
    "weight or appetite": r"weight (?:loss|gain|management)|appetite|satiety",
    "sweat, chafing or intimate hygiene": r"intimate wash|intimate hygiene|chafing|sweat|jock itch",
}
PATTERNS = {label: re.compile(rf"\b(?:{pattern})\b", re.I) for label, pattern in USES.items()}
PRODUCT_HEADING = re.compile(r"^#\s+[^\n]+", re.MULTILINE)
DETAILS_END = re.compile(r"^(?:Add to Cart|Buy Now|#{1,4}\s+(?:Shop|Related|Frequently Asked))\b", re.I | re.MULTILINE)
MARKDOWN_LINK = re.compile(r"!?\[([^\]]*)\]\([^\n)]*\)")


def captured_details(product: dict) -> str:
    slug = product["brand"].lower().replace(" ", "-")
    path = ROOT / "data/artifacts" / slug / f"{product['id']}.md"
    if not path.is_file():
        return ""
    page = path.read_text(encoding="utf-8")
    heading = PRODUCT_HEADING.search(page)
    if not heading:
        return ""
    # Prefer the main product copy and skip site navigation, FAQs, and other products.
    main_copy = DETAILS_END.split(page[heading.start():heading.start() + 6000], maxsplit=1)[0]
    return MARKDOWN_LINK.sub(r"\1", main_copy)


def main():
    seed = ROOT / "data/seeds"
    catalog = json.loads((seed / "catalog.json").read_text(encoding="utf-8"))
    guides = json.loads((seed / "concerns.json").read_text(encoding="utf-8"))
    reviewed_urls = {
        candidate["url"] for guide in guides for ingredient in guide["ingredients"]
        for candidate in ingredient["matches"]
    }
    rows = []
    counts = Counter()
    details_scanned = 0
    for product in catalog["products"]:
        matches = []
        details = captured_details(product)
        details_scanned += bool(details)
        fields = {field: product.get(field) or "" for field in ("name", "description", "category")}
        fields["captured_details"] = details
        for field, value in fields.items():
            for label, pattern in PATTERNS.items():
                if match := pattern.search(value):
                    matches.append({"topic": label, "field": field, "term": match.group()})
        counts.update({match["topic"] for match in matches})
        rows.append({
            "id": product["id"], "brand": product["brand"], "name": product["name"],
            "source_url": product["source_url"], "captured_at": product["captured_at"],
            "mentions": matches, "reviewed_example": product["source_url"] in reviewed_urls,
        })

    result = {
        "basis": "Keyword mentions in manufacturer listing text. Candidates for review, not evidence of efficacy or suitability.",
        "catalog_snapshot": catalog.get("generated_at"),
        "listings_scanned": len(rows), "listings_with_mentions": sum(bool(row["mentions"]) for row in rows),
        "captured_details_scanned": details_scanned,
        "topic_counts": dict(counts.most_common()), "products": rows,
    }
    output = ROOT / "data/artifacts/catalog-concern-audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Scanned {len(rows)} listings, including {details_scanned} primary page captures. "
          f"Found candidate mentions in {result['listings_with_mentions']} across {len(counts)} topic groups.")


if __name__ == "__main__":
    main()
