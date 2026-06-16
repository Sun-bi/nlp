#!/usr/bin/env python3
"""Compare pure vector, BM25, hybrid, and hybrid+rerank retrieval strategies."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from rag_redis.evaluation import load_eval_samples
from rag_redis.pipeline import load_pipeline


STRATEGIES = [
    ("pure_vector", "vector", "none"),
    ("bm25", "bm25", "none"),
    ("hybrid", "hybrid_no_rerank", "none"),
    ("hybrid_rerank", "hybrid", "lightweight"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare Redis RAG retrieval strategies")
    parser.add_argument("--corpus", default="data/raw/redis_seed_docs.jsonl")
    parser.add_argument("--eval", default="data/eval/eval_questions.jsonl")
    parser.add_argument("--index-dir", default="data/index")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--rebuild", action="store_true")
    parser.add_argument("--embedding-model", default="hashing", help="hashing, bge, or a SentenceTransformer model")
    parser.add_argument("--vector-store", default="local", choices=["local", "faiss", "chroma"], help="Vector store backend when rebuilding")
    parser.add_argument("--hybrid-reranker", default="lightweight", choices=["lightweight", "cross-encoder", "bge-reranker"], help="Reranker used by the hybrid_rerank strategy")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    samples = load_eval_samples(args.eval)
    rows: List[Dict[str, object]] = []
    summaries: List[Dict[str, object]] = []

    for name, retrieval_mode, reranker in STRATEGIES:
        pipeline = load_pipeline(
            args.corpus,
            args.index_dir,
            rebuild=args.rebuild,
            embedding_model=args.embedding_model,
            vector_store=args.vector_store,
            retrieval_mode=retrieval_mode,
            reranker=args.hybrid_reranker if name == "hybrid_rerank" else reranker,
        )
        relevance_scores: List[float] = []
        top1_hits: List[float] = []
        reciprocal_ranks: List[float] = []
        for sample in samples:
            contexts = pipeline.retriever.search(str(sample["question"]), top_k=args.top_k)
            gold = set(sample.get("gold_doc_ids", []))
            retrieved = [result.chunk.doc_id for result in contexts]
            hit_count = len(gold.intersection(retrieved))
            relevance = hit_count / len(gold) if gold else 0.0
            top1 = 1.0 if retrieved and retrieved[0] in gold else 0.0
            rr = 0.0
            for index, doc_id in enumerate(retrieved, start=1):
                if doc_id in gold:
                    rr = 1.0 / index
                    break
            relevance_scores.append(relevance)
            top1_hits.append(top1)
            reciprocal_ranks.append(rr)
            rows.append(
                {
                    "strategy": name,
                    "question": sample["question"],
                    "top1": retrieved[0] if retrieved else "",
                    "retrieved": "; ".join(retrieved),
                    "context_relevance": round(relevance, 4),
                    "top1_hit": round(top1, 4),
                    "reciprocal_rank": round(rr, 4),
                }
            )
        summaries.append(
            {
                "strategy": name,
                "context_relevance": round(sum(relevance_scores) / len(relevance_scores), 4),
                "top1_hit": round(sum(top1_hits) / len(top1_hits), 4),
                "mrr": round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4),
            }
        )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "retrieval_comparison.json").open("w", encoding="utf-8") as handle:
        json.dump({"summary": summaries, "rows": rows}, handle, ensure_ascii=False, indent=2)
    with (output_dir / "retrieval_comparison.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("Redis RAG retrieval comparison")
    for item in summaries:
        print(
            f"{item['strategy']}: "
            f"Context={item['context_relevance']:.4f}, "
            f"Top1={item['top1_hit']:.4f}, "
            f"MRR={item['mrr']:.4f}"
        )
    print(f"Saved outputs to: {output_dir}")


if __name__ == "__main__":
    main()
