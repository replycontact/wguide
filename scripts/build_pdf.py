#!/usr/bin/env python3
"""Build the printable companion to the offline Human Priest field guide.

Content comes from content/catalog.json and its Markdown files. The generator
does not hard-code chapter prose, so edits to the source guide flow into the
PDF on the next build.
"""

from __future__ import annotations

import html
import json
import re
import sys
import textwrap
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import markdown
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    ListFlowable,
    ListItem,
    LongTable,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "content" / "catalog.json"
OUTPUT_PATH = ROOT / "output" / "pdf" / "wow-forever-human-priest-guide.pdf"

PAGE_W, PAGE_H = letter
PAPER = colors.HexColor("#f4f0e7")
INK = colors.HexColor("#151923")
GOLD = colors.HexColor("#a97838")
VIOLET = colors.HexColor("#7055a5")
MUTED = colors.HexColor("#625f5a")
PALE_GOLD = colors.HexColor("#ece3d2")
PALE_VIOLET = colors.HexColor("#eee9f5")
RULE = colors.HexColor("#d3c9b8")
WHITE = colors.white
DASH_TRANSLATION = str.maketrans({
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-",
    "\u2014": "-", "\u2015": "-", "\u2212": "-",
})

FONT_DIRS = (
    ROOT / "assets" / "fonts",
    Path("/usr/share/fonts/truetype/noto"),
    Path("/usr/share/fonts/truetype/dejavu"),
)


def font_file(name: str) -> str:
    for directory in FONT_DIRS:
        candidate = directory / name
        if candidate.is_file():
            return str(candidate)
    raise FileNotFoundError(f"Required local font not found: {name}")


def register_fonts() -> set[int]:
    fonts = {
        "NotoSerifDisplay": "NotoSerifDisplay-Regular.ttf",
        "NotoSerifDisplay-Bold": "NotoSerifDisplay-Bold.ttf",
        "NotoSerifDisplay-Italic": "NotoSerifDisplay-Italic.ttf",
        "NotoSans": "NotoSans-Regular.ttf",
        "NotoSans-Bold": "NotoSans-Bold.ttf",
        "NotoSans-Italic": "NotoSans-Italic.ttf",
        "NotoSans-BoldItalic": "NotoSans-BoldItalic.ttf",
        "GlyphFallback": "DejaVuSans.ttf",
        "GlyphFallback-Bold": "DejaVuSans-Bold.ttf",
    }
    for face, filename in fonts.items():
        pdfmetrics.registerFont(TTFont(face, font_file(filename)))
    pdfmetrics.registerFontFamily(
        "NotoSans", normal="NotoSans", bold="NotoSans-Bold",
        italic="NotoSans-Italic", boldItalic="NotoSans-BoldItalic"
    )
    pdfmetrics.registerFontFamily(
        "NotoSerifDisplay", normal="NotoSerifDisplay",
        bold="NotoSerifDisplay-Bold", italic="NotoSerifDisplay-Italic",
        boldItalic="NotoSerifDisplay-Bold"
    )
    return set(pdfmetrics.getFont("NotoSans").face.charWidths)


BODY_CMAP = register_fonts()


@dataclass
class Element:
    tag: str
    attrs: dict[str, str] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)


