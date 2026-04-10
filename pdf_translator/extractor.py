"""PDF文本提取模块 - 使用PyMuPDF逐页提取文本，内存友好"""
from __future__ import annotations

import fitz  # PyMuPDF


def get_page_count(pdf_path: str) -> int:
    """获取PDF总页数"""
    with fitz.open(pdf_path) as doc:
        return len(doc)


def extract_page_text(pdf_path: str, page_num: int) -> str:
    """提取单页文本内容

    Args:
        pdf_path: PDF文件路径
        page_num: 页码（从0开始）

    Returns:
        该页的文本内容
    """
    with fitz.open(pdf_path) as doc:
        page = doc[page_num]
        return page.get_text("text")


def extract_pages_batch(pdf_path: str, start: int, end: int) -> list[tuple[int, str]]:
    """批量提取多页文本（减少文件打开次数）

    Args:
        pdf_path: PDF文件路径
        start: 起始页码（含）
        end: 结束页码（不含）

    Returns:
        [(页码, 文本内容), ...] 的列表
    """
    results = []
    with fitz.open(pdf_path) as doc:
        end = min(end, len(doc))
        for i in range(start, end):
            text = doc[i].get_text("text")
            results.append((i, text))
    return results


def extract_page_blocks(pdf_path: str, page_num: int) -> list[dict]:
    """提取单页的文本块（保留布局信息）

    Args:
        pdf_path: PDF文件路径
        page_num: 页码（从0开始）

    Returns:
        文本块列表，每个块包含 bbox, text, font_size 等信息
    """
    blocks = []
    with fitz.open(pdf_path) as doc:
        page = doc[page_num]
        block_list = page.get_text("dict")["blocks"]
        for block in block_list:
            if block["type"] == 0:  # 文本块
                text_parts = []
                font_sizes = []
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_parts.append(span["text"])
                        font_sizes.append(span["size"])
                text = " ".join(text_parts).strip()
                if text:
                    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
                    blocks.append({
                        "bbox": block["bbox"],
                        "text": text,
                        "font_size": avg_font_size,
                    })
    return blocks
