"""Build the concern retrieval index from source-checked guidance summaries."""

from pathlib import Path
import json
import os

from dotenv import load_dotenv
import psycopg


ROOT = Path(__file__).resolve().parents[2]


def main():
    load_dotenv(ROOT / ".env")
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("Set DATABASE_URL before indexing guidance.")
    guides = json.loads((ROOT / "data/seeds/concerns.json").read_text(encoding="utf-8"))
    with psycopg.connect(url, connect_timeout=5) as connection:
        connection.execute((ROOT / "infra/schema.sql").read_text(encoding="utf-8"))
        connection.execute("DELETE FROM concern_passages")
        for guide in guides:
            with connection.cursor() as cursor:
                cursor.executemany("""
                    INSERT INTO concern_passages (topic, passage_key, position, passage, source_url, reviewed_on)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [
                    (guide["id"], card["id"], position, f"{card['title']}. {card['text']}",
                     guide["sources"][card["source"]]["url"], guide["reviewed_on"])
                    for position, card in enumerate(guide["guidance"])
                ])
    print(f"Indexed {len(guides)} concern guides and {sum(len(guide['guidance']) for guide in guides)} source passages.")


if __name__ == "__main__":
    main()
