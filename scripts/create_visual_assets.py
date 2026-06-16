#!/usr/bin/env python3
"""Create visual assets used by the Redis RAG presentation."""

from __future__ import annotations

import json
import math
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PIL import Image, ImageDraw, ImageFont

from rag_redis.pipeline import load_pipeline


OUT = ROOT / "slides" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

WIDE = (1600, 900)
RED = "#D92D20"
RED_DARK = "#8A1C14"
INK = "#17212B"
TEXT = "#24313D"
MUTED = "#64748B"
BG = "#F7F9FC"
PANEL = "#FFFFFF"
LINE = "#CBD5E1"
TEAL = "#0F766E"
BLUE = "#2563EB"
AMBER = "#F59E0B"
GREEN = "#16A34A"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size, index=0)
    return ImageFont.load_default()


F_TITLE = font(54, True)
F_H1 = font(38, True)
F_H2 = font(30, True)
F_BODY = font(25)
F_SMALL = font(21)
F_MONO = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22) if Path("/System/Library/Fonts/Menlo.ttc").exists() else font(22)


def rounded(draw: ImageDraw.ImageDraw, xy, radius=24, fill=PANEL, outline=LINE, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False, replace_whitespace=False))


def draw_wrapped(draw, text, xy, width_chars, fnt, fill=TEXT, spacing=8):
    draw.multiline_text(xy, wrap(text, width_chars), font=fnt, fill=fill, spacing=spacing)


def shadow_card(draw, xy, radius=26, fill=PANEL, outline=LINE):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle((x1 + 8, y1 + 10, x2 + 8, y2 + 10), radius=radius, fill="#D9E1EA")
    rounded(draw, xy, radius=radius, fill=fill, outline=outline, width=2)


def create_hero():
    img = Image.new("RGB", WIDE, INK)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1600, 900), fill=INK)
    draw.rectangle((0, 0, 520, 900), fill=RED_DARK)
    draw.polygon([(520, 0), (720, 0), (560, 900), (420, 900)], fill="#B3261E")
    draw.text((90, 115), "Redis-RAG", font=F_TITLE, fill="white")
    draw.text((95, 195), "垂直领域深度问答系统", font=F_H2, fill="#F8FAFC")
    draw.text((98, 265), "Private KB  ·  Hybrid Retrieval  ·  DeepSeek", font=F_SMALL, fill="#DDE7F3")

    # Document stack
    for i, color in enumerate(["#FFFFFF", "#FDE8E5", "#EAF2FF"]):
        x = 760 + i * 20
        y = 145 + i * 18
        shadow_card(draw, (x, y, x + 360, y + 235), radius=24, fill=color, outline="#E2E8F0")
        draw.text((x + 34, y + 32), "Redis Docs", font=F_H2, fill=INK)
        for j in range(4):
            draw.rounded_rectangle((x + 36, y + 92 + j * 30, x + 310, y + 108 + j * 30), radius=7, fill="#CBD5E1")

    # Search and answer panels
    shadow_card(draw, (910, 485, 1435, 735), radius=30, fill="#FFFFFF", outline="#D7E1ED")
    draw.text((950, 525), "Question", font=F_H2, fill=RED)
    draw.text((950, 585), "AOF 和 RDB 有什么区别？", font=F_BODY, fill=INK)
    draw.rounded_rectangle((950, 650, 1390, 685), radius=16, fill="#EAF2FF")
    draw.text((970, 652), "redis:persistence  score=1.0000", font=F_SMALL, fill=BLUE)
    draw.line((1110, 335, 1090, 485), fill=RED, width=8)
    draw.polygon([(1090, 485), (1065, 450), (1115, 450)], fill=RED)
    img.save(OUT / "hero_redis_rag.png")


