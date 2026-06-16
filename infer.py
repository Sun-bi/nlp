#!/usr/bin/env python3
"""One-command Redis RAG inference script."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from rag_redis.pipeline import load_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask questions over the Redis RAG knowledge base")
    parser.add_argument(
        "--question",
        default="Redis 的 AOF 和 RDB 持久化有什么区别？",
        help="Question to ask",
    )
    parser.add_argument("--corpus", default="data/raw/redis_seed_docs.jsonl", help="JSONL corpus path")
    parser.add_argument("--index-dir", default="data/index", help="Directory for vector index files")
    parser.add_argument("--top-k", type=int, default=5, help="Number of retrieved chunks")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild index before inference")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pipeline = load_pipeline(
        corpus_path=args.corpus,
        index_dir=args.index_dir,
        rebuild=args.rebuild,
    )
    generated, contexts = pipeline.ask(args.question, top_k=args.top_k)

    payload = {
        "question": args.question,
        "answer": generated.answer,
        "sources": [
            {
                "doc_id": source.doc_id,
                "title": source.title,
                "url": source.url,
                "score": round(source.score, 4),
            }
            for source in generated.sources
        ],
        "retrieved_contexts": [
            {
                "doc_id": result.chunk.doc_id,
                "title": result.chunk.source_title,
                "score": round(result.final_score, 4),
                "combined_score": round(result.combined_score, 4),
                "rerank_score": round(result.rerank_score, 4),
                "term_coverage": round(result.term_coverage, 4),
                "vector_score": round(result.vector_score, 4),
                "bm25_score": round(result.bm25_score, 4),
            }
            for result in contexts
        ],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print("\n问题")
    print(args.question)
    print("\n答案")
    print(generated.answer)
    print("\n来源")
    for index, source in enumerate(generated.sources, start=1):
        print(f"[{index}] {source.title} ({source.doc_id}) score={source.score:.4f}")
        if source.url:
            print(f"    {source.url}")
    print(f"\n索引目录: {Path(args.index_dir).resolve()}")


if __name__ == "__main__":
    main()
