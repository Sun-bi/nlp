"""Embedding models used by the local vector database."""

from __future__ import annotations

import hashlib
import math
from typing import List, Sequence

from .text import tokenize


class HashingEmbeddingModel:
    """A deterministic local embedding model for reproducible coursework runs.

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