def create_kb_overview():
    img = Image.new("RGB", WIDE, BG)
    draw = ImageDraw.Draw(img)
    draw.text((70, 60), "Redis 私有知识库覆盖范围", font=F_TITLE, fill=INK)
    draw.text((72, 128), "16 个主题 · 官方文档 URL 可追溯 · JSONL 结构化存储", font=F_BODY, fill=MUTED)
    topics = [
        ("String", "GET / SET / INCR", RED),
        ("Hash", "HSET / HGETALL", TEAL),
        ("List", "LPUSH / BLPOP", BLUE),
        ("Stream", "XADD / XREADGROUP", AMBER),
        ("Sorted Set", "ZADD / ZRANGE", RED),
        ("TTL", "EXPIRE / PERSIST", TEAL),
        ("RDB/AOF", "snapshot / append log", BLUE),
        ("Cluster", "hash slot / MOVED", AMBER),
        ("Sentinel", "failover / monitor", RED),
        ("Lua", "EVAL / atomic", TEAL),
        ("Pub/Sub", "publish / subscribe", BLUE),
        ("Cache Risks", "penetration / avalanche", AMBER),
    ]
    cols = 4
    for i, (title, desc, color) in enumerate(topics):
        col = i % cols
        row = i // cols
        x = 80 + col * 370
        y = 220 + row * 180
        shadow_card(draw, (x, y, x + 310, y + 125), radius=24, fill="#FFFFFF", outline="#DDE5EF")
        draw.rectangle((x, y, x + 10, y + 125), fill=color)
        draw.text((x + 35, y + 26), title, font=F_H2, fill=INK)
        draw.text((x + 35, y + 78), desc, font=F_SMALL, fill=MUTED)
    img.save(OUT / "knowledge_base_overview.png")


def create_architecture_photo():
    img = Image.new("RGB", WIDE, BG)
    draw = ImageDraw.Draw(img)
    draw.text((70, 60), "RAG 数据流：从文档到带引用答案", font=F_TITLE, fill=INK)
    nodes = [
        ("Redis\nDocs", 80, 250, RED),
        ("Clean\nJSONL", 310, 250, TEAL),
        ("Chunking", 540, 250, BLUE),
        ("Embedding\nVector DB", 760, 165, AMBER),
        ("BM25\nIndex", 760, 335, TEAL),
        ("Hybrid\nRetriever", 1010, 250, RED),
        ("DeepSeek /\nFallback", 1240, 250, BLUE),
    ]
    for text, x, y, color in nodes:
        shadow_card(draw, (x, y, x + 165, y + 95), radius=22, fill="#FFFFFF", outline=color)
        draw.text((x + 20, y + 23), text, font=F_SMALL, fill=INK, spacing=4)
    arrows = [
        (245, 298, 310, 298),
        (475, 298, 540, 298),
        (705, 298, 760, 210),
        (705, 298, 760, 380),
        (925, 210, 1010, 292),
        (925, 380, 1010, 305),
        (1175, 298, 1240, 298),
    ]
    for x1, y1, x2, y2 in arrows:
        draw.line((x1, y1, x2, y2), fill=RED, width=5)
        ang = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - 18 * math.cos(ang - 0.5), y2 - 18 * math.sin(ang - 0.5))
        p2 = (x2 - 18 * math.cos(ang + 0.5), y2 - 18 * math.sin(ang + 0.5))
        draw.polygon([(x2, y2), p1, p2], fill=RED)
    shadow_card(draw, (250, 560, 1350, 720), radius=26, fill="#FFFFFF", outline="#DDE5EF")
    draw.text((300, 590), "高级策略", font=F_H2, fill=RED)
    draw.text((300, 648), "Query Rewriting + BM25/Vector Hybrid Retrieval + Context Filtering", font=F_BODY, fill=INK)
    img.save(OUT / "architecture_flow.png")


def get_infer_payload():
    pipeline = load_pipeline(ROOT / "data/raw/redis_seed_docs.jsonl", ROOT / "data/index", rebuild=True)
    question = "Redis 的 AOF 和 RDB 持久化有什么区别？"
    generated, contexts = pipeline.ask(question, top_k=5)
    return {
        "question": question,
        "answer": generated.answer,
        "sources": [
            {
                "doc_id": source.doc_id,
                "title": source.title,
                "score": source.score,
            }
            for source in generated.sources
        ],
        "retrieved": [
            {
                "doc_id": result.chunk.doc_id,
                "title": result.chunk.source_title,
                "combined": result.combined_score,
                "vector": result.vector_score,
                "bm25": result.bm25_score,
            }
            for result in contexts[:5]
        ],
    }


