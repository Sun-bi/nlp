"""Hybrid retrieval: vector search plus BM25 keyword matching."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

from .chunking import Chunk
from .embeddings import HashingEmbeddingModel
from .query import rewrite_query
from .text import tokenize
from .vector_store import LocalVectorStore


@dataclass(frozen=True)
class RetrievalResult:
    chunk: Chunk
    vector_score: float
    bm25_score: float
    combined_score: float


class BM25Index:
    def __init__(self, chunks: Sequence[Chunk], k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = list(chunks)
        self.k1 = k1
        self.b = b
        self.doc_freq: Dict[str, int] = {}
        self.term_freqs: List[Counter[str]] = []
        self.lengths: List[int] = []

        for chunk in self.chunks:
            counter = Counter(chunk.tokens)
            self.term_freqs.append(counter)
            self.lengths.append(len(chunk.tokens))
            for token in counter:
                self.doc_freq[token] = self.doc_freq.get(token, 0) + 1

        self.avgdl = sum(self.lengths) / len(self.lengths) if self.lengths else 0.0

    def score(self, query_tokens: Iterable[str]) -> List[float]:
        query = list(query_tokens)
        total_docs = len(self.chunks)
        scores = [0.0 for _ in self.chunks]
        if total_docs == 0 or self.avgdl == 0:
            return scores

        for token in query:
            df = self.doc_freq.get(token, 0)
            if df == 0:
                continue
            idf = math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
            for index, counter in enumerate(self.term_freqs):
                freq = counter.get(token, 0)
                if freq == 0:
                    continue
                length = self.lengths[index]
                denominator = freq + self.k1 * (1 - self.b + self.b * length / self.avgdl)
                scores[index] += idf * (freq * (self.k1 + 1)) / denominator
        return scores


def _normalize_scores(scores: Sequence[float]) -> List[float]:
    if not scores:
        return []
    max_score = max(scores)
    min_score = min(scores)
    if max_score == min_score:
        return [1.0 if max_score > 0 else 0.0 for _ in scores]
    return [(score - min_score) / (max_score - min_score) for score in scores]


class HybridRetriever:
    """Combine local vector search with BM25 for Redis command-sensitive RAG."""

    def __init__(
        self,
        chunks: Sequence[Chunk],
        embedder: HashingEmbeddingModel,
        vector_store: LocalVectorStore,
        vector_weight: float = 0.45,
        bm25_weight: float = 0.55,
        enable_query_rewrite: bool = True,
    ) -> None:
        self.chunks = list(chunks)
        self.embedder = embedder
        self.vector_store = vector_store
        self.bm25 = BM25Index(self.chunks)
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.enable_query_rewrite = enable_query_rewrite

    @classmethod
    def from_chunks(
        cls,
        chunks: Sequence[Chunk],
        embedder: HashingEmbeddingModel | None = None,
        vector_weight: float = 0.45,
        bm25_weight: float = 0.55,
        enable_query_rewrite: bool = True,
    ) -> "HybridRetriever":
        actual_embedder = embedder or HashingEmbeddingModel()
        vector_store = LocalVectorStore.from_chunks(chunks, actual_embedder)
        return cls(
            chunks=chunks,
            embedder=actual_embedder,
            vector_store=vector_store,
            vector_weight=vector_weight,
            bm25_weight=bm25_weight,
            enable_query_rewrite=enable_query_rewrite,
        )

    def search(self, question: str, top_k: int = 5) -> List[RetrievalResult]:
        rewritten = rewrite_query(question) if self.enable_query_rewrite else question
        query_vector = self.embedder.embed_one(rewritten)

        vector_pairs = self.vector_store.search(query_vector, top_k=len(self.chunks))
        vector_by_id = {chunk.chunk_id: score for chunk, score in vector_pairs}
        vector_scores = [vector_by_id.get(chunk.chunk_id, 0.0) for chunk in self.chunks]
        bm25_scores = self.bm25.score(tokenize(rewritten))

        normalized_vector = _normalize_scores(vector_scores)
        normalized_bm25 = _normalize_scores(bm25_scores)

        results: List[RetrievalResult] = []
        for index, chunk in enumerate(self.chunks):
            combined = (
                self.vector_weight * normalized_vector[index]
                + self.bm25_weight * normalized_bm25[index]
            )
            results.append(
                RetrievalResult(
                    chunk=chunk,
                    vector_score=vector_scores[index],
                    bm25_score=bm25_scores[index],
                    combined_score=combined,
                )
            )
        results.sort(key=lambda result: result.combined_score, reverse=True)
        return results[:top_k]
