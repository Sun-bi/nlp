#!/usr/bin/env bash
set -euo pipefail

QUESTION="${*:-Redis 的 AOF 和 RDB 持久化有什么区别？}"

cd "$(dirname "$0")"

python3 infer.py \
  --corpus data/raw/redis_official_docs.jsonl \
  --index-dir data/index_official \
  --question "$QUESTION"
