"""Load source-observed listing facts into PostgreSQL without replacing approved changes."""

import json
import os
from pathlib import Path

import psycopg
from psycopg.types.json import Jsonb


ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("Set DATABASE_URL to a PostgreSQL connection string.")
    seed = json.loads((ROOT / "data/seeds/catalog.json").read_text(encoding="utf-8"))
    with psycopg.connect(url) as connection:
        connection.execute((ROOT / "infra/schema.sql").read_text(encoding="utf-8"))
        for item in seed["products"]:
            previous = connection.execute(
                "SELECT content_sha256,review_status,name,price,description FROM catalog_products WHERE id=%s",
                (item["id"],),
            ).fetchone()
            if previous and previous[0] != item["content_sha256"]:
                changes = {key: {"previous": str(old), "observed": str(item.get(key))}
                           for key, old in (("name", previous[2]), ("price", previous[3]),
                                            ("description", previous[4]))
                           if str(old) != str(item.get(key))}
                connection.execute("""INSERT INTO catalog_change_events
                    (product_id,previous_hash,new_hash,state,diff) VALUES (%s,%s,%s,%s,%s)""",
                    (item["id"], previous[0], item["content_sha256"],
                     "needs_review" if previous[1] == "approved" else "observed", Jsonb(changes)),
                )
            connection.execute(
                """INSERT INTO catalog_products (
                    id,brand,region,name,description,sku,category,image_url,price,currency,
                    availability,ingredients,warnings,age_restrictions,source_url,captured_at,
                    content_sha256,review_status,field_sources
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name, description = EXCLUDED.description,
                    image_url = EXCLUDED.image_url, price = EXCLUDED.price,
                    currency = EXCLUDED.currency, availability = EXCLUDED.availability,
                    captured_at = EXCLUDED.captured_at, content_sha256 = EXCLUDED.content_sha256,
                    field_sources = EXCLUDED.field_sources
                WHERE catalog_products.review_status = 'source_observed'""",
                (
                    item["id"], item["brand"], item["region"], item["name"], item["description"],
                    item["sku"], item["category"], item["image_url"], item["price"], item["currency"],
                    item["availability"], Jsonb(item["ingredients"]), Jsonb(item["warnings"]),
                    item["age_restrictions"], item["source_url"], item["captured_at"],
                    item["content_sha256"], item["review_status"], Jsonb(item["field_sources"]),
                ),
            )
    print(f"Loaded or checked {len(seed['products'])} sourced product records.")


if __name__ == "__main__":
    main()

