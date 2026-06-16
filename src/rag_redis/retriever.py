"""Hybrid retrieval: vector search plus BM25 keyword matching."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, replace
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
    rerank_score: float = 0.0
    term_coverage: float = 0.0
    title_coverage: float = 0.0

    @property
    def final_score(self) -> float:
        return self.rerank_score if self.rerank_score > 0 else self.combined_score


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
        enable_rerank: bool = True,
    ) -> None:
        self.chunks = list(chunks)
        self.embedder = embedder
        self.vector_store = vector_store
        self.bm25 = BM25Index(self.chunks)
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.enable_query_rewrite = enable_query_rewrite
        self.enable_rerank = enable_rerank

    @classmethod
    def from_chunks(
        cls,
        chunks: Sequence[Chunk],
        embedder: HashingEmbeddingModel | None = None,
        vector_weight: float = 0.45,
        bm25_weight: float = 0.55,
        enable_query_rewrite: bool = True,
        enable_rerank: bool = True,
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
            enable_rerank=enable_rerank,
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
        if not self.enable_rerank:
            return results[:top_k]
        return self._rerank(results, tokenize(rewritten), top_k=top_k)

    def _rerank(
        self,
        results: Sequence[RetrievalResult],
        query_tokens: Sequence[str],
        top_k: int,
    ) -> List[RetrievalResult]:
        query_set = set(query_tokens)
        if not query_set:
            return list(results[:top_k])

        pool_size = max(top_k * 3, top_k)
        candidate_pool = results[:pool_size]
        reranked: List[RetrievalResult] = []
        for result in candidate_pool:
            chunk_tokens = set(result.chunk.tokens)
            title_tokens = set(tokenize(result.chunk.source_title))
            term_coverage = len(query_set.intersection(chunk_tokens)) / len(query_set)
            title_coverage = len(query_set.intersection(title_tokens)) / len(query_set)
            rerank_score = result.combined_score + 0.20 * term_coverage + 0.08 * title_coverage
            reranked.append(
                replace(
                    result,
                    rerank_score=rerank_score,
                    term_coverage=term_coverage,
                    title_coverage=title_coverage,
                )
            )

        reranked.sort(
            key=lambda result: (result.rerank_score, result.combined_score),
            reverse=True,
        )
        return reranked[:top_k]
