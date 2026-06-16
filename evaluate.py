#!/usr/bin/env python3
"""Run quantitative evaluation for the Redis RAG system."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from rag_redis.evaluation import (
    evaluate_single,
    load_eval_samples,
    save_eval_outputs,
    summarize_metrics,
)
from rag_redis.pipeline import load_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Redis RAG")
    parser.add_argument("--corpus", default="data/raw/redis_seed_docs.jsonl", help="JSONL corpus path")
    parser.add_argument("--eval", default="data/eval/eval_questions.jsonl", help="Evaluation set JSONL")
    parser.add_argument("--index-dir", default="data/index", help="Directory for vector index files")
    parser.add_argument("--output-dir", default="outputs", help="Directory for evaluation outputs")
    parser.add_argument("--top-k", type=int, default=5, help="Number of retrieved chunks")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild index before evaluation")
    parser.add_argument("--embedding-model", default="hashing", help="hashing, bge, or a SentenceTransformer model")
    parser.add_argument("--vector-store", default="local", choices=["local", "faiss", "chroma"], help="Vector store backend when rebuilding")
    parser.add_argument("--retrieval-mode", default="hybrid", choices=["vector", "bm25", "hybrid_no_rerank", "hybrid"], help="Retrieval strategy")
    parser.add_argument("--reranker", default="lightweight", choices=["none", "lightweight", "cross-encoder", "bge-reranker"], help="Second-stage reranker")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = load_pipeline(
        args.corpus,
        args.index_dir,
        rebuild=args.rebuild,
        embedding_model=args.embedding_model,
        vector_store=args.vector_store,
        retrieval_mode=args.retrieval_mode,
        reranker=args.reranker,
    )
    samples = load_eval_samples(args.eval)

    row_metrics: List[Dict[str, float]] = []
    rows: List[Dict[str, object]] = []
    for sample in samples:
        generated, contexts = pipeline.ask(str(sample["question"]), top_k=args.top_k)
        metrics = evaluate_single(sample, generated.answer, contexts)
        row_metrics.append(metrics)
        rows.append(
            {
                "question": sample["question"],
                "context_relevance": metrics["context_relevance"],
                "faithfulness": metrics["faithfulness"],
                "answer_relevance": metrics["answer_relevance"],
                "answer": generated.answer,
                "sources": "; ".join(source.doc_id for source in generated.sources),
                "citation_passed": generated.citation_check.passed
                if generated.citation_check
                else False,
            }
        )

    summary = summarize_metrics(row_metrics)
    save_eval_outputs(rows, summary, args.output_dir)

    print("Redis RAG evaluation")
    print(f"Samples: {len(samples)}")
    print(f"Context Relevance: {summary['context_relevance']:.4f}")
    print(f"Faithfulness: {summary['faithfulness']:.4f}")
    print(f"Answer Relevance: {summary['answer_relevance']:.4f}")
    print(f"Saved outputs to: {args.output_dir}")


if __name__ == "__main__":
    main()
