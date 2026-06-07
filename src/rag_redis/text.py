"""Text normalization and lightweight Redis-aware tokenization."""

from __future__ import annotations

import re
from typing import Iterable, List


ASCII_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_:+.-]*|[0-9]+")
CJK_RE = re.compile(r"[\u4e00-\u9fff]+")
SPACE_RE = re.compile(r"\s+")

REDIS_TERMS = [
    "持久化",
    "过期策略",
    "过期时间",
    "内存淘汰",
    "主从复制",
    "复制",
    "哨兵",
    "集群",
    "分片",
    "事务",
    "发布订阅",
    "消费者组",
    "有序集合",
    "字符串",
    "哈希",
    "列表",
    "集合",
    "流",
    "缓存穿透",
    "缓存击穿",
    "缓存雪崩",
    "键空间",
    "快照",
    "追加日志",
    "脚本",
    "原子性",
]

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "when",
    "while",
    "with",
    "的",
    "了",
    "和",
    "是",
    "在",
    "有",
    "什么",
    "如何",
    "怎么",
}


def normalize_text(text: str) -> str:
    """Normalize text while keeping Redis commands and Chinese terms readable."""
    lowered = text.lower()
    lowered = SPACE_RE.sub(" ", lowered)
    return lowered.strip()


def _cjk_ngrams(sequence: str) -> Iterable[str]:
    if len(sequence) <= 4:
        yield sequence
    for size in (2, 3):
        for index in range(0, max(len(sequence) - size + 1, 0)):
            yield sequence[index : index + size]


def tokenize(text: str) -> List[str]:
    """Tokenize mixed Chinese/English Redis documentation text.

    The tokenizer is intentionally dependency-free so the project can run in
    restricted course environments. It preserves exact command names such as
    SETEX, RDB, and AOF, and adds Redis-specific Chinese phrases for BM25.
    """
    normalized = normalize_text(text)
    tokens: List[str] = []

    for match in ASCII_RE.findall(normalized):
        if match not in STOPWORDS:
            tokens.append(match)

    for term in REDIS_TERMS:
        if term in normalized:
            tokens.append(term)

    for sequence in CJK_RE.findall(normalized):
        for token in _cjk_ngrams(sequence):
            if token not in STOPWORDS:
                tokens.append(token)

    return tokens


def unique_keywords(text: str) -> List[str]:
    """Return deterministic unique tokens for reporting and evaluation."""
    seen = set()
    result = []
    for token in tokenize(text):
        if token not in seen:
            seen.add(token)
            result.append(token)
    return result