class ElementTreeParser(HTMLParser):
    VOID = {"br", "hr", "img", "meta", "link", "input", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Element("root")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Element(tag.lower(), {k.lower(): (v or "") for k, v in attrs})
        self.stack[-1].children.append(node)
        if tag.lower() not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if data:
            self.stack[-1].children.append(data)


def fallback_markup(text: str) -> str:
    """Escape text while switching to a broad local font for missing glyphs."""
    text = text.translate(DASH_TRANSLATION)
    chunks: list[str] = []
    current_font = "NotoSans"
    run: list[str] = []

    def flush() -> None:
        nonlocal run
        if run:
            chunks.append(html.escape("".join(run), quote=False))
            run = []

    for char in text:
        if ord(char) in BODY_CMAP or char in "\n\t":
            if current_font != "NotoSans":
                flush()
                chunks.append("</font>")
                current_font = "NotoSans"
            run.append(char)
        else:
            if current_font != "GlyphFallback":
                flush()
                if chunks and chunks[-1] == "</font>":
                    pass
                chunks.append('<font name="GlyphFallback">')
                current_font = "GlyphFallback"
            run.append(char)
    flush()
    if current_font != "NotoSans":
        chunks.append("</font>")
    return "".join(chunks)


def inline_markup(children: list[Any], *, code: bool = False) -> str:
    out: list[str] = []
    for child in children:
        if isinstance(child, str):
            out.append(fallback_markup(child))
            continue
        tag = child.tag
        inner = inline_markup(child.children, code=code or tag == "code")
        if tag in {"strong", "b"}:
            out.append(f"<b>{inner}</b>")
        elif tag in {"em", "i"}:
            out.append(f"<i>{inner}</i>")
        elif tag == "del":
            out.append(f"<strike>{inner}</strike>")
        elif tag == "sup":
            out.append(f"<super>{inner}</super>")
        elif tag == "sub":
            out.append(f"<sub>{inner}</sub>")
        elif tag == "br":
            out.append("<br/>")
        elif tag == "a":
            href = child.attrs.get("href", "")
            safe_href = html.escape(href, quote=True)
            if href.startswith("#"):
                safe_href = "#sec-" + re.sub(r"[^A-Za-z0-9_-]", "-", href[1:])[:100]
                out.append(f'<link href="{safe_href}" color="#7055a5">{inner}</link>')
            elif href:
                out.append(f'<link href="{safe_href}" color="#7055a5">{inner}</link>')
            else:
                out.append(inner)
        elif tag == "code":
            out.append(f'<font name="NotoSans" size="8.5" color="#7055a5">{inner}</font>')
        elif tag == "span":
            out.append(inner)
        else:
            out.append(inner)
    return "".join(out).strip() if not any(isinstance(c, str) and c.endswith(" ") for c in children) else "".join(out)


def plain_text(node: Element) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        else:
            parts.append(plain_text(child))
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(text, style)


def get_cell_markup(node: Element) -> str:
    return inline_markup(node.children)


class GuideDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, styles: dict[str, ParagraphStyle]):
        self.styles = styles
        self.current_chapter = "Contents"
        self.chapter_starts: dict[int, str] = {}
        self.previous_chapter_starts: dict[int, str] = {}
        self.toc = TableOfContents()
        self.toc.levelStyles = [styles["TOCChapter"], styles["TOCSection"]]
        self.toc.dotsMinLevel = 0
        super().__init__(
            filename,
            pagesize=letter,
            leftMargin=0.78 * inch,
            rightMargin=0.78 * inch,
            topMargin=0.79 * inch,
            bottomMargin=0.73 * inch,
            title="Light & Shadow: The Human Priest field guide",
            author="WoW Forever Human Priest field guide",
            subject="WoW: Forever Human Priest launch edition, 06 November 2026",
            pageCompression=1,
        )
        cover = Frame(0, 0, PAGE_W, PAGE_H, id="cover", leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0, showBoundary=0)
        body = Frame(self.leftMargin, self.bottomMargin,
                     PAGE_W - self.leftMargin - self.rightMargin,
                     PAGE_H - self.topMargin - self.bottomMargin,
                     id="body", leftPadding=0, rightPadding=0,
                     topPadding=0, bottomPadding=0, showBoundary=0)
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover], onPage=draw_cover),
            PageTemplate(id="Body", frames=[body], onPage=draw_body_page),
        ])

    def beforeDocument(self) -> None:
        self.previous_chapter_starts = self.chapter_starts
        self.chapter_starts = {}
        self.current_chapter = "Contents"

    def afterFlowable(self, flowable: Any) -> None:
        pending = [flowable]
        while pending:
            item = pending.pop(0)
            if isinstance(item, KeepTogether):
                pending[0:0] = list(getattr(item, "_content", []))
                continue
            style_name = getattr(item, "style", None)
            if not isinstance(item, Paragraph) or style_name is None:
                continue
            name = style_name.name
            if name == "ChapterTitle":
                title = item.getPlainText()
                self.current_chapter = title
                self.chapter_starts[self.page] = title
                key = getattr(item, "_bookmark_key", None)
                if key:
                    self.canv.bookmarkPage(key)
                    self.canv.addOutlineEntry(title, key, 0, False)
                    self.notify("TOCEntry", (0, title, self.page, key))
            elif name == "SectionTitle":
                title = item.getPlainText()
                key = getattr(item, "_bookmark_key", None)
                if key:
                    self.canv.bookmarkPage(key)
                    self.notify("TOCEntry", (1, title, self.page, key))


