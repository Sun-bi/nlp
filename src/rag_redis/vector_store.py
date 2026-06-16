"""A small persistent vector database for chunk embeddings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from .chunking import Chunk
from .embeddings import EmbeddingModel


@dataclass(frozen=True)
class VectorRecord:
    chunk: Chunk
    vector: List[float]


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if not left or not right:
        return 0.0
    return sum(a * b for a, b in zip(left, right))


class LocalVectorStore:
    """JSONL-backed vector store used as the assignment's vector database."""

    def __init__(self, records: Iterable[VectorRecord]) -> None:
        self.records = list(records)

    @classmethod
    def from_chunks(
        cls, chunks: Sequence[Chunk], embedder: EmbeddingModel
    ) -> "LocalVectorStore":
        vectors = embedder.embed([chunk.text for chunk in chunks])
        return cls(VectorRecord(chunk=chunk, vector=vector) for chunk, vector in zip(chunks, vectors))

    def search(self, query_vector: Sequence[float], top_k: int = 5) -> List[Tuple[Chunk, float]]:
        scored = [
            (record.chunk, cosine_similarity(query_vector, record.vector))
            for record in self.records
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]

    def save(self, path: str | Path) -> None:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as handle:
            for record in self.records:
                payload = {
                    "chunk": {
                        "chunk_id": record.chunk.chunk_id,
                        "doc_id": record.chunk.doc_id,
                        "source_title": record.chunk.source_title,
                        "url": record.chunk.url,
                        "text": record.chunk.text,
                        "tokens": record.chunk.tokens,
                        "start_token": record.chunk.start_token,
                        "end_token": record.chunk.end_token,
                    },
                    "vector": record.vector,
                }
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    @classmethod
    def load(cls, path: str | Path) -> "LocalVectorStore":
        records: List[VectorRecord] = []
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                chunk_item = item["chunk"]
                chunk = Chunk(
                    chunk_id=chunk_item["chunk_id"],
                    doc_id=chunk_item["doc_id"],
                    source_title=chunk_item["source_title"],
                    url=chunk_item.get("url", ""),
                    text=chunk_item["text"],
                    tokens=list(chunk_item["tokens"]),
                    start_token=int(chunk_item["start_token"]),
                    end_token=int(chunk_item["end_token"]),
                )
                records.append(VectorRecord(chunk=chunk, vector=list(item["vector"])))
        return cls(records)


class FaissVectorStore(LocalVectorStore):
    """Optional FAISS-backed vector store with JSONL metadata fallback."""

    def __init__(self, records: Iterable[VectorRecord], index) -> None:
        super().__init__(records)
        self.index = index

    @classmethod
    def from_chunks(
        cls, chunks: Sequence[Chunk], embedder: EmbeddingModel
    ) -> "FaissVectorStore":
        try:
            import faiss
            import numpy as np
        except ImportError as exc:
            raise RuntimeError(
                "faiss-cpu is required for vector_store='faiss'. "
                "Install optional dependencies or use vector_store='local'."
            ) from exc
        vectors = embedder.embed([chunk.text for chunk in chunks])
        array = np.asarray(vectors, dtype="float32")
        index = faiss.IndexFlatIP(array.shape[1])
        index.add(array)
        records = [
            VectorRecord(chunk=chunk, vector=vector)
            for chunk, vector in zip(chunks, vectors)
        ]
        return cls(records, index)

    def search(self, query_vector: Sequence[float], top_k: int = 5) -> List[Tuple[Chunk, float]]:
        try:
            import numpy as np
        except ImportError:
            return super().search(query_vector, top_k=top_k)
        query = np.asarray([query_vector], dtype="float32")
        scores, indices = self.index.search(query, min(top_k, len(self.records)))
        return [
            (self.records[int(index)].chunk, float(score))
            for score, index in zip(scores[0], indices[0])
            if index >= 0
        ]


class ChromaVectorStore(LocalVectorStore):
    """Optional in-memory Chroma adapter used for local experimentation."""

    def __init__(self, records: Iterable[VectorRecord], collection) -> None:
        super().__init__(records)
        self.collection = collection

    @classmethod
    def from_chunks(
        cls, chunks: Sequence[Chunk], embedder: EmbeddingModel
    ) -> "ChromaVectorStore":
        try:
            import chromadb  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "chromadb is required for vector_store='chroma'. "
                "Install optional dependencies or use vector_store='local'."
            ) from exc
        vectors = embedder.embed([chunk.text for chunk in chunks])
        records = [
            VectorRecord(chunk=chunk, vector=vector)
            for chunk, vector in zip(chunks, vectors)
        ]
        client_factory = getattr(chromadb, "EphemeralClient", chromadb.Client)
        client = client_factory()
        collection = client.create_collection(
            name="redis_rag_chunks",
            metadata={"hnsw:space": "cosine"},
        )
        collection.add(
            ids=[record.chunk.chunk_id for record in records],
            embeddings=[record.vector for record in records],
            documents=[record.chunk.text for record in records],
            metadatas=[
                {
                    "doc_id": record.chunk.doc_id,
                    "source_title": record.chunk.source_title,
                    "url": record.chunk.url,
                }
                for record in records
            ],
        )
        return cls(records, collection)

    def search(self, query_vector: Sequence[float], top_k: int = 5) -> List[Tuple[Chunk, float]]:
        results = self.collection.query(
            query_embeddings=[list(query_vector)],
            n_results=min(top_k, len(self.records)),
        )
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        by_id = {record.chunk.chunk_id: record.chunk for record in self.records}
        scored: List[Tuple[Chunk, float]] = []
        for chunk_id, distance in zip(ids, distances):
            chunk = by_id.get(chunk_id)
            if chunk is None:
                continue
            score = 1.0 - float(distance)
            scored.append((chunk, score))
        return scored


def create_vector_store(
    chunks: Sequence[Chunk],
    embedder: EmbeddingModel,
    vector_store: str = "local",
) -> LocalVectorStore:
    normalized = vector_store.strip().lower()
    if normalized == "local":
        return LocalVectorStore.from_chunks(chunks, embedder)
    if normalized == "faiss":
        return FaissVectorStore.from_chunks(chunks, embedder)
    if normalized == "chroma":
        return ChromaVectorStore.from_chunks(chunks, embedder)
    raise ValueError(f"Unknown vector store: {vector_store}")
