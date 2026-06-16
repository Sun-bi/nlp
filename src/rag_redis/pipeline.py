"""High-level RAG pipeline assembly."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .chunking import Chunk, chunk_documents, load_chunks, save_chunks
from .corpus import load_jsonl_documents
from .embeddings import create_embedding_model
from .generator import GeneratedAnswer, OpenAICompatibleGenerator
from .retriever import HybridRetriever, RetrievalResult
from .vector_store import LocalVectorStore, create_vector_store


@dataclass
class RagPipeline:
    retriever: HybridRetriever
    generator: OpenAICompatibleGenerator

    def ask(self, question: str, top_k: int = 5) -> tuple[GeneratedAnswer, List[RetrievalResult]]:
        contexts = self.retriever.search(question, top_k=top_k)
        answer = self.generator.generate(question, contexts)
        return answer, contexts


def build_index(
    corpus_path: str | Path,
    index_dir: str | Path,
    chunk_size: int = 320,
    overlap: int = 40,
    dimensions: int = 256,
    embedding_model: str = "hashing",
    vector_store: str = "local",
) -> List[Chunk]:
    documents = load_jsonl_documents(corpus_path)
    chunks = chunk_documents(documents, chunk_size=chunk_size, overlap=overlap)
    directory = Path(index_dir)
    directory.mkdir(parents=True, exist_ok=True)
    save_chunks(chunks, directory / "chunks.jsonl")
    embedder = create_embedding_model(embedding_model, dimensions=dimensions)
    store = create_vector_store(chunks, embedder, vector_store=vector_store)
    store.save(directory / "vectors.jsonl")
    return chunks


def load_pipeline(
    corpus_path: str | Path,
    index_dir: str | Path,
    rebuild: bool = False,
    dimensions: int = 256,
    embedding_model: str = "hashing",
    vector_store: str = "local",
    retrieval_mode: str = "hybrid",
    reranker: str = "lightweight",
) -> RagPipeline:
    directory = Path(index_dir)
    chunks_path = directory / "chunks.jsonl"
    vectors_path = directory / "vectors.jsonl"
    if rebuild or not chunks_path.exists() or not vectors_path.exists():
        chunks = build_index(
            corpus_path,
            directory,
            dimensions=dimensions,
            embedding_model=embedding_model,
            vector_store=vector_store,
        )
        embedder = create_embedding_model(embedding_model, dimensions=dimensions)
        store = create_vector_store(chunks, embedder, vector_store=vector_store)
    else:
        chunks = load_chunks(chunks_path)
        store = LocalVectorStore.load(vectors_path)

    embedder = create_embedding_model(embedding_model, dimensions=dimensions)
    vector_weight, bm25_weight, enable_rerank = _retrieval_settings(retrieval_mode, reranker)
    retriever = HybridRetriever(
        chunks=chunks,
        embedder=embedder,
        vector_store=store,
        vector_weight=vector_weight,
        bm25_weight=bm25_weight,
        enable_query_rewrite=True,
        enable_rerank=enable_rerank,
        reranker=reranker,
    )
    return RagPipeline(retriever=retriever, generator=OpenAICompatibleGenerator())


def _retrieval_settings(retrieval_mode: str, reranker: str) -> tuple[float, float, bool]:
    mode = retrieval_mode.strip().lower()
    if mode in {"vector", "pure_vector"}:
        return 1.0, 0.0, False
    if mode in {"bm25", "keyword"}:
        return 0.0, 1.0, False
    if mode in {"hybrid_no_rerank", "hybrid-baseline"}:
        return 0.45, 0.55, False
    if mode in {"hybrid", "hybrid_rerank"}:
        return 0.45, 0.55, reranker.strip().lower() != "none"
    raise ValueError(f"Unknown retrieval mode: {retrieval_mode}")