def fit_centered(canvas: Any, text: str, font: str, size: float, max_width: float) -> str:
    while size > 16 and pdfmetrics.stringWidth(text, font, size) > max_width:
        size -= 1
    canvas.setFont(font, size)
    return text


def draw_cover(canvas: Any, doc: GuideDocTemplate) -> None:
    canvas.saveState()
    canvas.setFillColor(INK)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.65)
    canvas.rect(27, 27, PAGE_W - 54, PAGE_H - 54, fill=0, stroke=1)
    canvas.setStrokeColor(colors.HexColor("#544252"))
    canvas.setLineWidth(0.45)
    canvas.rect(34, 34, PAGE_W - 68, PAGE_H - 68, fill=0, stroke=1)

    cx, base, arch_w, arch_h = PAGE_W / 2, 170, 315, 400
    # Pointed cathedral arch, built as nested vector paths.
    for inset, color, width in [(0, GOLD, 1.45), (16, VIOLET, 0.95), (30, colors.HexColor("#9e793e"), 0.65)]:
        x0, x1 = cx - arch_w / 2 + inset, cx + arch_w / 2 - inset
        y0, top = base + inset, base + arch_h - inset
        path = canvas.beginPath()
        path.moveTo(x0, y0)
        path.curveTo(x0, y0 + arch_h * 0.40, cx - arch_w * 0.31, top - 32, cx, top)
        path.curveTo(cx + arch_w * 0.31, top - 32, x1, y0 + arch_h * 0.40, x1, y0)
        canvas.setStrokeColor(color)
        canvas.setLineWidth(width)
        canvas.drawPath(path, stroke=1, fill=0)

    # Stained-glass ribs and small central sun/halo.
    canvas.setStrokeColor(colors.HexColor("#8b7350"))
    canvas.setLineWidth(0.42)
    for side in (-1, 1):
        for fraction in (0.18, 0.33, 0.48, 0.63, 0.78):
            x = cx + side * (arch_w * fraction / 2)
            canvas.line(cx, base + arch_h - 30, x, base + 22)
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1)
    canvas.circle(cx, base + 282, 49, stroke=1, fill=0)
    canvas.setStrokeColor(VIOLET)
    canvas.circle(cx, base + 282, 42, stroke=1, fill=0)
    canvas.setFillColor(colors.HexColor("#dac49d"))
    canvas.circle(cx, base + 282, 3.5, stroke=0, fill=1)
    canvas.line(cx - 13, base + 282, cx + 13, base + 282)
    canvas.line(cx, base + 269, cx, base + 295)

    canvas.setFillColor(GOLD)
    canvas.setFont("NotoSans-Bold", 8.5)
    canvas.drawCentredString(cx, PAGE_H - 83, "WORLD OF WARCRAFT  /  FOREVER")
    canvas.setFillColor(WHITE)
    fit_centered(canvas, "LIGHT & SHADOW", "NotoSerifDisplay-Bold", 38, PAGE_W - 90)
    canvas.drawCentredString(cx, PAGE_H - 137, "LIGHT & SHADOW")
    canvas.setFillColor(colors.HexColor("#e4dcca"))
    canvas.setFont("NotoSans", 14)
    canvas.drawCentredString(cx, PAGE_H - 164, "The Human Priest field guide")
    canvas.setFillColor(colors.HexColor("#b7aa97"))
    canvas.setFont("NotoSans", 8.5)
    canvas.drawCentredString(cx, 94, "LAUNCH EDITION  •  06 NOVEMBER 2026")
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.8)
    canvas.line(cx - 52, 115, cx + 52, 115)
    canvas.restoreState()


