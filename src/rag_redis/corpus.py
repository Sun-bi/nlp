"""Corpus data structures and JSONL helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    url: str
    text: str


def load_jsonl_documents(path: str | Path) -> List[Document]:
    documents: List[Document] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            documents.append(
                Document(
                    doc_id=item["doc_id"],
                    title=item["title"],
                    url=item.get("url", ""),
                    text=item["text"],
                )
            )
    return documents


def save_jsonl_documents(documents: Iterable[Document], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for document in documents:
            handle.write(json.dumps(asdict(document), ensure_ascii=False) + "\n")
