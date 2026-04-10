"""原位翻译模块 - 在原PDF上直接替换文字，保留图片和布局

Typography Design System:
  - H1/H2/H3/Body/Caption classified by font size ratio
  - Color contrast per level (darker = more prominent)
  - 160% line height for readability
  - Empty pages auto-removed
"""
from __future__ import annotations

import fitz  # PyMuPDF

from pdf_translator.fonts import find_cjk_font

# ── Typography Scale ────────────────────────────────────
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
        cjk_fontname = "china-s"
        use_builtin = True
    else:
        cjk_fontname = None
        use_builtin = False

    font_kwargs = {
        "cjk_font": cjk_font,
        "cjk_fontname": cjk_fontname if use_builtin else None,
    }

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
                        flags = span.get("flags", 0)
                        if flags & (1 << 4):
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

        if not text_blocks:
            empty_pages.append(page_num)
            if progress_callback:
                progress_callback(idx + 1, total)
            continue

        # ── Phase 2: Classify levels & translate all blocks ──
        body_size = _estimate_body_size(all_font_sizes)

        translations = []
        for tb in text_blocks:
            level = _classify_level(tb["avg_size"], body_size, tb["is_bold"])
            try:
                translated = translator_fn(tb["text"])
            except Exception:
                translated = None

            translations.append({
                "bbox": tb["bbox"],
                "translated": translated,
                "level": level,
                "avg_size": tb["avg_size"],
                "spans_info": tb["spans_info"],
            })

        # ── Phase 3: Remove original text and insert translations ──
        # Process each block: cover original with white rect, then insert
        for tr in translations:
            if not tr["translated"]:
                continue

            bbox = tr["bbox"]
            level = tr["level"]
            orig_size = tr["avg_size"]

            # Cover original text with white rectangle
            page.draw_rect(bbox, color=None, fill=(1, 1, 1))

            # Color from design system
            color = _LEVEL_COLORS.get(level, _LEVEL_COLORS["body"])

            # Respect original non-black colors
            if tr["spans_info"]:
                raw_color = tr["spans_info"][0].get("color", 0)
                if isinstance(raw_color, int) and raw_color != 0:
                    r = ((raw_color >> 16) & 0xFF) / 255.0
                    g = ((raw_color >> 8) & 0xFF) / 255.0
                    b = (raw_color & 0xFF) / 255.0
                    if (r, g, b) != (0, 0, 0):
                        color = (r, g, b)

            if bilingual:
                insert_y = bbox.y1 + 2
                insert_rect = fitz.Rect(
                    bbox.x0, insert_y, bbox.x1, insert_y + bbox.height
                )
                font_size = max(orig_size * 0.85, 6)
                _insert_text(
                    page, insert_rect, tr["translated"],
                    font_size=font_size, color=(0.18, 0.24, 0.55),
                    **font_kwargs,
                )
            else:
                padding = _TOP_PADDING.get(level, 0)
                render_rect = fitz.Rect(
                    bbox.x0, bbox.y0 + padding, bbox.x1, bbox.y1
                )
                font_size = _calc_font_size(
                    tr["translated"], render_rect, orig_size, body_size, level
                )
                # Expand rect to fit text with 160% line height
                render_rect = _expand_rect(render_rect, font_size, tr["translated"])
                _insert_text(
                    page, render_rect, tr["translated"],
                    font_size=font_size, color=color,
                    **font_kwargs,
                )

        if progress_callback:
            progress_callback(idx + 1, total)

    # Remove empty pages (reverse order)
    if remove_empty and empty_pages:
        for pn in sorted(empty_pages, reverse=True):
            doc.delete_page(pn)

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()
    return {"empty_removed": len(empty_pages)}


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


def _estimate_body_size(font_sizes: list[float]) -> float:
    if not font_sizes:
        return 12.0
    buckets: dict[int, int] = {}
    for s in font_sizes:
        key = round(s)
        buckets[key] = buckets.get(key, 0) + 1
    return float(max(buckets, key=buckets.get))


def _calc_font_size(
    text: str, rect: fitz.Rect, orig_size: float,
    body_size: float, level: str,
) -> float:
    width = rect.width
    if width <= 0:
        return max(orig_size * 0.8, 5)

    target = orig_size * 0.9
    min_ratio = _MIN_SIZE_RATIOS.get(level, 0.8)
    target = max(target, orig_size * min_ratio)

    if level in ("h1", "h2", "h3"):
        target = max(target, body_size)

    return max(target, 5)


def _expand_rect(rect: fitz.Rect, font_size: float, text: str) -> fitz.Rect:
    """Expand rect height to fit text with 160% line height."""
    width = rect.width
    if width <= 0:
        return rect
    chars_per_line = max(int(width / (font_size * 0.72)), 1)
    lines = max(1, (len(text) + chars_per_line - 1) // chars_per_line)
    needed_height = lines * font_size * 1.6 + font_size * 0.4
    if needed_height > rect.height:
        return fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + needed_height)
    return rect


def _insert_text(
    page, rect, text, font_size, color, cjk_font=None, cjk_fontname=None
):
    font_kw = {}
    if cjk_fontname:
        font_kw["fontname"] = cjk_fontname
    elif cjk_font:
        font_kw["fontfile"] = cjk_font
        font_kw["fontname"] = "CJK"

    # For short text (single line), use insert_text (no clipping)
    # For longer text, use insert_textbox (auto-wraps)
    estimated_chars_per_line = max(int(rect.width / (font_size * 0.72)), 1)

    try:
        if len(text) <= estimated_chars_per_line:
            # Single line: insert at top-left of rect, no clipping
            point = fitz.Point(rect.x0, rect.y0 + font_size)
            page.insert_text(point, text,
                             fontsize=font_size, color=color, **font_kw)
        else:
            # Multi-line: use textbox with 160% line height
            expanded = _expand_rect(rect, font_size, text)
            rc = page.insert_textbox(expanded, text,
                                     fontsize=font_size, color=color,
                                     align=0, lineheight=1.6, **font_kw)
            # If still overflows, shrink font
            if rc < 0:
                smaller = max(font_size * 0.75, 4)
                bigger_rect = _expand_rect(rect, smaller, text)
                page.insert_textbox(bigger_rect, text,
                                    fontsize=smaller, color=color,
                                    align=0, lineheight=1.6, **font_kw)
    except Exception:
        try:
            point = fitz.Point(rect.x0, rect.y0 + font_size)
            page.insert_text(point, text,
                             fontsize=max(font_size * 0.7, 4), color=color,
                             **font_kw)
        except Exception:
            pass