def draw_body_page(canvas: Any, doc: GuideDocTemplate) -> None:
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    left, right = doc.leftMargin, PAGE_W - doc.rightMargin
    canvas.line(left, PAGE_H - 0.51 * inch, right, PAGE_H - 0.51 * inch)
    canvas.line(left, 0.48 * inch, right, 0.48 * inch)
    canvas.setFillColor(VIOLET)
    canvas.setFont("NotoSans-Bold", 6.8)
    canvas.drawString(left, PAGE_H - 0.39 * inch, "LIGHT & SHADOW")
    canvas.setFillColor(MUTED)
    canvas.setFont("NotoSans", 6.8)
    running = doc.previous_chapter_starts.get(doc.page, doc.current_chapter)
    if len(running) > 58:
        running = running[:55].rstrip() + "..."
    canvas.drawRightString(right, PAGE_H - 0.39 * inch, running.upper())
    canvas.setFillColor(MUTED)
    canvas.setFont("NotoSans", 7)
    canvas.drawString(left, 0.31 * inch, "HUMAN PRIEST  ·  FOREVER LAUNCH EDITION")
    canvas.drawRightString(right, 0.31 * inch, f"{doc.page:02d}")
    canvas.restoreState()


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()["BodyText"]
    styles = {
        "Body": ParagraphStyle(
            "Body", parent=base, fontName="NotoSans", fontSize=9.7, leading=13.8,
            textColor=INK, spaceAfter=7, alignment=TA_LEFT, splitLongWords=1,
            allowWidows=0, allowOrphans=0,
        ),
        "Deck": ParagraphStyle(
            "Deck", fontName="NotoSans", fontSize=11.2, leading=16,
            textColor=colors.HexColor("#494751"), spaceAfter=16,
            borderColor=GOLD, borderWidth=0, borderPadding=0,
        ),
        "ChapterKicker": ParagraphStyle(
            "ChapterKicker", fontName="NotoSans-Bold", fontSize=7.6, leading=10,
            textColor=GOLD, spaceBefore=2, spaceAfter=8, tracking=1.2,
        ),
        "ChapterTitle": ParagraphStyle(
            "ChapterTitle", fontName="NotoSerifDisplay-Bold", fontSize=27,
            leading=31, textColor=INK, spaceAfter=9, keepWithNext=True,
        ),
        "SectionTitle": ParagraphStyle(
            "SectionTitle", fontName="NotoSerifDisplay-Bold", fontSize=17,
            leading=21, textColor=VIOLET, spaceBefore=17, spaceAfter=7,
            keepWithNext=True,
        ),
        "SubsectionTitle": ParagraphStyle(
            "SubsectionTitle", fontName="NotoSerifDisplay-Bold", fontSize=12.4,
            leading=16, textColor=INK, spaceBefore=12, spaceAfter=5,
            keepWithNext=True,
        ),
        "Small": ParagraphStyle(
            "Small", fontName="NotoSans", fontSize=8, leading=10.5,
            textColor=MUTED, spaceAfter=4,
        ),
        "Callout": ParagraphStyle(
            "Callout", fontName="NotoSans", fontSize=9.4, leading=13.2,
            textColor=INK, leftIndent=9, rightIndent=7, borderColor=GOLD,
            borderWidth=0, borderPadding=8, backColor=PALE_GOLD,
            spaceBefore=5, spaceAfter=9,
        ),
        "TableCell": ParagraphStyle(
            "TableCell", fontName="NotoSans", fontSize=8.1, leading=10.6,
            textColor=INK, spaceAfter=0, splitLongWords=1,
        ),
        "TableHead": ParagraphStyle(
            "TableHead", fontName="NotoSans-Bold", fontSize=8.1, leading=10.6,
            textColor=WHITE, spaceAfter=0, splitLongWords=1,
        ),
        "Code": ParagraphStyle(
            "Code", fontName="NotoSans", fontSize=7.8, leading=9.7,
            textColor=INK, spaceAfter=0, wordWrap="CJK", splitLongWords=1,
        ),
        "TOCTitle": ParagraphStyle(
            "TOCTitle", fontName="NotoSerifDisplay-Bold", fontSize=27,
            leading=31, textColor=INK, spaceAfter=18,
        ),
        "TOCChapter": ParagraphStyle(
            "TOCChapter", fontName="NotoSans-Bold", fontSize=9.3, leading=13,
            leftIndent=0, firstLineIndent=0, textColor=INK, spaceBefore=3,
            rightIndent=22,
        ),
        "TOCSection": ParagraphStyle(
            "TOCSection", fontName="NotoSans", fontSize=8.2, leading=11.5,
            leftIndent=14, firstLineIndent=0, textColor=MUTED,
            rightIndent=22,
        ),
    }
    return styles


