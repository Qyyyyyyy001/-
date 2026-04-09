"""输出模块 - 生成翻译后的PDF或双语文本文件"""

import os
from fpdf import FPDF


# 支持中文的字体搜索路径
_FONT_SEARCH_PATHS = [
    # Linux
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc",
    # macOS
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    # Windows
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]


def _find_cjk_font(custom_font: str | None = None) -> str | None:
    """查找系统中可用的中文字体"""
    if custom_font and os.path.isfile(custom_font):
        return custom_font
    for path in _FONT_SEARCH_PATHS:
        if os.path.isfile(path):
            return path
    return None


class PDFWriter:
    """生成翻译后的PDF文件"""

    def __init__(self, font_path: str | None = None):
        self.font_path = _find_cjk_font(font_path)

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

        for page_num in sorted_pages:
            data = pages[page_num]
            pdf.add_page()

            # 页眉
            pdf.set_font(font_name, size=8)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 5, f"--- Page {page_num + 1} ---", align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)

            if bilingual and data.get("original"):
                # 双语模式：先原文后译文
                pdf.set_font(font_name, size=9)
                pdf.set_text_color(100, 100, 100)
                self._write_text(pdf, data["original"])
                pdf.ln(5)
                pdf.set_draw_color(200, 200, 200)
                pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
                pdf.ln(5)

            # 译文
            pdf.set_font(font_name, size=10)
            pdf.set_text_color(0, 0, 0)
            translated = data.get("translated", "")
            if translated:
                self._write_text(pdf, translated)
            else:
                pdf.cell(0, 10, "[本页无可翻译文本]", new_x="LMARGIN", new_y="NEXT")

        pdf.output(output_path)

    def _write_text(self, pdf: FPDF, text: str):
        """将文本写入PDF（自动换行）"""
        for paragraph in text.split("\n"):
            paragraph = paragraph.strip()
            if paragraph:
                pdf.multi_cell(0, 6, paragraph)
                pdf.ln(2)


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

        with open(output_path, "w", encoding="utf-8") as f:
            for page_num in sorted_pages:
                data = pages[page_num]
                f.write(f"{'='*60}\n")
                f.write(f"  第 {page_num + 1} 页\n")
                f.write(f"{'='*60}\n\n")

                if bilingual and data.get("original"):
                    f.write("【原文】\n")
                    f.write(data["original"])
                    f.write("\n\n" + "-" * 40 + "\n\n")
                    f.write("【译文】\n")

                translated = data.get("translated", "")
                f.write(translated if translated else "[本页无可翻译文本]")
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
