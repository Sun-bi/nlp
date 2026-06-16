"""Citation validation utilities for generated RAG answers."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Sequence

from .retriever import RetrievalResult
from .text import tokenize


@dataclass(frozen=True)
class CitationCheck:
    has_citation: bool
    valid_indices: bool
    grounded: bool
    cited_indices: list[int]
    missing_indices: list[int]
    supported_indices: list[int]

    @property
    def passed(self) -> bool:
        return self.has_citation and self.valid_indices and self.grounded

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["passed"] = self.passed
        return payload


def check_citations(answer: str, contexts: Sequence[RetrievalResult]) -> CitationCheck:
    cited_indices = sorted({int(match) for match in re.findall(r"\[(\d+)\]", answer)})
    missing_indices = [
        index for index in cited_indices if index < 1 or index > len(contexts)
    ]
    answer_tokens = set(tokenize(re.sub(r"\[\d+\]", "", answer)))
    supported_indices: list[int] = []
    for index in cited_indices:
        if index in missing_indices:
            continue
        context_tokens = set(contexts[index - 1].chunk.tokens)
        if answer_tokens.intersection(context_tokens):
            supported_indices.append(index)
    return CitationCheck(
        has_citation=bool(cited_indices),
        valid_indices=not missing_indices,
        grounded=bool(supported_indices),
        cited_indices=cited_indices,
        missing_indices=missing_indices,
        supported_indices=supported_indices,
    )