def table_flowable(table_node: Element, width: float, styles: dict[str, ParagraphStyle]) -> LongTable | None:
    rows: list[list[Paragraph]] = []
    def table_rows(node: Element) -> list[Element]:
        found: list[Element] = []
        for child in node.children:
            if isinstance(child, Element):
                if child.tag == "tr":
                    found.append(child)
                else:
                    found.extend(table_rows(child))
        return found

    for tr in table_rows(table_node):
        cells = [node for node in tr.children if isinstance(node, Element) and node.tag in {"td", "th"}]
        if not cells:
            continue
        is_header = any(cell.tag == "th" for cell in cells)
        style = styles["TableHead"] if is_header else styles["TableCell"]
        rows.append([p(get_cell_markup(cell) or "&#160;", style) for cell in cells])
    if not rows:
        return None
    ncols = max(len(row) for row in rows)
    if ncols == 1:
        widths = [width]
    else:
        # Markdown tables usually have short, regular cells; even widths avoid
        # measuring an unbreakable URL as a huge minimum column width.
        widths = [width / ncols] * ncols
    normalized = [row + [p("&#160;", styles["TableCell"])] * (ncols - len(row)) for row in rows]
    row_nodes = table_rows(table_node)
    has_header = bool(row_nodes) and any(
        isinstance(node, Element) and node.tag == "th"
        for node in row_nodes[0].children
    )
    table = LongTable(normalized, colWidths=widths, repeatRows=1 if has_header else 0,
                      hAlign="LEFT", splitByRow=1)
    cmds: list[tuple] = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.35, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if has_header:
        cmds.append(("BACKGROUND", (0, 0), (-1, 0), VIOLET))
        for row_idx in range(1, len(normalized)):
            if row_idx % 2 == 0:
                cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#faf8f2")))
    else:
        for row_idx in range(0, len(normalized)):
            if row_idx % 2 == 0:
                cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), colors.HexColor("#faf8f2")))
    table.setStyle(TableStyle(cmds))
    return table


def list_flowable(node: Element, styles: dict[str, ParagraphStyle]) -> ListFlowable:
    ordered = node.tag == "ol"
    items: list[ListItem] = []
    block_tags = {"p", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "pre", "table", "blockquote", "div", "hr"}
    for li in [child for child in node.children if isinstance(child, Element) and child.tag == "li"]:
        flowables: list[Any] = []
        inline_run: list[Any] = []

        def flush_inline() -> None:
            if not inline_run:
                return
            markup = inline_markup(inline_run)
            if markup:
                flowables.append(p(markup, styles["Body"]))
            inline_run.clear()

        for child in li.children:
            if isinstance(child, Element) and child.tag in block_tags:
                flush_inline()
                flowables.extend(node_flowables([child], styles, in_list=True))
            else:
                # Keep labels, emphasis, and their explanation in a single
                # paragraph. Treating each inline node as a block orphaned
                # bold checklist labels at page boundaries.
                inline_run.append(child)
        flush_inline()
        if not flowables:
            flowables = [p("&#160;", styles["Body"])]
        items.append(ListItem(flowables, leftIndent=0))
    start = str(node.attrs.get("start", "1")) if ordered else None
    return ListFlowable(
        items,
        bulletType="1" if ordered else "bullet",
        start=start,
        leftIndent=19,
        bulletFontName="NotoSans",
        bulletFontSize=8.4,
        bulletColor=GOLD if not ordered else INK,
        bulletOffsetY=1,
        spaceAfter=6,
        bulletDedent=7,
    )


