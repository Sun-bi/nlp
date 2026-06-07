"""A small persistent vector database for chunk embeddings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

from .chunking import Chunk
from .embeddings import HashingEmbeddingModel


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
        cls, chunks: Sequence[Chunk], embedder: HashingEmbeddingModel
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
