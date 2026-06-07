"""Answer generation with extractive fallback and optional OpenAI-compatible LLM."""

from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass
from typing import List, Sequence

from .retriever import RetrievalResult
from .text import tokenize


@dataclass(frozen=True)
class Source:
    doc_id: str
    title: str
    url: str
    score: float


@dataclass(frozen=True)
class GeneratedAnswer:
    answer: str
    sources: List[Source]


class ExtractiveGenerator:
    """Grounded answer generator that only uses retrieved chunks."""

    def generate(self, question: str, contexts: Sequence[RetrievalResult]) -> GeneratedAnswer:
        if not contexts:
            return GeneratedAnswer(
                answer="未在 Redis 知识库中找到足够依据回答该问题。",
                sources=[],
            )

        max_score = max(result.combined_score for result in contexts) or 1.0
        grounded_contexts = [
            result for result in contexts if result.combined_score >= max_score * 0.5
        ] or [contexts[0]]
        question_tokens = set(tokenize(question))
        selected_sentences: List[str] = []
        sources: List[Source] = []

        for index, result in enumerate(grounded_contexts[:3], start=1):
            chunk = result.chunk
            sources.append(
                Source(
                    doc_id=chunk.doc_id,
                    title=chunk.source_title,
                    url=chunk.url,
                    score=result.combined_score,
                )
            )
            sentences = _split_sentences(chunk.text)
            ranked = sorted(
                sentences,
                key=lambda sentence: len(question_tokens.intersection(tokenize(sentence))),
                reverse=True,
            )
            relevant = [
                sentence
                for sentence in ranked
                if question_tokens.intersection(tokenize(sentence))
            ][:4]
            if not relevant and ranked:
                relevant = ranked[:1]
            if relevant:
                selected_sentences.append(f"{' '.join(relevant)} [{index}]")

        body = " ".join(selected_sentences)
        answer = (
            "根据检索到的 Redis 文档，"
            + body
            + "。以上回答仅基于列出的知识库片段。"
        )
        return GeneratedAnswer(answer=answer, sources=sources)


class OpenAICompatibleGenerator:
    """Call an OpenAI-compatible chat completion endpoint when configured."""

    def __init__(self, fallback: ExtractiveGenerator | None = None) -> None:
        self.fallback = fallback or ExtractiveGenerator()
        deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_key = os.getenv("OPENAI_API_KEY") or deepseek_key
        default_base_url = "https://api.deepseek.com" if deepseek_key else "https://api.openai.com/v1"
        default_model = "deepseek-v4-pro" if deepseek_key else "gpt-4o-mini"
        self.base_url = os.getenv("OPENAI_BASE_URL", default_base_url)
        self.model = os.getenv("OPENAI_MODEL", default_model)

    def generate(self, question: str, contexts: Sequence[RetrievalResult]) -> GeneratedAnswer:
        if not self.api_key:
            return self.fallback.generate(question, contexts)

        prompt_context = "\n\n".join(
            f"[{index}] {result.chunk.source_title}\nURL: {result.chunk.url}\n{result.chunk.text}"
            for index, result in enumerate(contexts[:5], start=1)
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "你是 Redis 文档问答助手。只能依据给定上下文回答；"
                    "如果上下文不足，明确说明无法从知识库确认。答案必须带 [1] 形式引用。"
                ),
            },
            {
                "role": "user",
                "content": f"问题：{question}\n\n上下文：\n{prompt_context}",
            },
        ]
        payload = json.dumps(
            {"model": self.model, "messages": messages, "temperature": 0.1},
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"].strip()
        except Exception:
            return self.fallback.generate(question, contexts)

        sources = [
            Source(
                doc_id=result.chunk.doc_id,
                title=result.chunk.source_title,
                url=result.chunk.url,
                score=result.combined_score,
            )
            for result in contexts[:5]
        ]
        return GeneratedAnswer(answer=content, sources=sources)


def _split_sentences(text: str) -> List[str]:
    sentences = [part.strip() for part in re.split(r"[。！？.!?]\s*", text) if part.strip()]
    return sentences or [text.strip()]
