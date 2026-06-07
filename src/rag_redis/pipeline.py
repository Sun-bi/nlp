"""High-level RAG pipeline assembly."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .chunking import Chunk, chunk_documents, load_chunks, save_chunks
from .corpus import load_jsonl_documents
from .embeddings import HashingEmbeddingModel
from .generator import GeneratedAnswer, OpenAICompatibleGenerator
from .retriever import HybridRetriever, RetrievalResult
from .vector_store import LocalVectorStore


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
) -> List[Chunk]:
    documents = load_jsonl_documents(corpus_path)
    chunks = chunk_documents(documents, chunk_size=chunk_size, overlap=overlap)
    directory = Path(index_dir)
    directory.mkdir(parents=True, exist_ok=True)
    save_chunks(chunks, directory / "chunks.jsonl")
    vector_store = LocalVectorStore.from_chunks(chunks, HashingEmbeddingModel(dimensions=dimensions))
    vector_store.save(directory / "vectors.jsonl")
    return chunks


def load_pipeline(
    corpus_path: str | Path,
    index_dir: str | Path,
    rebuild: bool = False,
    dimensions: int = 256,
) -> RagPipeline:
    directory = Path(index_dir)
    chunks_path = directory / "chunks.jsonl"
    vectors_path = directory / "vectors.jsonl"
    if rebuild or not chunks_path.exists() or not vectors_path.exists():
        chunks = build_index(corpus_path, directory, dimensions=dimensions)
        vector_store = LocalVectorStore.from_chunks(chunks, HashingEmbeddingModel(dimensions=dimensions))
    else:
        chunks = load_chunks(chunks_path)
        vector_store = LocalVectorStore.load(vectors_path)

    embedder = HashingEmbeddingModel(dimensions=dimensions)
    retriever = HybridRetriever(
        chunks=chunks,
        embedder=embedder,
        vector_store=vector_store,
        vector_weight=0.45,
        bm25_weight=0.55,
        enable_query_rewrite=True,
    )
    return RagPipeline(retriever=retriever, generator=OpenAICompatibleGenerator())
