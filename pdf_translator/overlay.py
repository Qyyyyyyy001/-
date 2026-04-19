"""原位翻译模块 - 在原PDF上直接替换文字，保留图片和布局

Typography Design System:
  - H1/H2/H3/Body/Caption classified by font size ratio
  - Color contrast per level (darker = more prominent)
  - 160% line height for readability
  - Empty pages auto-removed

Note: draw_rect white fill covers text visually but does NOT remove
the original text from the PDF content stream. This is a PyMuPDF
limitation — redaction API was tested but causes rendering issues.
"""
from __future__ import annotations

import fitz  # PyMuPDF

from pdf_translator.fonts import find_cjk_font

# ── Typography Constants ────────────────────────────────
_LINE_HEIGHT = 1.6           # 160% line spacing
_CHAR_WIDTH_RATIO = 0.72     # CJK char width ≈ 72% of font size
_MIN_FONT_SIZE = 4

_LEVEL_THRESHOLDS = {
    "h1": 1.8, "h2": 1.45, "h3": 1.2, "body": 0.85, "caption": 0,
}
_LEVEL_COLORS = {
    "h1": (0.067, 0.067, 0.078),
    "h2": (0.114, 0.114, 0.129),
    "h3": (0.180, 0.180, 0.200),
    "body": (0.200, 0.200, 0.220),
    "caption": (0.400, 0.400, 0.430),
}
_MIN_SIZE_RATIOS = {
    "h1": 0.92, "h2": 0.90, "h3": 0.88, "body": 0.80, "caption": 0.75,
}
_TOP_PADDING = {"h1": 4.0, "h2": 3.0, "h3": 2.0, "body": 0.0, "caption": 0.0}


def _chars_per_line(width: float, font_size: float) -> int:
    return max(int(width / (font_size * _CHAR_WIDTH_RATIO)), 1)


def translate_pdf_inplace(
    input_path: str,
    output_path: str,
    translator_fn,
    start_page: int = 0,
    end_page: int | None = None,
    font_path: str | None = None,
    bilingual: bool = False,
    remove_empty: bool = True,
    progress_callback=None,
):
    cjk_font = find_cjk_font(font_path)
    if not cjk_font:
        font_kw = {"fontname": "china-s"}
    else:
        font_kw = {"fontfile": cjk_font, "fontname": "CJK"}

    doc = fitz.open(input_path)
    total_pages = len(doc)
    if end_page is None:
        end_page = total_pages
    end_page = min(end_page, total_pages)

    pages_to_process = list(range(start_page, end_page))
    total = len(pages_to_process)
    empty_pages = []

    for idx, page_num in enumerate(pages_to_process):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        # ── Phase 1: Collect all text blocks ──
        text_blocks = []
        all_font_sizes = []

        for block in blocks:
            if block["type"] != 0:
                continue

            block_text_parts = []
            spans_info = []
            is_bold = False

            for line in block["lines"]:
                line_parts = []
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        line_parts.append(text)
                        spans_info.append(span)
                        if span.get("flags", 0) & (1 << 4):
                            is_bold = True
                if line_parts:
                    block_text_parts.append(" ".join(line_parts))

            original_text = " ".join(block_text_parts).strip()
            if not original_text or len(original_text) < 2:
                continue

            avg_size = (
                sum(s["size"] for s in spans_info) / len(spans_info)
                if spans_info else 12
            )
            all_font_sizes.append(avg_size)

            text_blocks.append({
                "text": original_text,
                "bbox": fitz.Rect(block["bbox"]),
                "spans_info": spans_info,
                "avg_size": avg_size,
                "is_bold": is_bold,
            })

        # A page is "empty" only if it had no text at all originally.
        # Filtering may also drop page numbers/headers but never cause empty.
        had_text = bool(text_blocks)
        text_blocks = _filter_boilerplate(text_blocks, page.rect)

        if not had_text:
            empty_pages.append(page_num)
            if progress_callback:
                progress_callback(idx + 1, total)
            continue

        if not text_blocks:
            # All blocks were boilerplate — skip translation but keep the page
            if progress_callback:
                progress_callback(idx + 1, total)
            continue

        # ── Phase 2: Classify + translate with paragraph context ──
        body_size = _estimate_body_size(all_font_sizes)

        for tb in text_blocks:
            tb["level"] = _classify_level(tb["avg_size"], body_size, tb["is_bold"])
            tb["translated"] = None

        _translate_with_context(text_blocks, translator_fn)

        # ── Phase 3: Cover original text and insert translations ──
        for tb in text_blocks:
            if not tb["translated"]:
                continue

            bbox = tb["bbox"]
            level = tb["level"]
            orig_size = tb["avg_size"]

            page.draw_rect(bbox, color=None, fill=(1, 1, 1))

            color = _get_color(level, tb["spans_info"])

            if bilingual:
                insert_rect = fitz.Rect(
                    bbox.x0, bbox.y1 + 2, bbox.x1, bbox.y1 + 2 + bbox.height
                )
                font_size = max(orig_size * 0.85, 6)
                _insert_text(page, insert_rect, tb["translated"],
                             font_size, (0.18, 0.24, 0.55), font_kw)
            else:
                padding = _TOP_PADDING.get(level, 0)
                render_rect = fitz.Rect(
                    bbox.x0, bbox.y0 + padding, bbox.x1, bbox.y1
                )
                font_size = _calc_font_size(orig_size, body_size, level)
                _insert_text(page, render_rect, tb["translated"],
                             font_size, color, font_kw)

        if progress_callback:
            progress_callback(idx + 1, total)

    # Only remove empty pages if we'd still have at least one page left
    remaining = len(doc) - len(empty_pages)
    if remove_empty and empty_pages and remaining > 0:
        for pn in sorted(empty_pages, reverse=True):
            doc.delete_page(pn)
        removed = len(empty_pages)
    else:
        removed = 0

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return {"empty_removed": removed}