def code_flowable(node: Element, width: float, styles: dict[str, ParagraphStyle]) -> LongTable:
    def raw_text(element: Element) -> str:
        return "".join(c if isinstance(c, str) else raw_text(c) for c in element.children)

    raw = raw_text(node)
    raw = html.unescape(raw).strip("\n")
    max_chars = max(28, int(width / 4.5))
    rows = []
    for line in raw.splitlines() or [""]:
        wrapped = textwrap.wrap(line, width=max_chars, replace_whitespace=False,
                                 drop_whitespace=False, break_long_words=True,
                                 break_on_hyphens=False) or [""]
        for segment in wrapped:
            markup = fallback_markup(segment).replace(" ", "&#160;") or "&#160;"
            rows.append([p(markup, styles["Code"])])
    table = LongTable(rows, colWidths=[width], hAlign="LEFT", splitByRow=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eae5db")),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return table


def node_flowables(children: list[Any], styles: dict[str, ParagraphStyle], *, in_list: bool = False) -> list[Any]:
    result: list[Any] = []
    width = PAGE_W - 0.78 * inch * 2
    children = [c for c in children if not (isinstance(c, str) and not c.strip())]
    index = 0
    while index < len(children):
        child = children[index]
        if isinstance(child, str):
            text = child.strip()
            if text:
                result.append(p(fallback_markup(text), styles["Body"]))
            index += 1
            continue
        tag = child.tag
        if tag in {"h1", "script", "style"}:
            index += 1
            continue
        if tag == "h2":
            title = plain_text(child)
            flow = p(inline_markup(child.children), styles["SectionTitle"])
            ident = child.attrs.get("id")
            if ident:
                flow._bookmark_key = "sec-" + re.sub(r"[^A-Za-z0-9_-]", "-", ident)
                flow._bookmark_key = flow._bookmark_key[:100]
            if index + 1 < len(children):
                following = children[index + 1]
                if isinstance(following, Element) and following.tag in {"p", "ul", "ol"}:
                    next_flows = node_flowables([following], styles)
                    if next_flows:
                        result.append(KeepTogether([flow, next_flows[0]]))
                        result.extend(next_flows[1:])
                        index += 2
                        continue
            result.append(flow)
            index += 1
            continue
        if tag in {"h3", "h4", "h5", "h6"}:
            title = inline_markup(child.children)
            result.append(p(title, styles["SubsectionTitle"]))
        elif tag == "p":
            markup = inline_markup(child.children)
            if markup:
                result.append(p(markup, styles["Body"]))
        elif tag in {"ul", "ol"}:
            result.append(list_flowable(child, styles))
        elif tag == "blockquote":
            quoted = node_flowables(child.children, styles)
            for flowable in quoted:
                if isinstance(flowable, Paragraph):
                    flowable.style = ParagraphStyle(
                        f"Quote-{id(flowable)}", parent=styles["Callout"]
                    )
            result.extend(quoted)
        elif tag == "pre":
            result.append(code_flowable(child, width, styles))
            result.append(Spacer(1, 4))
        elif tag == "table":
            table = table_flowable(child, width, styles)
            if table:
                result.append(table)
                result.append(Spacer(1, 8))
        elif tag == "hr":
            rule = Table([[""]], colWidths=[width], rowHeights=[1])
            rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), RULE)]))
            result.extend([Spacer(1, 4), rule, Spacer(1, 9)])
        elif tag == "div":
            class_name = child.attrs.get("class", "")
            nested = node_flowables(child.children, styles)
            if "footnote" in class_name:
                for flowable in nested:
                    if isinstance(flowable, Paragraph):
                        flowable.style = styles["Small"]
            result.extend(nested)
        elif tag == "section":
            result.extend(node_flowables(child.children, styles))
        elif tag == "img":
            alt = child.attrs.get("alt", "")
            if alt:
                result.append(p(f"<i>{fallback_markup(alt)}</i>", styles["Small"]))
        else:
            # Markdown may emit wrappers around otherwise standard blocks.
            result.extend(node_flowables(child.children, styles))
        index += 1
    return result


