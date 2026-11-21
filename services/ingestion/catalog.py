"""Official Mosaic catalog discovery and deterministic extraction.

Run from the repository root: python services/ingestion/catalog.py --limit 10
The committed seed contains sourced listing facts; local per-page artifacts are ignored by Git.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "seeds" / "catalog.json"
ARTIFACTS = ROOT / "data" / "artifacts"
AGENT = "VivekCatalog/0.1 (Fellowship research; public product pages)"
BRANDS = {
    "Man Matters": "https://manmatters.com",
    "Be Bodywise": "https://bebodywise.com",
    "Little Joys": "https://ourlittlejoys.com",
    "Root Labs": "https://rootlabshealth.com",
}


def fetch(session: requests.Session, url: str) -> requests.Response:
    response = session.get(url, timeout=30, allow_redirects=True)
    response.raise_for_status()
    return response


def sitemap_urls(session: requests.Session, base: str) -> list[str]:
    """Read only official product sitemaps, keeping page order stable."""
    root = ET.fromstring(fetch(session, f"{base}/sitemap.xml").content)
    children = [item.text for item in root.iter() if item.tag.endswith("loc") and item.text]
    product_maps = [url for url in children if "sitemap" in url and "product" in url]
    found: list[str] = []
    for sitemap in product_maps:
        product_root = ET.fromstring(fetch(session, sitemap).content)
        if product_root.tag.endswith("urlset"):
            for entry in product_root:
                if not entry.tag.endswith("url"):
                    continue
                location = next((node.text for node in entry if node.tag.endswith("loc")), None)
                if location and urlparse(location).netloc == urlparse(base).netloc:
                    if "/product/" in location or "/products/" in location or "/dp/" in location:
                        found.append(location.split("?")[0])
    return list(dict.fromkeys(found))


def robots_for(session: requests.Session, base: str) -> RobotFileParser:
    robots_url = f"{base}/robots.txt"
    response = fetch(session, robots_url)
    parser = RobotFileParser()
    parser.parse(response.text.splitlines())
    return parser


def product_jsonld(soup: BeautifulSoup) -> dict | None:
    def visit(value):
        if isinstance(value, list):
            for item in value:
                result = visit(item)
                if result:
                    return result
        if isinstance(value, dict):
            types = value.get("@type", [])
            if isinstance(types, str):
                types = [types]
            if "Product" in types and value.get("name"):
                return value
            return visit(value.get("@graph", []))
        return None

    for script in soup.select('script[type="application/ld+json"]'):
        try:
            result = visit(json.loads(script.string or script.get_text()))
            if result:
                return result
        except (ValueError, TypeError):
            continue
    return None


def normalize_offer(value) -> dict:
    offers = value if isinstance(value, list) else [value]
    for offer in offers:
        if isinstance(offer, dict) and offer.get("price") is not None:
            return {
                "price": offer.get("price"),
                "currency": offer.get("priceCurrency"),
                "availability": str(offer.get("availability", "")).rsplit("/", 1)[-1] or None,
            }
    return {"price": None, "currency": None, "availability": None}


def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", html.unescape(value)).strip() or None


def extract(url: str, brand: str, response: requests.Response) -> tuple[dict | None, dict]:
    soup = BeautifulSoup(response.text, "html.parser")
    structured = product_jsonld(soup)
    captured_at = datetime.now(timezone.utc).isoformat()
    digest = hashlib.sha256(response.content).hexdigest()
    for element in soup(["script", "style", "noscript", "svg"]):
        element.decompose()
    main = soup.find("main") or soup.body or soup
    page_text = clean_text(main.get_text("\n", strip=True)) or ""
    artifact = {
        "url": response.url,
        "captured_at": captured_at,
        "content_sha256": digest,
        "http_status": response.status_code,
        "page_text": page_text[:120_000],
        "jsonld": structured,
    }
    if not structured:
        return None, artifact
    offer = normalize_offer(structured.get("offers"))
    image = structured.get("image")
    if isinstance(image, list):
        image = image[0] if image else None
    if isinstance(image, dict):
        image = image.get("url") or image.get("contentUrl")
    name = clean_text(structured.get("name"))
    description = clean_text(structured.get("description"))
    fields = {
        "name": name,
        "description": description,
        "sku": clean_text(str(structured.get("sku", ""))),
        "category": clean_text(structured.get("category")),
        "image_url": image if isinstance(image, str) and image.startswith("https://") else None,
        **offer,
    }
    provenance = {
        key: {
            "source_url": response.url,
            "captured_at": captured_at,
            "content_sha256": digest,
            "method": "product_jsonld",
            "status": "source_observed",
        }
        for key, value in fields.items()
        if value is not None
    }
    record = {
        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, response.url.split("?")[0])),
        "brand": brand,
        "region": "US" if brand == "Root Labs" else "IN",
        "source_url": response.url,
        "captured_at": captured_at,
        "content_sha256": digest,
        "review_status": "source_observed",
        **fields,
        "ingredients": None,
        "warnings": None,
        "age_restrictions": None,
        "field_sources": provenance,
    }
    return record, artifact


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Per-brand page limit; 0 means all")
    parser.add_argument("--delay", type=float, default=0.7, help="Seconds between product requests")
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update({"User-Agent": AGENT, "Accept": "text/html,application/xml;q=0.9"})
    previous = {}
    if OUT.exists():
        previous = {item["id"]: item for item in json.loads(OUT.read_text(encoding="utf-8")).get("products", [])}
    products = dict(previous)
    coverage = {}
    for brand, base in BRANDS.items():
        try:
            robots = robots_for(session, base)
            urls = sitemap_urls(session, base)
        except Exception as exc:
            coverage[brand] = {"error": str(exc), "discovered": 0, "fetched": 0}
            continue
        selected = urls[: args.limit or None]
        stats = {"discovered": len(urls), "selected": len(selected), "fetched": 0, "blocked": 0, "unstructured": 0, "errors": []}
        for url in selected:
            if not robots.can_fetch(AGENT, url):
                stats["blocked"] += 1
                continue
            try:
                response = fetch(session, url)
                record, artifact = extract(url, brand, response)
                artifact_path = ARTIFACTS / brand.lower().replace(" ", "-") / f"{uuid.uuid5(uuid.NAMESPACE_URL, url)}.json"
                artifact_path.parent.mkdir(parents=True, exist_ok=True)
                artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
                if record:
                    old = products.get(record["id"])
                    if old and old.get("review_status") == "approved":
                        if old.get("content_sha256") != record["content_sha256"]:
                            changes = ARTIFACTS / "pending-changes.jsonl"
                            with changes.open("a", encoding="utf-8") as stream:
                                stream.write(json.dumps({"product_id": record["id"], "source_url": record["source_url"], "old_hash": old["content_sha256"], "new_hash": record["content_sha256"], "new_record": record}, ensure_ascii=False) + "\n")
                    else:
                        products[record["id"]] = record
                    stats["fetched"] += 1
                else:
                    stats["unstructured"] += 1
            except Exception as exc:
                stats["errors"].append({"url": url, "reason": str(exc)[:200]})
            time.sleep(max(args.delay, 0))
        coverage[brand] = stats
        print(f"{brand}: {stats['fetched']}/{stats['selected']} structured pages; {stats['blocked']} blocked", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "method": "official sitemap + Product JSON-LD", "coverage": coverage, "products": list(products.values())}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(products)} sourced products to {OUT}", flush=True)


if __name__ == "__main__":
    main()