# ── Helpers ─────────────────────────────────────────────

def _classify_level(font_size: float, body_size: float, is_bold: bool) -> str:
    if body_size <= 0:
        return "body"
    ratio = font_size / body_size
    if ratio >= _LEVEL_THRESHOLDS["h1"]:
        return "h1"
    if ratio >= _LEVEL_THRESHOLDS["h2"]:
        return "h2"
    if ratio >= _LEVEL_THRESHOLDS["h3"]:
        return "h3"
    if ratio >= _LEVEL_THRESHOLDS["body"]:
        return "h3" if is_bold else "body"
    return "caption"


_BOILERPLATE_MARGIN = 0.08   # top/bottom 8% of page
_BOILERPLATE_MAX_CHARS = 25  # short text only


def _filter_boilerplate(blocks: list[dict], page_rect) -> list[dict]:
    """Remove page numbers and running headers/footers from edge zones."""
    import re
    top_zone = page_rect.height * _BOILERPLATE_MARGIN
    bot_zone = page_rect.height * (1 - _BOILERPLATE_MARGIN)

    patterns = [
        re.compile(r"^[\s\dIVXivx\-–—·•/|.,]+$"),           # pure digits/roman
        re.compile(r"^\s*page\s*\d+(\s*(of|/)\s*\d+)?\s*$", re.I),  # "Page 1 of 10"
        re.compile(r"^\s*\d+\s*(of|/)\s*\d+\s*$", re.I),     # "1/10"
        re.compile(r"^\s*-\s*\d+\s*-\s*$"),                   # "- 5 -"
    ]

    result = []
    for b in blocks:
        text = b["text"]
        y_center = (b["bbox"].y0 + b["bbox"].y1) / 2
        in_margin = y_center < top_zone or y_center > bot_zone
        is_short = len(text) <= _BOILERPLATE_MAX_CHARS
        if in_margin and is_short and any(p.match(text) for p in patterns):
            continue
        result.append(b)
    return result


def _translate_with_context(blocks: list[dict], translator_fn):
    """Translate each block individually.

    An earlier version attempted to batch adjacent blocks with a separator
    token ("┃BLOCK┃") to give the translator paragraph context, but machine
    translators (Google/DeepL) translate or collapse the separator, making
    it impossible to reliably split the result back. Individual translation
    is slower but correct.
    """
    for tb in blocks:
        try:
            tb["translated"] = translator_fn(tb["text"])
        except Exception:
            tb["translated"] = None


def _estimate_body_size(font_sizes: list[float]) -> float:
    if not font_sizes:
        return 12.0
    buckets: dict[int, int] = {}
    for s in font_sizes:
        key = round(s)
        buckets[key] = buckets.get(key, 0) + 1
    return float(max(buckets, key=buckets.get))


def _get_color(level: str, spans_info: list[dict]) -> tuple:
    """Use design-system color, but preserve original non-black colors."""
    if spans_info:
        raw = spans_info[0].get("color", 0)
        if isinstance(raw, int) and raw != 0:
            r = ((raw >> 16) & 0xFF) / 255.0
            g = ((raw >> 8) & 0xFF) / 255.0
            b = (raw & 0xFF) / 255.0
            if (r, g, b) != (0, 0, 0):
                return (r, g, b)
    return _LEVEL_COLORS.get(level, _LEVEL_COLORS["body"])


def _calc_font_size(orig_size: float, body_size: float, level: str) -> float:
    target = orig_size * 0.9
    min_ratio = _MIN_SIZE_RATIOS.get(level, 0.8)
    target = max(target, orig_size * min_ratio)
    if level in ("h1", "h2", "h3"):
        target = max(target, body_size)
    return max(target, _MIN_FONT_SIZE)


def _expand_rect(rect: fitz.Rect, font_size: float, text: str) -> fitz.Rect:
    """Expand rect height to fit text with current line height."""
    width = rect.width
    if width <= 0:
        return rect
    cpl = _chars_per_line(width, font_size)
    lines = max(1, (len(text) + cpl - 1) // cpl)
    needed = lines * font_size * _LINE_HEIGHT + font_size * 0.4
    if needed > rect.height:
        return fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + needed)
    return rect


def _insert_text(page, rect, text, font_size, color, font_kw):
    """Insert text: single-line uses insert_text (no clip), multi-line uses textbox."""
    cpl = _chars_per_line(rect.width, font_size)

    try:
        if len(text) <= cpl:
            point = fitz.Point(rect.x0, rect.y0 + font_size)
            page.insert_text(point, text,
                             fontsize=font_size, color=color, **font_kw)
        else:
            expanded = _expand_rect(rect, font_size, text)
            rc = page.insert_textbox(
                expanded, text, fontsize=font_size, color=color,
                align=0, lineheight=_LINE_HEIGHT, **font_kw)
            if rc < 0:
                smaller = max(font_size * 0.75, _MIN_FONT_SIZE)
                bigger = _expand_rect(rect, smaller, text)
                page.insert_textbox(
                    bigger, text, fontsize=smaller, color=color,
                    align=0, lineheight=_LINE_HEIGHT, **font_kw)
    except Exception:
        try:
            point = fitz.Point(rect.x0, rect.y0 + font_size)
            page.insert_text(point, text,
                             fontsize=max(font_size * 0.75, _MIN_FONT_SIZE),
                             color=color, **font_kw)
        except Exception:
            pass