def markdown_flowables(source: str, styles: dict[str, ParagraphStyle], namespace: str) -> list[Any]:
    source = source.translate(DASH_TRANSLATION)
    md = markdown.Markdown(extensions=["tables", "fenced_code", "footnotes", "toc", "sane_lists"])
    rendered = md.convert(source)
    namespace = re.sub(r"[^A-Za-z0-9_-]", "-", namespace)
    rendered = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{namespace}-{m.group(1)}"', rendered)
    rendered = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{namespace}-{m.group(1)}"', rendered)
    parser = ElementTreeParser()
    parser.feed(rendered)
    return node_flowables(parser.root.children, styles)


def catalog_chapters() -> list[dict[str, Any]]:
    if not CATALOG_PATH.is_file():
        raise FileNotFoundError(f"Missing content catalog: {CATALOG_PATH}")
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise ValueError("content/catalog.json must be a nonempty JSON array")
    seen: set[str] = set()
    chapters = []
    for position, raw in enumerate(data, 1):
        if not isinstance(raw, dict):
            raise ValueError(f"Catalog entry {position} must be an object")
        for field_name in ("id", "title", "markdown"):
            if not raw.get(field_name):
                raise ValueError(f"Catalog entry {position} is missing {field_name!r}")
        chapter = dict(raw)
        chapter_id = re.sub(r"[^A-Za-z0-9_-]", "-", str(chapter["id"]))
        if chapter_id in seen:
            raise ValueError(f"Duplicate chapter id after normalization: {chapter_id}")
        seen.add(chapter_id)
        path = (ROOT / str(chapter["markdown"])).resolve()
        if ROOT not in path.parents:
            raise ValueError(f"Markdown path must stay inside repository: {chapter['markdown']}")
        if not path.is_file():
            raise FileNotFoundError(f"Markdown source not found: {path}")
        chapter["_path"] = path
        chapter["_key"] = "chapter-" + chapter_id
        chapters.append(chapter)
    return chapters


def hex_color(value: Any, fallback: colors.Color) -> colors.Color:
    if not value:
        return fallback
    try:
        return colors.HexColor(str(value))
    except (ValueError, TypeError):
        return fallback


def make_story(chapters: list[dict[str, Any]], styles: dict[str, ParagraphStyle]) -> list[Any]:
    story: list[Any] = [Spacer(1, 1), NextPageTemplate("Body"), PageBreak()]
    story.extend([
        p("CONTENTS", styles["TOCTitle"]),
        p("A field guide to the class, its choices, and its place in Forever.", styles["Deck"]),
    ])
    story.append(Spacer(1, 1))
    # The actual TOC object is bound to the document after construction.
    story.append(PageBreak())
    for number, chapter in enumerate(chapters, 1):
        if number > 1:
            story.append(PageBreak())
        kicker = str(chapter.get("kicker") or f"FIELD NOTE  {number:02d}").strip()
        color = hex_color(chapter.get("color"), GOLD)
        kicker_style = ParagraphStyle(f"Kicker-{number}", parent=styles["ChapterKicker"], textColor=color)
        story.append(p(fallback_markup(kicker.upper()), kicker_style))
        title_flow = p(fallback_markup(str(chapter["title"])), styles["ChapterTitle"])
        title_flow._bookmark_key = chapter["_key"]
        story.append(title_flow)
        description = str(chapter.get("description") or "").strip()
        if description:
            story.append(p(fallback_markup(description), styles["Deck"]))
        source = chapter["_path"].read_text(encoding="utf-8")
        story.extend(markdown_flowables(source, styles, str(chapter["id"])))
    return story


def build(output: Path = OUTPUT_PATH) -> Path:
    chapters = catalog_chapters()
    styles = build_styles()
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = GuideDocTemplate(str(output), styles)
    story = make_story(chapters, styles)
    # Replace the TOC placeholder after creating the document-owned flowable.
    for idx, flowable in enumerate(story):
        if isinstance(flowable, Spacer) and idx >= 2:
            story[idx] = doc.toc
            break
    doc.multiBuild(story)
    return output


def main() -> int:
    try:
        path = build()
    except Exception as exc:
        print(f"PDF build failed: {exc}", file=sys.stderr)
        raise
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
