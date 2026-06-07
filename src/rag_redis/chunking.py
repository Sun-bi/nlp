"""Chunk Redis documents into overlapping retrieval units."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List

from .corpus import Document
from .text import tokenize


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    doc_id: str
    source_title: str
    url: str
    text: str
    tokens: List[str]
    start_token: int
    end_token: int


def chunk_document(document: Document, chunk_size: int = 180, overlap: int = 35) -> List[Chunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    source_tokens = tokenize(f"{document.title} {document.text}")
    if not source_tokens:
        return []

    chunks: List[Chunk] = []
    start = 0
    index = 0
    step = chunk_size - overlap
    while start < len(source_tokens):
        end = min(start + chunk_size, len(source_tokens))
        window = source_tokens[start:end]
        chunk_text = document.text if start == 0 and end == len(source_tokens) else " ".join(window)
        chunks.append(
            Chunk(
                chunk_id=f"{document.doc_id}#{index}",
                doc_id=document.doc_id,
                source_title=document.title,
                url=document.url,
                text=chunk_text,
                tokens=window,
                start_token=start,
                end_token=end,
            )
        )
        if end == len(source_tokens):
            break
        start += step
        index += 1
    return chunks


def chunk_documents(
    documents: Iterable[Document], chunk_size: int = 180, overlap: int = 35
) -> List[Chunk]:
    chunks: List[Chunk] = []
    for document in documents:
        chunks.extend(chunk_document(document, chunk_size=chunk_size, overlap=overlap))
    return chunks


def save_chunks(chunks: Iterable[Chunk], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")


def load_chunks(path: str | Path) -> List[Chunk]:
    chunks: List[Chunk] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            chunks.append(
                Chunk(
                    chunk_id=item["chunk_id"],
                    doc_id=item["doc_id"],
                    source_title=item["source_title"],
                    url=item.get("url", ""),
                    text=item["text"],
                    tokens=list(item["tokens"]),
                    start_token=int(item["start_token"]),
                    end_token=int(item["end_token"]),
                )
            )
    return chunks
