"""输出模块 - 生成翻译后的PDF或双语文本文件"""
from __future__ import annotations

import os
from fpdf import FPDF

from pdf_translator.fonts import find_cjk_font


class PDFWriter:
    """生成翻译后的PDF文件"""

    def __init__(self, font_path: str | None = None):
        self.font_path = find_cjk_font(font_path)

    def write(
        self,
        pages: dict[int, dict],
        output_path: str,
        bilingual: bool = False,
    ):
        """写入翻译后的PDF

        Args:
            pages: {页码: {"original": 原文, "translated": 译文}}
            output_path: 输出文件路径
            bilingual: 是否输出双语对照
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)

        if self.font_path:
            pdf.add_font("CJK", "", self.font_path, uni=True)
            font_name = "CJK"
        else:
            # 没有中文字体，回退到内置字体（中文会显示为方块）
            font_name = "Helvetica"

        sorted_pages = sorted(pages.keys())
        total = len(sorted_pages)

        for idx, page_num in enumerate(sorted_pages):
            data = pages[page_num]
            pdf.add_page()

            # 页眉：细线 + 页码 (右上角，Apple风格简洁)
            pdf.set_font(font_name, size=8)
            pdf.set_text_color(174, 174, 178)  # Apple tertiaryLabel
            pdf.cell(0, 5, f"Page {page_num + 1}", align="R", new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(229, 229, 234)  # Apple separator
            pdf.set_line_width(0.3)
            pdf.line(pdf.l_margin, pdf.get_y() + 1, pdf.w - pdf.r_margin, pdf.get_y() + 1)
            pdf.ln(8)

            if bilingual and data.get("original"):
                # 原文：较浅灰色，略小字号
                pdf.set_font(font_name, size=9)
                pdf.set_text_color(142, 142, 147)  # Apple secondaryLabel
                self._write_text(pdf, data["original"], line_height=5.5)
                pdf.ln(6)
                # 分隔线：居中短线
                mid_x = pdf.w / 2
                pdf.set_draw_color(209, 209, 214)
                pdf.line(mid_x - 30, pdf.get_y(), mid_x + 30, pdf.get_y())
                pdf.ln(6)

            # 译文：正文黑色
            pdf.set_font(font_name, size=10.5)
            pdf.set_text_color(29, 29, 31)  # Apple label (#1d1d1f)
            translated = data.get("translated", "")
            if translated:
                self._write_text(pdf, translated, line_height=6.5)
            else:
                pdf.set_text_color(174, 174, 178)
                pdf.cell(0, 10, "[No translatable text on this page]",
                         new_x="LMARGIN", new_y="NEXT")

            # 页脚：页码进度
            pdf.set_y(-20)
            pdf.set_font(font_name, size=7)
            pdf.set_text_color(199, 199, 204)
            pdf.cell(0, 5, f"{idx + 1} / {total}", align="C")

        pdf.output(output_path)

    def _write_text(self, pdf: FPDF, text: str, line_height: float = 6):
        """将文本写入PDF（自动换行，段间距优化）"""
        for paragraph in text.split("\n"):
            paragraph = paragraph.strip()
            if paragraph:
                pdf.multi_cell(0, line_height, paragraph)
                pdf.ln(3)


class TextWriter:
    """生成翻译后的纯文本文件"""

    def write(
        self,
        pages: dict[int, dict],
        output_path: str,
        bilingual: bool = False,
    ):
        """写入翻译后的文本文件

        Args:
            pages: {页码: {"original": 原文, "translated": 译文}}
            output_path: 输出文件路径
            bilingual: 是否输出双语对照
        """
        sorted_pages = sorted(pages.keys())

        total = len(sorted_pages)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("=" * 52 + "\n")
            f.write("  PDF Translator | English -> Chinese\n")
            f.write("=" * 52 + "\n\n")

            for idx, page_num in enumerate(sorted_pages):
                data = pages[page_num]
                f.write(f"  [{page_num + 1}]  Page {page_num + 1} of {total}\n")
                f.write(f"  {'- ' * 24}\n\n")

                if bilingual and data.get("original"):
                    f.write("  ORIGINAL:\n\n")
                    for line in data["original"].split("\n"):
                        line = line.strip()
                        if line:
                            f.write(f"    {line}\n")
                    f.write(f"\n  {'~ ' * 20}\n\n")
                    f.write("  TRANSLATED:\n\n")

                translated = data.get("translated", "")
                if translated:
                    for line in translated.split("\n"):
                        line = line.strip()
                        if line:
                            f.write(f"    {line}\n")
                else:
                    f.write("    [No translatable text on this page]\n")

                f.write("\n\n")


def create_writer(output_format: str, font_path: str | None = None):
    """工厂方法：创建输出写入器

    Args:
        output_format: "pdf" 或 "txt"
        font_path: 自定义中文字体路径（仅PDF格式需要）
    """
    if output_format == "pdf":
        return PDFWriter(font_path=font_path)
    elif output_format == "txt":
        return TextWriter()
    else:
        raise ValueError(f"不支持的输出格式: {output_format}，可选: pdf, txt")
