"""Build the concern retrieval index from source-checked guidance summaries."""

from pathlib import Path
import json
import os
import sys

from dotenv import load_dotenv
import psycopg


ROOT = Path(__file__).resolve().parents[2]


def main():
    load_dotenv(ROOT / ".env")
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("Set DATABASE_URL before indexing guidance.")

    sys.path.insert(0, str(ROOT / "apps/api"))
    from app.embeddings import embedding_model, vector_literal

    guides = json.loads((ROOT / "data/seeds/concerns.json").read_text(encoding="utf-8"))
    profiles = {
        guide["id"]: ". ".join([guide["title"], *guide["search_examples"], " ".join(guide["aliases"])])
        for guide in guides
    }
    passages = [
        (guide["id"], card["id"], position, f"{card['title']}. {card['text']}",
         guide["sources"][card["source"]]["url"], guide["reviewed_on"])
        for guide in guides for position, card in enumerate(guide["guidance"])
    ]
    with psycopg.connect(url, connect_timeout=5) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT pg_advisory_xact_lock(542013)")
        cursor.execute((ROOT / "infra/schema.sql").read_text(encoding="utf-8"))
        if dict(cursor.execute("SELECT topic, profile FROM concern_topics").fetchall()) != profiles:
            vectors = embedding_model().embed(list(profiles.values()), batch_size=4)
            cursor.execute("DELETE FROM concern_topics")
            cursor.executemany(
                "INSERT INTO concern_topics (topic, profile, embedding) VALUES (%s, %s, %s)",
                [(topic, profile, vector_literal(vector)) for (topic, profile), vector in zip(profiles.items(), vectors, strict=True)],
            )
        saved = cursor.execute("""
            SELECT topic, passage_key, position, passage, source_url, reviewed_on::text FROM concern_passages
        """).fetchall()
        if set(saved) != set(passages):
            cursor.execute("DELETE FROM concern_passages")
            cursor.executemany("""
                INSERT INTO concern_passages (topic, passage_key, position, passage, source_url, reviewed_on)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, passages)
    print(f"Verified the index of {len(profiles)} concern guides and {len(passages)} source passages.")


if __name__ == "__main__":
    main()
