"""原位翻译模块 - 在原PDF上直接替换文字，保留图片和布局"""
from __future__ import annotations

import fitz  # PyMuPDF

from pdf_translator.fonts import find_cjk_font

# 标题判定阈值：字号大于正文平均字号的倍数即视为标题
_TITLE_SIZE_RATIO = 1.25


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
    """在原PDF上原位替换英文为中文，保留图片和布局

    Args:
        input_path: 输入PDF路径
        output_path: 输出PDF路径
        translator_fn: 翻译函数
        start_page: 起始页码（从0开始）
        end_page: 结束页码（不含）
        font_path: 自定义中文字体路径
        bilingual: 是否在原文下方追加译文
        remove_empty: 是否删除没有文本内容的页面
        progress_callback: 进度回调 callback(current, total)
    """
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

        # 收集该页所有文本块及其字号
        text_blocks = []
        all_font_sizes = []

        for block in blocks:
            if block["type"] != 0:
                continue

            block_text_parts = []
            spans_info = []

            for line in block["lines"]:
                line_parts = []
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        line_parts.append(text)
                        spans_info.append(span)
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
            })

        # 判断该页是否为空页
        if not text_blocks:
            empty_pages.append(page_num)
            if progress_callback:
                progress_callback(idx + 1, total)
            continue

        # 计算正文基准字号（众数/中位数），用来区分标题与正文
        body_size = _estimate_body_size(all_font_sizes)

        # 逐块翻译并替换
        for tb in text_blocks:
            try:
                translated = translator_fn(tb["text"])
            except Exception:
                continue
            if not translated:
                continue

            bbox = fitz.Rect(tb["bbox"])
            orig_size = tb["avg_size"]
            is_title = orig_size >= body_size * _TITLE_SIZE_RATIO

            # 读取原始颜色
            if tb["spans_info"]:
                orig_color = tb["spans_info"][0].get("color", 0)
            else:
                orig_color = 0

            if isinstance(orig_color, int):
                r = ((orig_color >> 16) & 0xFF) / 255.0
                g = ((orig_color >> 8) & 0xFF) / 255.0
                b = (orig_color & 0xFF) / 255.0
                color = (r, g, b)
            else:
                color = (0, 0, 0)

            if bilingual:
                insert_y = bbox.y1 + 2
                insert_rect = fitz.Rect(
                    bbox.x0, insert_y, bbox.x1, insert_y + bbox.height
                )
                font_size = max(orig_size * 0.85, 6)
                _insert_text_in_rect(
                    page, insert_rect, translated,
                    font_size=font_size,
                    color=(0, 0, 0.6),
                    **font_kwargs,
                )
            else:
                # 白色覆盖原文
                page.draw_rect(bbox, color=None, fill=(1, 1, 1))

                # 保持标题/正文的字号层级
                if is_title:
                    font_size = _calc_font_size(translated, bbox, orig_size)
                    # 标题字号不能小于正文
                    font_size = max(font_size, body_size * 0.95)
                else:
                    font_size = _calc_font_size(translated, bbox, orig_size)

                _insert_text_in_rect(
                    page, bbox, translated,
                    font_size=font_size,
                    color=color,
                    **font_kwargs,
                )

        if progress_callback:
            progress_callback(idx + 1, total)

    # 删除空白页（倒序删除避免索引偏移）
    if remove_empty and empty_pages:
        for pn in sorted(empty_pages, reverse=True):
            doc.delete_page(pn)

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()

    return {"empty_removed": len(empty_pages)}


def _estimate_body_size(font_sizes: list[float]) -> float:
    """估算正文基准字号（取出现频率最高的字号附近值）"""
    if not font_sizes:
        return 12.0
    # 按字号分桶（四舍五入到整数）
    buckets: dict[int, int] = {}
    for s in font_sizes:
        key = round(s)
        buckets[key] = buckets.get(key, 0) + 1
    # 取频率最高的桶
    most_common = max(buckets, key=buckets.get)
    return float(most_common)


def _calc_font_size(text: str, rect: fitz.Rect, orig_size: float) -> float:
    """根据文本长度和可用区域计算合适的字号"""
    width = rect.width
    height = rect.height

    chars = len(text)
    chars_per_line = max(int(width / (orig_size * 0.7)), 1)
    lines_needed = max(1, (chars + chars_per_line - 1) // chars_per_line)

    line_height = orig_size * 1.3
    max_lines = max(int(height / line_height), 1)

    if lines_needed <= max_lines:
        return orig_size * 0.9

    ratio = max_lines / lines_needed
    return max(orig_size * ratio * 0.9, 5)


def _insert_text_in_rect(
    page, rect, text, font_size, color, cjk_font=None, cjk_fontname=None
):
    """在指定矩形区域内插入中文文本"""
    kwargs = {"fontsize": font_size, "color": color, "align": 0}
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
