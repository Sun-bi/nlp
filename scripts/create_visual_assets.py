#!/usr/bin/env python3
"""Create visual assets used by the Redis RAG presentation."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from PIL import Image, ImageDraw, ImageFont

OUT = ROOT / "slides" / "assets"
OUT.mkdir(parents=True, exist_ok=True)
RUN_LOGS = ROOT / "outputs" / "run_logs"
RUN_LOGS.mkdir(parents=True, exist_ok=True)

SCALE = 2
WIDE = (1600 * SCALE, 900 * SCALE)
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


def _scale(value: int | float) -> int:
    return int(round(value * SCALE))


def _scale_xy(values):
    return tuple(_scale(value) for value in values)


class ScaledDraw:
    """Draw with 1600x900 logical coordinates on a high-resolution canvas."""

    def __init__(self, draw: ImageDraw.ImageDraw) -> None:
        self._draw = draw

    def rectangle(self, xy, **kwargs):
        if "width" in kwargs:
            kwargs["width"] = max(1, _scale(kwargs["width"]))
        return self._draw.rectangle(_scale_xy(xy), **kwargs)

    def rounded_rectangle(self, xy, radius=0, **kwargs):
        if "width" in kwargs:
            kwargs["width"] = max(1, _scale(kwargs["width"]))
        return self._draw.rounded_rectangle(_scale_xy(xy), radius=_scale(radius), **kwargs)

    def text(self, xy, text, **kwargs):
        return self._draw.text(_scale_xy(xy), text, **kwargs)

    def multiline_text(self, xy, text, **kwargs):
        if "spacing" in kwargs:
            kwargs["spacing"] = _scale(kwargs["spacing"])
        return self._draw.multiline_text(_scale_xy(xy), text, **kwargs)

    def line(self, xy, **kwargs):
        if "width" in kwargs:
            kwargs["width"] = max(1, _scale(kwargs["width"]))
        return self._draw.line(_scale_xy(xy), **kwargs)

    def polygon(self, xy, **kwargs):
        points = [_scale_xy(point) for point in xy] if xy and isinstance(xy[0], tuple) else _scale_xy(xy)
        return self._draw.polygon(points, **kwargs)

    def ellipse(self, xy, **kwargs):
        return self._draw.ellipse(_scale_xy(xy), **kwargs)


def drawing(img: Image.Image) -> ScaledDraw:
    return ScaledDraw(ImageDraw.Draw(img))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size * SCALE, index=0)
    return ImageFont.load_default()


F_TITLE = font(54, True)
F_H1 = font(38, True)
F_H2 = font(30, True)
F_BODY = font(25)
F_SMALL = font(21)
F_MONO = font(20)


def run_project_command(args: list[str], log_name: str) -> str:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    for key in ("DEEPSEEK_API_KEY", "OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"):
        env.pop(key, None)
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )
    command = f"$ python3 {' '.join(args)}"
    output = completed.stdout.strip()
    if completed.stderr.strip():
        output = f"{output}\n\n[stderr]\n{completed.stderr.strip()}" if output else completed.stderr.strip()
    text = f"{command}\n{output}\n"
    (RUN_LOGS / log_name).write_text(text, encoding="utf-8")
    return text


def run_json_command(args: list[str], log_name: str) -> dict:
    text = run_project_command(args, log_name)
    json_text = "\n".join(text.splitlines()[1:])
    return json.loads(json_text)


def rounded(draw: ImageDraw.ImageDraw, xy, radius=24, fill=PANEL, outline=LINE, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def wrap(text: str, width: int) -> str:
    return "\n".join(textwrap.wrap(text, width=width, break_long_words=False, replace_whitespace=False))


def draw_wrapped(draw, text, xy, width_chars, fnt, fill=TEXT, spacing=8):
    draw.multiline_text(xy, wrap(text, width_chars), font=fnt, fill=fill, spacing=spacing)


def terminal_lines(text: str, width_chars: int = 92, max_lines: int = 18) -> list[str]:
    lines: list[str] = []
    for line in text.strip().splitlines():
        if not line:
            lines.append("")
            continue
        wrapped = textwrap.wrap(
            line,
            width=width_chars,
            break_long_words=True,
            replace_whitespace=False,
        )
        lines.extend(wrapped or [""])
    if len(lines) > max_lines:
        return lines[: max_lines - 1] + ["..."]
    return lines


def draw_terminal_panel(draw, text: str, xy, title: str = "VS Code Terminal actual run"):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle((x1 + 8, y1 + 10, x2 + 8, y2 + 10), radius=26, fill="#D9E1EA")
    draw.rounded_rectangle((x1, y1, x2, y2), radius=26, fill="#101826", outline="#101826", width=2)
    draw.rounded_rectangle((x1, y1, x2, y1 + 54), radius=26, fill="#1E293B")
    draw.rectangle((x1, y1 + 27, x2, y1 + 54), fill="#1E293B")
    for i, color in enumerate(("#FF5F56", "#FFBD2E", "#27C93F")):
        draw.ellipse((x1 + 26 + i * 28, y1 + 18, x1 + 40 + i * 28, y1 + 32), fill=color)
    draw.text((x1 + 130, y1 + 16), title, font=F_SMALL, fill="#E2E8F0")
    y = y1 + 78
    for line in terminal_lines(text, width_chars=82, max_lines=19):
        color = "#A7F3D0" if line.startswith("$") else "#E5E7EB"
        if line in {"问题", "答案", "来源"} or line.startswith("Context") or line.startswith("Faithfulness") or line.startswith("Answer"):
            color = "#FCA5A5"
        draw.text((x1 + 34, y), line, font=F_MONO, fill=color)
        y += 27


def shadow_card(draw, xy, radius=26, fill=PANEL, outline=LINE):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle((x1 + 8, y1 + 10, x2 + 8, y2 + 10), radius=radius, fill="#D9E1EA")
    rounded(draw, xy, radius=radius, fill=fill, outline=outline, width=2)


def create_hero():
    img = Image.new("RGB", WIDE, INK)
    draw = drawing(img)
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
    draw = drawing(img)
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
    draw = drawing(img)
    draw.text((70, 60), "RAG 数据流：从文档到带引用答案", font=F_TITLE, fill=INK)
    nodes = [
        ("Redis\nDocs", 80, 250, RED),
        ("Clean\nJSONL", 310, 250, TEAL),
        ("Chunking", 540, 250, BLUE),
        ("Embedding\nVector DB", 760, 165, AMBER),
        ("BM25\nIndex", 760, 335, TEAL),
        ("Hybrid\nRetriever", 980, 250, RED),
        ("Light\nReranker", 1190, 250, AMBER),
        ("DeepSeek /\nFallback", 1385, 205, BLUE),
        ("Citation\nCheck", 1385, 355, TEAL),
    ]
    for text, x, y, color in nodes:
        shadow_card(draw, (x, y, x + 165, y + 95), radius=22, fill="#FFFFFF", outline=color)
        draw.text((x + 20, y + 23), text, font=F_SMALL, fill=INK, spacing=4)
    arrows = [
        (245, 298, 310, 298),
        (475, 298, 540, 298),
        (705, 298, 760, 210),
        (705, 298, 760, 380),
        (925, 210, 980, 292),
        (925, 380, 980, 305),
        (1145, 298, 1190, 298),
        (1355, 298, 1385, 252),
        (1355, 298, 1385, 400),
    ]
    for x1, y1, x2, y2 in arrows:
        draw.line((x1, y1, x2, y2), fill=RED, width=5)
        ang = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - 18 * math.cos(ang - 0.5), y2 - 18 * math.sin(ang - 0.5))
        p2 = (x2 - 18 * math.cos(ang + 0.5), y2 - 18 * math.sin(ang + 0.5))
        draw.polygon([(x2, y2), p1, p2], fill=RED)
    shadow_card(draw, (250, 560, 1350, 720), radius=26, fill="#FFFFFF", outline="#DDE5EF")
    draw.text((300, 590), "高级策略", font=F_H2, fill=RED)
    draw.text((300, 648), "Query Rewriting + Hybrid Retrieval + Reranking + Citation Checking", font=F_BODY, fill=INK)
    img.save(OUT / "architecture_flow.png")


def create_inference_result(infer_text: str):
    img = Image.new("RGB", WIDE, BG)
    draw = drawing(img)
    draw.text((70, 55), "真实一键推理运行结果", font=F_TITLE, fill=INK)
    draw.text((72, 125), "由脚本实际执行 infer.py 后生成，原始 stdout 保存到 outputs/run_logs/infer_stdout.txt", font=F_SMALL, fill=MUTED)
    draw_terminal_panel(draw, infer_text, (80, 180, 1515, 805), "VS Code Terminal · infer.py actual stdout")
    img.save(OUT / "inference_result.png")


def create_evaluation_chart(eval_text: str):
    summary = json.loads((ROOT / "outputs/eval_results.json").read_text(encoding="utf-8")).get("summary", {})
    img = Image.new("RGB", WIDE, BG)
    draw = drawing(img)
    draw.text((70, 55), "三维量化评估结果与真实运行输出", font=F_TITLE, fill=INK)
    draw.text((72, 125), "evaluate.py 实际运行后写入 outputs/eval_results.json / csv", font=F_BODY, fill=MUTED)
    metrics = [
        ("Context Relevance", summary["context_relevance"], RED),
        ("Faithfulness", summary["faithfulness"], TEAL),
        ("Answer Relevance", summary["answer_relevance"], AMBER),
    ]
    y = 235
    for label, value, color in metrics:
        draw.text((105, y - 10), label, font=F_H2, fill=INK)
        draw.rounded_rectangle((485, y, 1130, y + 42), radius=20, fill="#E5E7EB")
        draw.rounded_rectangle((485, y, 485 + int(645 * value), y + 42), radius=20, fill=color)
        draw.text((1170, y - 2), f"{value:.4f}", font=F_H2, fill=INK)
        y += 115
    draw_terminal_panel(draw, eval_text, (85, 555, 1515, 850), "VS Code Terminal · evaluate.py actual stdout")
    img.save(OUT / "evaluation_results.png")


def create_build_result(build_text: str):
    img = Image.new("RGB", WIDE, BG)
    draw = drawing(img)
    draw.text((70, 55), "真实索引构建运行结果", font=F_TITLE, fill=INK)
    draw.text((72, 125), "build_index.py 实际运行后生成 chunks.jsonl 与 vectors.jsonl", font=F_BODY, fill=MUTED)
    draw_terminal_panel(draw, build_text, (80, 185, 1515, 790), "VS Code Terminal · build_index.py actual stdout")
    img.save(OUT / "build_index_result.png")


def create_retrieval_scores(payload: dict):
    img = Image.new("RGB", WIDE, BG)
    draw = drawing(img)
    draw.text((70, 55), "检索命中文档与二阶段重排序分数", font=F_TITLE, fill=INK)
    draw.text((72, 125), "数据来自 infer.py --json 的真实输出：score = rerank_score，保留 hybrid/vector/BM25/coverage 便于调试", font=F_SMALL, fill=MUTED)
    headers = ["Rank", "doc_id", "score", "hybrid", "rerank", "coverage"]
    widths = [125, 455, 200, 200, 200, 210]
    x0, y0 = 120, 220
    row_h = 82
    x = x0
    for header, width in zip(headers, widths):
        draw.rectangle((x, y0, x + width, y0 + row_h), fill=RED, outline=LINE)
        draw.text((x + 22, y0 + 26), header, font=F_SMALL, fill="white")
        x += width
    for r, item in enumerate(payload["retrieved_contexts"], start=1):
        y = y0 + r * row_h
        fill = "#FFFFFF" if r % 2 else "#F8FAFC"
        x = x0
        values = [
            str(r),
            item["doc_id"],
            f"{item['score']:.4f}",
            f"{item['combined_score']:.4f}",
            f"{item['rerank_score']:.4f}",
            f"{item['term_coverage']:.4f}",
        ]
        for value, width in zip(values, widths):
            draw.rectangle((x, y, x + width, y + row_h), fill=fill, outline=LINE)
            draw.text((x + 22, y + 26), value, font=F_SMALL, fill=INK)
            x += width
    draw.text((120, 735), "redis:persistence 排名第一，说明 AOF/RDB 问题被正确定位到持久化文档；term_coverage 展示术语覆盖贡献。", font=F_BODY, fill=INK)
    img.save(OUT / "retrieval_scores.png")


def create_retrieval_comparison():
    data = json.loads((ROOT / "outputs/retrieval_comparison.json").read_text(encoding="utf-8"))
    rows = data["summary"]
    img = Image.new("RGB", WIDE, BG)
    draw = drawing(img)
    draw.text((70, 55), "检索策略消融对比", font=F_TITLE, fill=INK)
    draw.text((72, 125), "compare_retrieval.py 真实运行输出：20 条问题，Top-k=5", font=F_BODY, fill=MUTED)
    metrics = [
        ("context_relevance", "Context"),
        ("top1_hit", "Top-1"),
        ("mrr", "MRR"),
    ]
    colors = [RED, TEAL, AMBER]
    x0, y0 = 125, 230
    group_h = 118
    bar_w = 760
    for row_idx, row in enumerate(rows):
        y = y0 + row_idx * group_h
        draw.text((x0, y + 18), row["strategy"], font=F_H2, fill=INK)
        for col_idx, (key, label) in enumerate(metrics):
            value = float(row[key])
            bx = x0 + 380
            by = y + col_idx * 32
            draw.text((bx - 95, by), label, font=F_SMALL, fill=MUTED)
            draw.rounded_rectangle((bx, by + 3, bx + bar_w, by + 25), radius=11, fill="#E5E7EB")
            draw.rounded_rectangle((bx, by + 3, bx + int(bar_w * value), by + 25), radius=11, fill=colors[col_idx])
            draw.text((bx + bar_w + 25, by - 1), f"{value:.4f}", font=F_SMALL, fill=INK)
    shadow_card(draw, (125, 735, 1475, 825), radius=24, fill="#FFFFFF", outline="#DDE5EF")
    draw.text((170, 762), "结论：pure vector 在命令密集场景下最弱；BM25 和 hybrid 更稳，rerank 提供可解释的最终排序字段。", font=F_BODY, fill=INK)
    img.save(OUT / "retrieval_comparison.png")


def main() -> None:
    question = "Redis 的 AOF 和 RDB 持久化有什么区别？"
    build_text = run_project_command(["build_index.py"], "build_index_stdout.txt")
    infer_text = run_project_command(["infer.py", "--question", question], "infer_stdout.txt")
    infer_payload = run_json_command(["infer.py", "--question", question, "--json"], "infer_json_stdout.txt")
    eval_text = run_project_command(["evaluate.py", "--rebuild"], "evaluate_stdout.txt")
    run_project_command(["compare_retrieval.py", "--rebuild"], "retrieval_comparison_stdout.txt")

    create_hero()
    create_kb_overview()
    create_architecture_photo()
    create_build_result(build_text)
    create_inference_result(infer_text)
    create_evaluation_chart(eval_text)
    create_retrieval_scores(infer_payload)
    create_retrieval_comparison()
    print(OUT)


if __name__ == "__main__":
    main()
