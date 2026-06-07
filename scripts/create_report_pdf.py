#!/usr/bin/env python3
"""Render the Markdown report into a PDF file."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "report" / "redis_rag_report.md"
OUTPUT = ROOT / "report" / "redis_rag_report.pdf"


def clean_inline(text: str) -> str:
    text = text.replace("`", "")
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    return text.strip()


def build_styles():
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    styles = getSampleStyleSheet()
    base = {
        "fontName": "STSong-Light",
        "leading": 16,
        "textColor": colors.HexColor("#202124"),
    }
    styles.add(
        ParagraphStyle(
            name="ChineseTitle",
            parent=styles["Title"],
            fontName="STSong-Light",
            fontSize=19,
            leading=25,
            textColor=colors.HexColor("#b3261e"),
            spaceAfter=16,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ChineseHeading",
            parent=styles["Heading2"],
            fontName="STSong-Light",
            fontSize=13.5,
            leading=18,
            textColor=colors.HexColor("#b3261e"),
            spaceBefore=10,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ChineseBody",
            parent=styles["BodyText"],
            **base,
            fontSize=10.2,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ChineseCode",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=8.5,
            leading=11,
            backColor=colors.HexColor("#f3f4f6"),
            borderColor=colors.HexColor("#dddddd"),
            borderWidth=0.5,
            borderPadding=5,
            spaceAfter=6,
        )
    )
    return styles


def parse_markdown(markdown: str):
    styles = build_styles()
    story = []
    lines = markdown.splitlines()
    index = 0
    in_code = False
    code_lines = []
    bullets = []

    def flush_bullets():
        nonlocal bullets
        if bullets:
            story.append(
                ListFlowable(
                    [ListItem(Paragraph(item, styles["ChineseBody"])) for item in bullets],
                    bulletType="bullet",
                    leftIndent=14,
                )
            )
            story.append(Spacer(1, 4))
            bullets = []

    while index < len(lines):
        raw = lines[index]
        line = raw.strip()

        if line.startswith("```"):
            if in_code:
                story.append(Paragraph("<br/>".join(code_lines), styles["ChineseCode"]))
                code_lines = []
                in_code = False
            else:
                flush_bullets()
                in_code = True
            index += 1
            continue

        if in_code:
            code_lines.append(raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            index += 1
            continue

        if not line:
            flush_bullets()
            story.append(Spacer(1, 3))
            index += 1
            continue

        if line.startswith("|") and "|" in line[1:]:
            flush_bullets()
            table_rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                cells = [clean_inline(cell) for cell in lines[index].strip().strip("|").split("|")]
                if not all(set(cell) <= {"-", ":"} for cell in cells):
                    table_rows.append(cells)
                index += 1
            if table_rows:
                table = Table(
                    [[Paragraph(cell, styles["ChineseBody"]) for cell in row] for row in table_rows],
                    hAlign="LEFT",
                )
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f7d7d3")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#202124")),
                            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                story.append(table)
                story.append(Spacer(1, 8))
            continue

        if line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(clean_inline(line[2:]), styles["ChineseTitle"]))
        elif line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(clean_inline(line[3:]), styles["ChineseHeading"]))
        elif line.startswith("- "):
            bullets.append(clean_inline(line[2:]))
        else:
            flush_bullets()
            story.append(Paragraph(clean_inline(line), styles["ChineseBody"]))

        index += 1

    flush_bullets()
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    story = parse_markdown(SOURCE.read_text(encoding="utf-8"))
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="基于 RAG 的 Redis 垂直领域深度问答系统构建",
    )
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()
