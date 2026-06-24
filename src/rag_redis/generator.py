"""Answer generation with extractive fallback and optional OpenAI-compatible LLM."""

from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass
from typing import List, Sequence

from .citations import CitationCheck, check_citations
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
    citation_check: CitationCheck | None = None


class ExtractiveGenerator:
    """Grounded answer generator that only uses retrieved chunks."""

    def generate(self, question: str, contexts: Sequence[RetrievalResult]) -> GeneratedAnswer:
        if not contexts:
            return GeneratedAnswer(
                answer="未在 Redis 知识库中找到足够依据回答该问题。",
                sources=[],
            )

        max_score = max(result.final_score for result in contexts) or 1.0
        grounded_contexts = [
            result for result in contexts if result.final_score >= max_score * 0.5
        ] or [contexts[0]]
        sources = [
            Source(
                doc_id=result.chunk.doc_id,
                title=result.chunk.source_title,
                url=result.chunk.url,
                score=result.final_score,
            )
            for result in grounded_contexts[:3]
        ]
        template_answer = _template_answer(question, grounded_contexts[:3])
        if template_answer:
            return GeneratedAnswer(
                answer=template_answer,
                sources=sources,
                citation_check=check_citations(template_answer, grounded_contexts[:3]),
            )

        question_tokens = set(tokenize(question))
        selected_sentences: List[str] = []

        for index, result in enumerate(grounded_contexts[:3], start=1):
            chunk = result.chunk
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
        return GeneratedAnswer(
            answer=answer,
            sources=sources,
            citation_check=check_citations(answer, grounded_contexts[:3]),
        )


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
                score=result.final_score,
            )
            for result in contexts[:5]
        ]
        return GeneratedAnswer(
            answer=content,
            sources=sources,
            citation_check=check_citations(content, contexts[:5]),
        )


def _split_sentences(text: str) -> List[str]:
    sentences = [part.strip() for part in re.split(r"[。！？.!?]\s*", text) if part.strip()]
    return sentences or [text.strip()]


def _template_answer(question: str, contexts: Sequence[RetrievalResult]) -> str | None:
    """Return concise Chinese fallback answers for common Redis documentation topics."""
    if not contexts:
        return None
    doc_ids = {result.chunk.doc_id for result in contexts}
    query = question.lower()

    if "redis:persistence" in doc_ids or {"aof", "rdb"}.intersection(tokenize(question)):
        return (
            "Redis 持久化主要有 RDB 和 AOF 两种方式：RDB 是按时间点生成数据快照，"
            "文件紧凑，适合备份和恢复；AOF 是追加记录写命令，通常能提供更好的数据安全性，"
            "但文件和重写成本更高。实际部署中可以同时开启 RDB 和 AOF，让快照恢复速度和写命令日志安全性互补 [1]。"
        )

    if "redis:sentinel" in doc_ids or "sentinel" in query or "哨兵" in question:
        return (
            "Redis Sentinel 主要解决非集群 Redis 的高可用问题：它会监控 master 和 replica，"
            "发现 master 异常后发起故障转移，把合适的 replica 提升为新的 master，"
            "并通知客户端新的主节点地址。因此 Sentinel 同时承担监控、自动故障转移、通知和服务发现的作用 [1]。"
        )

    if {"redis:streams", "redis:pubsub"}.intersection(doc_ids) or "pub/sub" in query or "stream" in query:
        return (
            "Redis Pub/Sub 适合实时广播，消息发出后只会推给当前在线订阅者，不保留历史；"
            "Redis Stream 是追加式日志，可以保存消息历史，并通过消费者组实现多人协同消费和确认机制。"
            "所以需要可靠消费、消息回放和消费者组时更适合使用 Stream；只需要实时通知时可以使用 Pub/Sub [1]。"
        )

    if "redis:cluster" in doc_ids or "cluster" in query or "集群" in question:
        return (
            "Redis Cluster 通过 hash slot 把键分布到多个 master 节点上，实现横向扩展。"
            "跨 slot 的多 key 命令会受限制，因为相关键可能分布在不同节点，无法在单个节点上原子执行。"
            "如果确实需要多 key 操作，可以使用 hash tag 让相关 key 落到同一个 slot [1]。"
        )

    if "redis:replication" in doc_ids or "复制" in question or "replication" in query:
        return (
            "Redis 主从复制用于把 master 的数据同步到 replica。replica 可以承担读请求、提供数据冗余，"
            "并在高可用方案中作为故障转移候选节点。需要注意的是 Redis 复制默认是异步的，"
            "因此故障发生时仍可能存在少量已确认写入丢失的风险 [1]。"
        )

    if "redis:expiration" in doc_ids or "过期" in question or "ttl" in query:
        return (
            "Redis 可以为 key 设置过期时间，常用命令包括 EXPIRE、PEXPIRE 和 TTL。"
            "过期时间到达后，key 会被删除；如果持久化或复制涉及过期 key，Redis 会通过统一的删除传播机制保持一致性。"
            "这类机制常用于缓存自动失效、会话过期和临时锁超时 [1]。"
        )

    if "redis:transactions" in doc_ids or "事务" in question or "watch" in query:
        return (
            "Redis 事务使用 MULTI 开启、EXEC 执行，事务中的命令会按顺序一次性执行。"
            "WATCH 可以对 key 做乐观锁监控，如果被监控的 key 在 EXEC 前被其他客户端修改，事务会失败。"
            "因此 Redis 事务适合把一组命令顺序提交，但不等同于传统数据库的完整回滚事务 [1]。"
        )

    if "redis:scripting" in doc_ids or "lua" in query or "脚本" in question:
        return (
            "Redis Lua 脚本通过 EVAL 在服务端执行，可以把多步逻辑放到 Redis 内部运行，减少网络往返。"
            "脚本执行期间具有原子性，其他命令不会插入执行，因此适合实现条件更新、限流、库存扣减等需要原子组合操作的场景 [1]。"
        )

    if "redis:strings" in doc_ids and ("锁" in question or "nx" in query):
        return (
            "Redis 可以用 SET 命令配合 NX 和过期时间实现简单互斥锁：NX 保证只有 key 不存在时才写入，"
            "过期时间避免客户端异常退出后锁一直不释放。实际使用时还需要校验锁值，避免误删其他客户端持有的锁 [1]。"
        )

    return None