def create_inference_result():
    payload = get_infer_payload()
    img = Image.new("RGB", WIDE, BG)
    draw = ImageDraw.Draw(img)
    draw.text((70, 55), "一键推理结果截图", font=F_TITLE, fill=INK)
    draw.text((72, 125), "python3 infer.py --question \"Redis 的 AOF 和 RDB 持久化有什么区别？\"", font=F_SMALL, fill=MUTED)
    shadow_card(draw, (80, 190, 1515, 790), radius=28, fill="#111827", outline="#111827")
    draw.text((120, 230), "$ python3 infer.py --question 'Redis 的 AOF 和 RDB 持久化有什么区别？'", font=F_SMALL, fill="#A7F3D0")
    draw.text((120, 295), "问题", font=F_H2, fill="#FCA5A5")
    draw.text((120, 345), payload["question"], font=F_BODY, fill="#F9FAFB")
    draw.text((120, 405), "答案", font=F_H2, fill="#FCA5A5")
    answer = payload["answer"].replace("根据检索到的 Redis 文档，", "")
    draw_wrapped(draw, answer, (120, 455), 46, F_SMALL, fill="#E5E7EB", spacing=7)
    draw.text((930, 295), "来源", font=F_H2, fill="#FCA5A5")
    y = 350
    for i, source in enumerate(payload["sources"], start=1):
        draw.text((930, y), f"[{i}] {source['doc_id']}", font=F_BODY, fill="#F9FAFB")
        draw.text((930, y + 42), f"score={source['score']:.4f}", font=F_SMALL, fill="#93C5FD")
        y += 95
    img.save(OUT / "inference_result.png")


def create_evaluation_chart():
    summary = json.loads((ROOT / "outputs/eval_results.json").read_text(encoding="utf-8")).get("summary", {})
    if not summary:
        subprocess.run([sys.executable, str(ROOT / "evaluate.py"), "--rebuild"], check=True)
        summary = json.loads((ROOT / "outputs/eval_results.json").read_text(encoding="utf-8"))["summary"]
    img = Image.new("RGB", WIDE, BG)
    draw = ImageDraw.Draw(img)
    draw.text((70, 60), "三维量化评估结果", font=F_TITLE, fill=INK)
    draw.text((72, 130), "Context Relevance · Faithfulness · Answer Relevance", font=F_BODY, fill=MUTED)
    metrics = [
        ("Context Relevance", summary["context_relevance"], RED),
        ("Faithfulness", summary["faithfulness"], TEAL),
        ("Answer Relevance", summary["answer_relevance"], AMBER),
    ]
    y = 250
    for label, value, color in metrics:
        draw.text((130, y - 10), label, font=F_H2, fill=INK)
        draw.rounded_rectangle((520, y, 1320, y + 42), radius=20, fill="#E5E7EB")
        draw.rounded_rectangle((520, y, 520 + int(800 * value), y + 42), radius=20, fill=color)
        draw.text((1360, y - 2), f"{value:.4f}", font=F_H2, fill=INK)
        y += 150
    shadow_card(draw, (160, 720, 1440, 810), radius=24, fill="#FFFFFF", outline="#DDE5EF")
    draw.text((205, 748), "结论：检索覆盖稳定，答案大部分能被上下文支持，关键词覆盖仍有优化空间。", font=F_BODY, fill=INK)
    img.save(OUT / "evaluation_results.png")


def create_retrieval_scores():
    payload = get_infer_payload()
    img = Image.new("RGB", WIDE, BG)
    draw = ImageDraw.Draw(img)
    draw.text((70, 55), "检索命中文档与分数", font=F_TITLE, fill=INK)
    draw.text((72, 125), "Top-k contexts expose combined/vector/BM25 scores for debugging", font=F_SMALL, fill=MUTED)
    headers = ["Rank", "doc_id", "combined", "vector", "BM25"]
    widths = [140, 520, 230, 230, 230]
    x0, y0 = 120, 220
    row_h = 82
    x = x0
    for header, width in zip(headers, widths):
        draw.rectangle((x, y0, x + width, y0 + row_h), fill=RED, outline=LINE)
        draw.text((x + 22, y0 + 26), header, font=F_SMALL, fill="white")
        x += width
    for r, item in enumerate(payload["retrieved"], start=1):
        y = y0 + r * row_h
        fill = "#FFFFFF" if r % 2 else "#F8FAFC"
        x = x0
        values = [
            str(r),
            item["doc_id"],
            f"{item['combined']:.4f}",
            f"{item['vector']:.4f}",
            f"{item['bm25']:.4f}",
        ]
        for value, width in zip(values, widths):
            draw.rectangle((x, y, x + width, y + row_h), fill=fill, outline=LINE)
            draw.text((x + 22, y + 26), value, font=F_SMALL, fill=INK)
            x += width
    draw.text((120, 735), "redis:persistence 排名第一，说明 AOF/RDB 问题被正确定位到持久化文档。", font=F_BODY, fill=INK)
    img.save(OUT / "retrieval_scores.png")


def main() -> None:
    create_hero()
    create_kb_overview()
    create_architecture_photo()
    create_inference_result()
    create_evaluation_chart()
    create_retrieval_scores()
    print(OUT)


if __name__ == "__main__":
    main()
