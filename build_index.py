#!/usr/bin/env python3
"""Build the Redis RAG local vector index."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from rag_redis.pipeline import build_index


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Redis RAG index")
    parser.add_argument("--corpus", default="data/raw/redis_seed_docs.jsonl", help="JSONL corpus path")
    parser.add_argument("--index-dir", default="data/index", help="Directory for vector index files")
    parser.add_argument("--chunk-size", type=int, default=320, help="Chunk size in tokens")
    parser.add_argument("--overlap", type=int, default=40, help="Chunk overlap in tokens")
    parser.add_argument("--dimensions", type=int, default=256, help="Hashing embedding dimensions")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    chunks = build_index(
        corpus_path=args.corpus,
        index_dir=args.index_dir,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        dimensions=args.dimensions,
    )
    print(f"Built Redis RAG index")
    print(f"Corpus: {Path(args.corpus).resolve()}")
    print(f"Index: {Path(args.index_dir).resolve()}")
    print(f"Chunks: {len(chunks)}")


if __name__ == "__main__":
    main()
