"""Index observed manufacturer listing facts for local hybrid retrieval.

Only catalog fields with a source URL enter answer retrieval. Crawl4AI Markdown
is retained as a review artifact and is not promoted to verified health facts.
"""

import hashlib
import json
import os
import uuid
from pathlib import Path

import psycopg
from fastembed import TextEmbedding


ROOT = Path(__file__).resolve().parents[2]
MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit("Set DATABASE_URL before indexing.")
    products = json.loads((ROOT / "data/seeds/catalog.json").read_text(encoding="utf-8"))["products"]
    model = TextEmbedding(model_name=MODEL)
    passages = []
    for item in products:
        parts = [f"Product: {item['name']}", f"Brand: {item['brand']}"]
        for label, key in (("Category", "category"), ("Description from official listing", "description"), ("SKU", "sku")):
            if item.get(key):
                parts.append(f"{label}: {item[key]}")
        if item.get("price") is not None:
            parts.append(f"Displayed price at capture: {item['currency']} {item['price']}")
        parts.append("Ingredients, warnings and age guidance are unknown unless separately reviewed.")
        passages.append("\n".join(parts))
    embeddings = model.embed(passages, batch_size=32)
    with psycopg.connect(database_url) as connection:
        for item, passage, embedding in zip(products, passages, embeddings):
            digest = hashlib.sha256(passage.encode("utf-8")).hexdigest()
            doc_id = uuid.uuid5(uuid.NAMESPACE_URL, item["source_url"])
            passage_id = uuid.uuid5(doc_id, digest)
            connection.execute("""INSERT INTO source_documents
                (id,source_url,title,publisher,jurisdiction,source_kind,rights_status,
                 captured_at,content_sha256,review_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET captured_at=EXCLUDED.captured_at,
                    content_sha256=EXCLUDED.content_sha256,
                    review_status=EXCLUDED.review_status""",
                (doc_id, item["source_url"], item["name"], item["brand"], item["region"],
                 "official_product_listing", "public_with_user_reported_permission",
                 item["captured_at"], digest, item["review_status"]),
            )
            vector = "[" + ",".join(str(float(value)) for value in embedding) + "]"
            connection.execute("""INSERT INTO source_passages
                (id,document_id,passage,passage_index,embedding) VALUES (%s,%s,%s,0,%s)
                ON CONFLICT (document_id,passage_index) DO UPDATE SET
                    id=EXCLUDED.id, passage=EXCLUDED.passage, embedding=EXCLUDED.embedding""",
                (passage_id, doc_id, passage, vector),
            )
    print(f"Indexed {len(passages)} source passages with {MODEL} embeddings.")


if __name__ == "__main__":
    main()
