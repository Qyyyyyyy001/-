"""原位翻译模块 - 在原PDF上直接替换文字，保留图片和布局"""
from __future__ import annotations

import re
import fitz  # PyMuPDF

from pdf_translator.fonts import find_cjk_font

_LINE_HEIGHT = 1.6
_CHAR_WIDTH_RATIO = 0.72
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

_PAGE_NUM_PATTERNS = [
    re.compile(r"^[\s\dIVXivx\-–—·•/|.,]+$"),
    re.compile(r"^\s*page\s*\d+(\s*(of|/)\s*\d+)?\s*$", re.I),
    re.compile(r"^\s*\d+\s*(of|/)\s*\d+\s*$", re.I),
    re.compile(r"^\s*-\s*\d+\s*-\s*$"),
]


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
    # Pre-flight: test translator works
    try:
        test = translator_fn("Hello, world! Testing translation.")
        if not test:
            raise RuntimeError("翻译引擎返回空结果，请检查网络连接")
    except Exception as e:
        raise RuntimeError(f"翻译引擎测试失败: {e}") from e

    cjk_font = find_cjk_font(font_path)
    font_kw = {"fontname": "china-s"} if not cjk_font else {
        "fontfile": cjk_font, "fontname": "CJK"
    }

    doc = fitz.open(input_path)
    total_pages = len(doc)
    if end_page is None:
        end_page = total_pages
    end_page = min(end_page, total_pages)

    pages_to_process = list(range(start_page, end_page))
    total = len(pages_to_process)
    empty_pages = []
    stats = {"translated": 0, "failed": 0, "skipped": 0}

    for idx, page_num in enumerate(pages_to_process):
        page = doc[page_num]
        text_blocks = _extract_text_blocks(page)

        if not text_blocks:
            empty_pages.append(page_num)
            if progress_callback:
                progress_callback(idx + 1, total)
            continue

        # Filter page numbers but only if it doesn't remove everything
        filtered = _filter_page_numbers(text_blocks, page.rect)
        if filtered:
            text_blocks = filtered

        body_size = _estimate_body_size([tb["avg_size"] for tb in text_blocks])

        # Classify and translate each block
        for tb in text_blocks:
            tb["level"] = _classify_level(tb["avg_size"], body_size, tb["is_bold"])
            try:
                result = translator_fn(tb["text"])
                if result and result.strip():
                    tb["translated"] = result
                    stats["translated"] += 1
                else:
                    tb["translated"] = None
                    stats["skipped"] += 1
            except Exception:
                tb["translated"] = None
                stats["failed"] += 1

        # Render translations
        for tb in text_blocks:
            if not tb["translated"]:
                continue

            bbox = tb["bbox"]
            page.draw_rect(bbox, color=None, fill=(1, 1, 1))
            color = _get_color(tb["level"], tb["spans_info"])

            if bilingual:
                insert_rect = fitz.Rect(
                    bbox.x0, bbox.y1 + 2, bbox.x1, bbox.y1 + 2 + bbox.height
                )
                font_size = max(tb["avg_size"] * 0.85, 6)
                _insert_text(page, insert_rect, tb["translated"],
                             font_size, (0.18, 0.24, 0.55), font_kw)
            else:
                padding = _TOP_PADDING.get(tb["level"], 0)
                render_rect = fitz.Rect(
                    bbox.x0, bbox.y0 + padding, bbox.x1, bbox.y1
                )
                font_size = _calc_font_size(tb["avg_size"], body_size, tb["level"])
                _insert_text(page, render_rect, tb["translated"],
                             font_size, color, font_kw)

        if progress_callback:
            progress_callback(idx + 1, total)

    # Remove truly empty pages (but keep at least 1)
    remaining = len(doc) - len(empty_pages)
    if remove_empty and empty_pages and remaining > 0:
        for pn in sorted(empty_pages, reverse=True):
            doc.delete_page(pn)
        stats["pages_removed"] = len(empty_pages)

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return stats


# ── Text extraction ─────────────────────────────────────

def _extract_text_blocks(page) -> list[dict]:
    """Extract all text blocks from a page with metadata."""
    blocks = page.get_text("dict")["blocks"]
    result = []

    for block in blocks:
        if block["type"] != 0:
            continue

        parts = []
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
                parts.append(" ".join(line_parts))

        original = " ".join(parts).strip()
        if not original or len(original) < 2:
            continue

        avg_size = (
            sum(s["size"] for s in spans_info) / len(spans_info)
            if spans_info else 12
        )

        result.append({
            "text": original,
            "bbox": fitz.Rect(block["bbox"]),
            "spans_info": spans_info,
            "avg_size": avg_size,
            "is_bold": is_bold,
        })

    return result


def _filter_page_numbers(blocks: list[dict], page_rect) -> list[dict]:
    """Remove page numbers at the edges. Returns filtered list,
    or empty list if everything would be removed."""
    top_zone = page_rect.height * 0.08
    bot_zone = page_rect.height * 0.92

    result = []
    for b in blocks:
        y_center = (b["bbox"].y0 + b["bbox"].y1) / 2
        in_margin = y_center < top_zone or y_center > bot_zone
        is_short = len(b["text"]) <= 25
        if in_margin and is_short and any(p.match(b["text"]) for p in _PAGE_NUM_PATTERNS):
            continue
        result.append(b)
    return result


# ── Typography ──────────────────────────────────────────

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


def _estimate_body_size(font_sizes: list[float]) -> float:
    if not font_sizes:
        return 12.0
    buckets: dict[int, int] = {}
    for s in font_sizes:
        key = round(s)
        buckets[key] = buckets.get(key, 0) + 1
    return float(max(buckets, key=buckets.get))


def _get_color(level: str, spans_info: list[dict]) -> tuple:
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


# ── Text insertion ──────────────────────────────────────

def _expand_rect(rect: fitz.Rect, font_size: float, text_len: int, cpl: int) -> fitz.Rect:
    lines = max(1, (text_len + cpl - 1) // cpl)
    needed = lines * font_size * _LINE_HEIGHT + font_size * 0.4
    if needed > rect.height:
        return fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + needed)
    return rect


def _insert_text(page, rect, text, font_size, color, font_kw):
    cpl = _chars_per_line(rect.width, font_size)

    try:
        if len(text) <= cpl:
            point = fitz.Point(rect.x0, rect.y0 + font_size)
            page.insert_text(point, text,
                             fontsize=font_size, color=color, **font_kw)
        else:
            expanded = _expand_rect(rect, font_size, len(text), cpl)
            rc = page.insert_textbox(
                expanded, text, fontsize=font_size, color=color,
                align=0, lineheight=_LINE_HEIGHT, **font_kw)
            if rc < 0:
                smaller = max(font_size * 0.75, _MIN_FONT_SIZE)
                smaller_cpl = _chars_per_line(rect.width, smaller)
                bigger = _expand_rect(rect, smaller, len(text), smaller_cpl)
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
