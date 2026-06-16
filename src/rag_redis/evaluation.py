"""Quantitative RAG evaluation for coursework reporting."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from .retriever import RetrievalResult
from .text import normalize_text, tokenize


def evaluate_single(
    sample: Dict[str, object],
    answer: str,
    contexts: Sequence[RetrievalResult],
) -> Dict[str, float]:
    gold_doc_ids = set(sample.get("gold_doc_ids", []))
    retrieved_doc_ids = {result.chunk.doc_id for result in contexts}
    if gold_doc_ids:
        context_relevance = len(gold_doc_ids.intersection(retrieved_doc_ids)) / len(gold_doc_ids)
    else:
        context_relevance = 0.0

    faithfulness = _faithfulness(answer, " ".join(result.chunk.text for result in contexts))
    expected_keywords = [str(item) for item in sample.get("expected_keywords", [])]
    answer_relevance = _keyword_coverage(answer, expected_keywords)

    return {
        "context_relevance": round(context_relevance, 4),
        "faithfulness": round(faithfulness, 4),
        "answer_relevance": round(answer_relevance, 4),
    }


def load_eval_samples(path: str | Path) -> List[Dict[str, object]]:
    samples: List[Dict[str, object]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                samples.append(json.loads(line))
    return samples


def summarize_metrics(rows: Iterable[Dict[str, float]]) -> Dict[str, float]:
    materialized = list(rows)
    if not materialized:
        return {"context_relevance": 0.0, "faithfulness": 0.0, "answer_relevance": 0.0}
    keys = ["context_relevance", "faithfulness", "answer_relevance"]
    return {
        key: round(sum(row[key] for row in materialized) / len(materialized), 4)
        for key in keys
    }


def save_eval_outputs(
    rows: Sequence[Dict[str, object]],
    metrics: Dict[str, float],
    output_dir: str | Path,
) -> None:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "eval_results.json").open("w", encoding="utf-8") as handle:
        json.dump({"summary": metrics, "rows": rows}, handle, ensure_ascii=False, indent=2)

    with (directory / "eval_results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "question",
                "context_relevance",
                "faithfulness",
                "answer_relevance",
                "answer",
                "sources",
                "citation_passed",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _faithfulness(answer: str, context: str) -> float:
    context_tokens = set(tokenize(context))
    answer_tokens = [token for token in tokenize(answer) if not token.isdigit()]
    if not answer_tokens:
        return 0.0
    supported = sum(1 for token in answer_tokens if token in context_tokens)
    return supported / len(answer_tokens)


def _keyword_coverage(answer: str, expected_keywords: Sequence[str]) -> float:
    if not expected_keywords:
        return 0.0
    normalized_answer = normalize_text(answer)
    answer_tokens = set(tokenize(answer))
    hits = 0
    for keyword in expected_keywords:
        normalized_keyword = normalize_text(keyword)
        keyword_tokens = set(tokenize(keyword))
        if normalized_keyword in normalized_answer:
            hits += 1
        elif keyword_tokens and keyword_tokens.issubset(answer_tokens):
            hits += 1
    return hits / len(expected_keywords)
