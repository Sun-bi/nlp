"""Embedding models used by the local vector database."""

from __future__ import annotations

import hashlib
import math
from typing import List, Protocol, Sequence

from .text import tokenize


class EmbeddingModel(Protocol):
    dimensions: int

    def embed_one(self, text: str) -> List[float]:
        ...

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        ...


class HashingEmbeddingModel:
    """A deterministic local embedding model for reproducible runs.

    It maps Redis-aware tokens into a fixed dimensional vector using signed
    hashing. The README documents how to swap this for BGE/SentenceTransformer
    embeddings when a GPU or model cache is available.
    """

    def __init__(self, dimensions: int = 256) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self.dimensions = dimensions

    def embed_one(self, text: str) -> List[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        return [self.embed_one(text) for text in texts]


class SentenceTransformerEmbeddingModel:
    """Optional BGE/SentenceTransformer embedding adapter.

    The default local path intentionally does not require this dependency.
    Install `sentence-transformers` and pass a BGE model name to enable it.
    """

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5") -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is required for BGE embeddings. "
                "Install optional dependencies or use embedding_model='hashing'."
            ) from exc
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimensions = int(self.model.get_sentence_embedding_dimension())

    def embed_one(self, text: str) -> List[float]:
        return self.embed([text])[0]

    def embed(self, texts: Sequence[str]) -> List[List[float]]:
        vectors = self.model.encode(
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [list(map(float, vector)) for vector in vectors]


def create_embedding_model(
    embedding_model: str = "hashing",
    dimensions: int = 256,
) -> EmbeddingModel:
    normalized = embedding_model.strip().lower()
    if normalized in {"hashing", "local", "deterministic"}:
        return HashingEmbeddingModel(dimensions=dimensions)
    aliases = {
        "bge": "BAAI/bge-small-zh-v1.5",
        "bge-small-zh": "BAAI/bge-small-zh-v1.5",
        "bge-base-zh": "BAAI/bge-base-zh-v1.5",
    }
    return SentenceTransformerEmbeddingModel(aliases.get(normalized, embedding_model))
