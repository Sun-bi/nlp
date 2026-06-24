#!/usr/bin/env python3
"""Collect and clean selected Redis official documentation pages."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag_redis.corpus import Document, save_jsonl_documents  # noqa: E402


REDIS_DOC_PAGES: Dict[str, str] = {
    "overview": "https://redis.io/docs/latest/",
    "strings": "https://redis.io/docs/latest/develop/data-types/strings/",
    "hashes": "https://redis.io/docs/latest/develop/data-types/hashes/",
    "lists": "https://redis.io/docs/latest/develop/data-types/lists/",
    "streams": "https://redis.io/docs/latest/develop/data-types/streams/",
    "sorted_sets": "https://redis.io/docs/latest/develop/data-types/sorted-sets/",
    "expiration": "https://redis.io/docs/latest/commands/expire/",
    "persistence": "https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/",
    "replication": "https://redis.io/docs/latest/operate/oss_and_stack/management/replication/",
    "sentinel": "https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/",
    "cluster": "https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/",
    "transactions": "https://redis.io/docs/latest/develop/using-commands/transactions/",
    "scripting": "https://redis.io/docs/latest/develop/programmability/eval-intro/",
    "pubsub": "https://redis.io/docs/latest/develop/pubsub/",
}


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.parts: List[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "nav", "footer", "header", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "footer", "header", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        text = re.sub(r"\s+", " ", data).strip()
        if len(text) >= 30:
            self.parts.append(text)

    def text(self) -> str:
        seen = set()
        cleaned = []
        for part in self.parts:
            if is_page_metadata(part):
                continue
            if part not in seen:
                seen.add(part)
                cleaned.append(part)
        return "\n".join(cleaned)


def is_page_metadata(text: str) -> bool:
    stripped = text.strip()
    return (
        stripped.startswith("{")
        and '"duplicateOf"' in stripped
        and '"tableOfContents"' in stripped
    )


def fetch_page(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "redis-rag-system/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="ignore")


def collect() -> List[Document]:
    documents: List[Document] = []
    for slug, url in REDIS_DOC_PAGES.items():
        try:
            html = fetch_page(url)
        except Exception as exc:
            print(f"warning: failed to fetch {url}: {exc}", file=sys.stderr)
            continue
        parser = TextExtractor()
        parser.feed(html)
        text = parser.text()
        if not text:
            print(f"warning: empty page after cleaning {url}", file=sys.stderr)
            continue
        documents.append(
            Document(
                doc_id=f"redis:{slug}",
                title=f"Redis {slug.replace('_', ' ')}",
                url=url,
                text=text,
            )
        )
    return documents


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect Redis docs into JSONL corpus")
    parser.add_argument("--output", default="data/raw/redis_official_docs.jsonl", help="Output JSONL path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    documents = collect()
    save_jsonl_documents(documents, args.output)
    print(json.dumps({"output": args.output, "documents": len(documents)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
