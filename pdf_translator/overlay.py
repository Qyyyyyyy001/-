"""原位翻译模块 - 在原PDF上直接替换文字，保留图片和布局"""
from __future__ import annotations

import os
import fitz  # PyMuPDF


# 中文字体搜索路径
_CJK_FONT_PATHS = [
    # macOS
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/STSong.ttf",
    # Linux
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    # Windows
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]


def _find_cjk_font(custom_font: str | None = None) -> str | None:
    """查找系统中可用的中文字体文件"""
    if custom_font and os.path.isfile(custom_font):
        return custom_font
    for path in _CJK_FONT_PATHS:
        if os.path.isfile(path):
            return path
    return None


def translate_pdf_inplace(
    input_path: str,
    output_path: str,
    translator_fn,
    start_page: int = 0,
    end_page: int | None = None,
    font_path: str | None = None,
    bilingual: bool = False,
    progress_callback=None,
):
    """在原PDF上原位替换英文为中文，保留图片和布局

    Args:
        input_path: 输入PDF路径
        output_path: 输出PDF路径
        translator_fn: 翻译函数，接收英文字符串返回中文字符串
        start_page: 起始页码（从0开始）
        end_page: 结束页码（不含），None表示到最后一页
        font_path: 自定义中文字体路径
        bilingual: 是否在原文下方追加译文（而非替换）
        progress_callback: 进度回调函数 callback(current, total)
    """
    # 查找中文字体
    cjk_font = _find_cjk_font(font_path)
    if not cjk_font:
        # PyMuPDF内置的CJK字体名称
        cjk_fontname = "china-s"  # 简体中文内置字体
        use_builtin = True
    else:
        cjk_fontname = None
        use_builtin = False

    doc = fitz.open(input_path)
    total_pages = len(doc)
    if end_page is None:
        end_page = total_pages
    end_page = min(end_page, total_pages)

    pages_to_process = list(range(start_page, end_page))
    total = len(pages_to_process)

    for idx, page_num in enumerate(pages_to_process):
        page = doc[page_num]

        # 获取页面上所有文本块的详细信息
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block["type"] != 0:  # 跳过非文本块（图片等保留）
                continue

            # 收集整个块的文本和位置信息
            block_text_parts = []
            spans_info = []

            for line in block["lines"]:
                line_text_parts = []
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        line_text_parts.append(text)
                        spans_info.append(span)
                if line_text_parts:
                    block_text_parts.append(" ".join(line_text_parts))

            original_text = " ".join(block_text_parts).strip()
            if not original_text or len(original_text) < 3:
                continue

            # 翻译
            try:
                translated = translator_fn(original_text)
            except Exception:
                continue

            if not translated:
                continue

            # 获取块的边界框
            bbox = fitz.Rect(block["bbox"])

            # 获取原始字体大小（取第一个span的）
            if spans_info:
                orig_size = spans_info[0]["size"]
                orig_color = spans_info[0].get("color", 0)
            else:
                orig_size = 12
                orig_color = 0

            if bilingual:
                # 双语模式：在原文下方添加译文
                # 在块下方找空间插入译文
                insert_y = bbox.y1 + 2
                insert_rect = fitz.Rect(bbox.x0, insert_y, bbox.x1, insert_y + bbox.height)

                font_size = max(orig_size * 0.85, 6)  # 译文稍小
                _insert_text_in_rect(
                    page, insert_rect, translated,
                    font_size=font_size,
                    color=(0, 0, 0.6),  # 蓝色区分
                    cjk_font=cjk_font,
                    cjk_fontname=cjk_fontname if use_builtin else None,
                )
            else:
                # 替换模式：白色覆盖原文，插入译文
                # 用白色矩形覆盖原文区域
                page.draw_rect(bbox, color=None, fill=(1, 1, 1))

                # 计算合适的字号（中文通常比英文短，但每字更宽）
                font_size = _calc_font_size(translated, bbox, orig_size)

                # 将颜色从整数转为RGB元组
                if isinstance(orig_color, int):
                    r = ((orig_color >> 16) & 0xFF) / 255.0
                    g = ((orig_color >> 8) & 0xFF) / 255.0
                    b = (orig_color & 0xFF) / 255.0
                    color = (r, g, b)
                else:
                    color = (0, 0, 0)

                _insert_text_in_rect(
                    page, bbox, translated,
                    font_size=font_size,
                    color=color,
                    cjk_font=cjk_font,
                    cjk_fontname=cjk_fontname if use_builtin else None,
                )

        if progress_callback:
            progress_callback(idx + 1, total)

    doc.save(output_path, garbage=4, deflate=True)
    doc.close()


def _calc_font_size(text: str, rect: fitz.Rect, orig_size: float) -> float:
    """根据文本长度和可用区域计算合适的字号"""
    width = rect.width
    height = rect.height

    # 估算：中文每字大约占 font_size 宽度
    chars = len(text)
    chars_per_line = max(int(width / (orig_size * 0.7)), 1)
    lines_needed = max(1, (chars + chars_per_line - 1) // chars_per_line)

    # 如果行数太多放不下，缩小字号
    line_height = orig_size * 1.3
    max_lines = max(int(height / line_height), 1)

    if lines_needed <= max_lines:
        return orig_size * 0.9  # 稍微缩小以适应中文

    # 需要缩小字号
    ratio = max_lines / lines_needed
    return max(orig_size * ratio * 0.9, 5)  # 最小5pt


def _insert_text_in_rect(
    page, rect, text, font_size, color, cjk_font=None, cjk_fontname=None
):
    """在指定矩形区域内插入中文文本（自动换行）"""
    try:
        if cjk_fontname:
            # 使用PyMuPDF内置CJK字体
            rc = page.insert_textbox(
                rect, text,
                fontsize=font_size,
                fontname=cjk_fontname,
                color=color,
                align=0,  # 左对齐
            )
        elif cjk_font:
            # 使用外部字体文件
            rc = page.insert_textbox(
                rect, text,
                fontsize=font_size,
                fontfile=cjk_font,
                fontname="CJK",
                color=color,
                align=0,
            )
        else:
            # 回退：无中文字体
            page.insert_textbox(
                rect, text,
                fontsize=font_size,
                color=color,
                align=0,
            )

    except Exception:
        # 如果插入失败，尝试更小的字号
        try:
            smaller = max(font_size * 0.7, 4)
            if cjk_fontname:
                page.insert_textbox(
                    rect, text,
                    fontsize=smaller, fontname=cjk_fontname, color=color,
                )
            elif cjk_font:
                page.insert_textbox(
                    rect, text,
                    fontsize=smaller, fontfile=cjk_font, fontname="CJK", color=color,
                )
        except Exception:
            pass  # 实在放不下就跳过
