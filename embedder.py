"""Turns text into embeddings (a list of 384 numbers that capture the *meaning* of the text)."""
import numpy as np
from fastembed import TextEmbedding

MODEL_NAME = "BAAI/bge-small-en-v1.5"   # small, free, runs on your laptop
DIM = 384

_model = None


def _get_model():
    global _model
    if _model is None:
        _model = TextEmbedding(MODEL_NAME)   # downloads once, then cached
    return _model


def _normalize(v):
    v = np.asarray(v, dtype="float32")
    return v / (np.linalg.norm(v) + 1e-12)


def embed_texts(texts):
    """Embed a list of document chunks."""
    return [_normalize(v) for v in _get_model().embed(texts)]


def embed_query(query):
    """Embed a search question. This model likes a special prefix for questions."""
    prefix = "Represent this sentence for searching relevant passages: "
    return _normalize(next(iter(_get_model().embed([prefix + query]))))


def to_db_format(vec):
    """SingleStore accepts vectors as text like '[0.1, 0.2, ...]'."""
    return "[" + ",".join(f"{x:.6f}" for x in vec) + "]"
