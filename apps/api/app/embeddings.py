"""Shared local embeddings for the two PostgreSQL indexes."""

from functools import lru_cache
from threading import Lock


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model_lock = Lock()


@lru_cache(maxsize=1)
def embedding_model():
    from fastembed import TextEmbedding

    return TextEmbedding(model_name=MODEL_NAME, threads=1)


def vector_literal(vector) -> str:
    return "[" + ",".join(str(float(value)) for value in vector) + "]"


def question_embedding(question: str) -> str:
    with _model_lock:
        return vector_literal(next(embedding_model().query_embed(question)))
