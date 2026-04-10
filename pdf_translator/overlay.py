"""原位翻译模块 - 在原PDF上直接替换文字，保留图片和布局

Typography Design System (inspired by Apple HIG):
  - Heading levels classified by font size ratio to body
  - Color contrast: headings darker, captions lighter
  - Spacing: headings get extra top padding for visual breathing room
  - Size preservation: translated headings never shrink below body size
"""
from __future__ import annotations

import fitz  # PyMuPDF

from pdf_translator.fonts import find_cjk_font

# ── Typography Scale ────────────────────────────────────
# Ratio thresholds relative to body size for heading classification
_LEVEL_THRESHOLDS = {
    "h1": 1.8,    # Large Title  (e.g. 24pt when body=12pt)
    "h2": 1.45,   # Title        (e.g. 18pt when body=12pt)
    "h3": 1.2,    # Headline     (e.g. 15pt when body=12pt)
    "body": 0.85, # Body text
    "caption": 0,  # Small/caption text (below body)
}

# Color palette per level — (R, G, B) in 0..1 range
# Darker = more visual weight, lighter = less prominent
_LEVEL_COLORS = {
    "h1": (0.067, 0.067, 0.078),   # #111114 — near-black
    "h2": (0.114, 0.114, 0.129),   # #1d1d21 — very dark gray
    "h3": (0.180, 0.180, 0.200),   # #2e2e33 — dark gray
    "body": (0.200, 0.200, 0.220), # #333338 — standard reading gray
    "caption": (0.400, 0.400, 0.430), # #66666e — lighter for captions
}

# Minimum font size ratio (vs original) after fitting text into bbox
_MIN_SIZE_RATIOS = {
    "h1": 0.92,
    "h2": 0.90,
    "h3": 0.88,
    "body": 0.80,
    "caption": 0.75,
}

# Extra top padding (in pt) added above the text box for breathing room
_TOP_PADDING = {
    "h1": 4.0,
    "h2": 3.0,
    "h3": 2.0,
    "body": 0.0,
    "caption": 0.0,
}


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

        # ── Pass 1: Collect all text blocks and font size data ──
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
                        if flags & (1 << 4):  # bit 4 = bold
                            is_bold = True
                if line_parts:
                    block_text_parts.append(" ".join(line_parts))

            original_text = " ".join(block_text_parts).strip()
            if not original_text or len(original_text) < 3:
                continue

            avg_size = (
                sum(s["size"] for s in spans_info) / len(spans_info)
                if spans_info else 12
            )
            all_font_sizes.append(avg_size)

            text_blocks.append({
                "text": original_text,
                "bbox": block["bbox"],
                "spans_info": spans_info,
                "avg_size": avg_size,
                "is_bold": is_bold,
            })

        if not text_blocks:
            empty_pages.append(page_num)
            if progress_callback:
                progress_callback(idx + 1, total)
            continue

        # ── Pass 2: Classify each block's typography level ──
        body_size = _estimate_body_size(all_font_sizes)

        for tb in text_blocks:
            tb["level"] = _classify_level(tb["avg_size"], body_size, tb["is_bold"])

        # ── Pass 3: Translate and render with typography system ──
        for tb in text_blocks:
            try:
                translated = translator_fn(tb["text"])
            except Exception:
                continue
            if not translated:
                continue

            bbox = fitz.Rect(tb["bbox"])
            level = tb["level"]
            orig_size = tb["avg_size"]

            # Apply design-system color
            color = _LEVEL_COLORS.get(level, _LEVEL_COLORS["body"])

            # If the original had a non-black color, respect it for
            # special elements (links, colored headings, etc.)
            if tb["spans_info"]:
                raw_color = tb["spans_info"][0].get("color", 0)
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
                _insert_text_in_rect(
                    page, insert_rect, translated,
                    font_size=font_size,
                    color=(0.18, 0.24, 0.55),  # muted blue
                    **font_kwargs,
                )
            else:
                # Remove original text by redacting it (no white background)
                page.add_redact_annot(bbox)
                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

                # Add breathing room for headings
                padding = _TOP_PADDING.get(level, 0)
                render_rect = fitz.Rect(
                    bbox.x0, bbox.y0 + padding, bbox.x1, bbox.y1
                )

                # Calculate font size — preserve hierarchy
                font_size = _calc_font_size_for_level(
                    translated, render_rect, orig_size, body_size, level
                )

                _insert_text_in_rect(
                    page, render_rect, translated,
                    font_size=font_size,
                    color=color,
                    **font_kwargs,
                )

        if progress_callback:
            progress_callback(idx + 1, total)

    # Remove empty pages (reverse order to preserve indices)
    if remove_empty and empty_pages:
        for pn in sorted(empty_pages, reverse=True):
            doc.delete_page(pn)

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

    return {"empty_removed": len(empty_pages)}


# ── Typography helpers ──────────────────────────────────

def _classify_level(
    font_size: float, body_size: float, is_bold: bool
) -> str:
    """Classify a text block into a typography level based on its
    font size relative to the page's body size."""
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
        # Bold text at body size is treated as a sub-heading
        return "h3" if is_bold else "body"
    return "caption"


def _estimate_body_size(font_sizes: list[float]) -> float:
    """Estimate the body text font size (most common size on the page)."""
    if not font_sizes:
        return 12.0
    buckets: dict[int, int] = {}
    for s in font_sizes:
        key = round(s)
        buckets[key] = buckets.get(key, 0) + 1
    return float(max(buckets, key=buckets.get))


def _calc_font_size_for_level(
    text: str,
    rect: fitz.Rect,
    orig_size: float,
    body_size: float,
    level: str,
) -> float:
    """Calculate the best font size for translated text, respecting
    the typography level hierarchy."""
    width = rect.width
    height = rect.height
    if width <= 0 or height <= 0:
        return max(orig_size * 0.8, 5)

    # Start from original size scaled down slightly for CJK width
    target = orig_size * 0.9

    # Estimate how many lines we need
    chars = len(text)
    chars_per_line = max(int(width / (target * 0.72)), 1)
    lines_needed = max(1, (chars + chars_per_line - 1) // chars_per_line)
    line_height = target * 1.6  # match 160% lineheight
    max_lines = max(int(height / line_height), 1)

    if lines_needed > max_lines:
        # Need to shrink — but respect minimum ratio for this level
        shrink = max_lines / lines_needed
        min_ratio = _MIN_SIZE_RATIOS.get(level, 0.8)
        target = max(orig_size * shrink * 0.9, orig_size * min_ratio)

    # Headings must never be smaller than body text
    if level in ("h1", "h2", "h3"):
        target = max(target, body_size)

    return max(target, 5)


def _insert_text_in_rect(
    page, rect, text, font_size, color, cjk_font=None, cjk_fontname=None
):
    """Insert Chinese text into a rectangle with automatic wrapping."""
    kwargs = {"fontsize": font_size, "color": color, "align": 0, "lineheight": 1.6}
    if cjk_fontname:
        kwargs["fontname"] = cjk_fontname
    elif cjk_font:
        kwargs["fontfile"] = cjk_font
        kwargs["fontname"] = "CJK"

    try:
        page.insert_textbox(rect, text, **kwargs)
    except Exception:
        try:
            kwargs["fontsize"] = max(font_size * 0.7, 4)
            page.insert_textbox(rect, text, **kwargs)
        except Exception:
            pass
