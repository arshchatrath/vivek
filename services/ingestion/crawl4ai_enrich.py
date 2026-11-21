"""Capture private, per-page Crawl4AI Markdown for review and later extraction.

Official product URLs and their access checks come from catalog.py. Artifacts are
local and ignored by Git; no page text is published automatically.
"""

import argparse
import asyncio
import json
import os
from pathlib import Path

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig


ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "data/seeds/catalog.json"
ARTIFACTS = ROOT / "data/artifacts"


async def enrich(limit: int, delay: float) -> None:
    products = json.loads(SEED.read_text(encoding="utf-8"))["products"]
    os.environ.setdefault("CRAWL4AI_NO_CLOUD_NOTICE", "1")
    browser = BrowserConfig(headless=True, chrome_channel="msedge" if os.name == "nt" else "chromium", verbose=False)
    config = CrawlerRunConfig(check_robots_txt=True, wait_until="domcontentloaded", page_timeout=30000, verbose=False)
    completed = 0
    errors = []
    async with AsyncWebCrawler(config=browser) as crawler:
        for product in products:
            path = ARTIFACTS / product["brand"].lower().replace(" ", "-") / f"{product['id']}.md"
            if path.exists():
                continue
            if limit and completed >= limit:
                break
            try:
                result = await crawler.arun(product["source_url"], config=config)
                if not result.success or not result.markdown:
                    raise RuntimeError(str(result.error_message or "Empty Markdown")[:200])
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(str(result.markdown), encoding="utf-8")
                completed += 1
                print(f"{completed}: {product['brand']} — {product['name'][:55]}", flush=True)
            except Exception as exc:
                errors.append({"url": product["source_url"], "reason": str(exc)[:200]})
            await asyncio.sleep(max(delay, 0))
    (ARTIFACTS / "crawl4ai-errors.json").write_text(json.dumps(errors, indent=2), encoding="utf-8")
    print(f"Crawl4AI Markdown captured: {completed}; errors: {len(errors)}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10, help="New pages to capture; 0 means all")
    parser.add_argument("--delay", type=float, default=0.7)
    args = parser.parse_args()
    asyncio.run(enrich(args.limit, args.delay))

