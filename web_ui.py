#!/usr/bin/env python3
"""
PDF翻译工具 - Web 界面
启动: python web_ui.py
浏览器打开: http://localhost:7860
"""

import os
import tempfile
import time
import traceback

import gradio as gr

from pdf_translator.extractor import get_page_count, extract_pages_batch
from pdf_translator.translator import create_backend, BatchTranslator
from pdf_translator.writer import create_writer
from pdf_translator.checkpoint import Checkpoint


def get_pdf_info(file_path):
    """上传PDF后显示基本信息"""
    if file_path is None:
        return "请上传PDF文件", gr.update(maximum=1, value=1), gr.update(maximum=1, value=1)
    try:
        total = get_page_count(file_path)
        info = f"总页数: {total} 页  |  文件大小: {os.path.getsize(file_path) / 1024 / 1024:.1f} MB"
        return info, gr.update(maximum=total, value=1), gr.update(maximum=total, value=total)
    except Exception as e:
        return f"读取PDF失败: {e}", gr.update(), gr.update()


def translate_pdf(
    file_path,
    backend,
    api_key,
    start_page,
    end_page,
    output_format,
    bilingual,
    workers,
    batch_size,
    progress=gr.Progress(),
):
    """核心翻译函数"""
    if file_path is None:
        raise gr.Error("请先上传PDF文件")

    pdf_path = file_path
    total_pages = get_page_count(pdf_path)

    # 页码范围
    start = max(0, int(start_page) - 1)
    end = min(total_pages, int(end_page))
    page_range = list(range(start, end))
    if not page_range:
        raise gr.Error(f"无效的页码范围: {start_page}-{end_page}")

    # 创建翻译后端
    progress(0, desc="初始化翻译引擎...")
    try:
        engine = create_backend(backend, api_key=api_key or None)
    except Exception as e:
        raise gr.Error(f"初始化翻译后端失败: {e}")

    translator = BatchTranslator(
        backend=engine,
        workers=int(workers),
        delay=0.3 if backend == "google" else 0.0,
    )

    # 临时检查点
    tmp_dir = tempfile.mkdtemp()
    ckpt_path = os.path.join(tmp_dir, "progress.json")
    checkpoint = Checkpoint(ckpt_path)
    checkpoint.set_metadata(pdf_path, total_pages, backend)

    # 分批翻译
    bs = int(batch_size)
    batches = [page_range[i:i + bs] for i in range(0, len(page_range), bs)]
    total_to_translate = len(page_range)
    done = 0
    errors = []
    start_time = time.time()

    for batch_pages in batches:
        # 提取文本
        page_texts = extract_pages_batch(pdf_path, batch_pages[0], batch_pages[-1] + 1)

        translatable = [(pn, text) for pn, text in page_texts if len(text.strip()) >= 5]

        # 保存空白页
        for pn, text in page_texts:
            if len(text.strip()) < 5:
                checkpoint.save_page(pn, text, "")

        if translatable:
            try:
                results = translator.translate_batch(translatable)
                for pn, text in translatable:
                    checkpoint.save_page(pn, text, results.get(pn, ""))
            except Exception as e:
                errors.extend([pn + 1 for pn, _ in translatable])
                for pn, text in translatable:
                    checkpoint.save_page(pn, text, f"[翻译失败: {e}]")

        checkpoint.save()
        done += len(batch_pages)
        elapsed = time.time() - start_time
        speed = done / elapsed if elapsed > 0 else 0
        eta = (total_to_translate - done) / speed if speed > 0 else 0
        progress(
            done / total_to_translate,
            desc=f"翻译中... {done}/{total_to_translate} 页 | {speed:.1f}页/秒 | 剩余 {eta:.0f}秒",
        )

    # 生成输出文件
    progress(0.95, desc="生成输出文件...")
    ext = ".pdf" if output_format == "PDF" else ".txt"
    output_path = os.path.join(tmp_dir, f"translated{ext}")

    fmt = "pdf" if output_format == "PDF" else "txt"
    writer = create_writer(fmt)
    pages_data = checkpoint.get_all_pages()
    writer.write(pages_data, output_path, bilingual=bilingual)

    elapsed = time.time() - start_time
    file_size = os.path.getsize(output_path)
    size_str = f"{file_size / 1024 / 1024:.1f} MB" if file_size > 1024 * 1024 else f"{file_size / 1024:.1f} KB"

    # 预览前几页
    preview_lines = []
    sorted_pages = sorted(pages_data.keys())[:3]
    for pn in sorted_pages:
        data = pages_data[pn]
        translated = data.get("translated", "")
        snippet = translated[:300] + "..." if len(translated) > 300 else translated
        preview_lines.append(f"--- 第 {pn + 1} 页 ---\n{snippet}")
    preview = "\n\n".join(preview_lines) if preview_lines else "无预览内容"

    error_msg = f"\n失败页: {errors[:20]}" if errors else ""
    summary = (
        f"翻译完成!\n"
        f"翻译页数: {total_to_translate} 页\n"
        f"耗时: {elapsed:.1f} 秒 ({speed:.1f} 页/秒)\n"
        f"文件大小: {size_str}\n"
        f"翻译引擎: {engine.name()}"
        f"{error_msg}"
    )

    progress(1.0, desc="完成!")
    return output_path, summary, preview


def build_ui():
    with gr.Blocks(title="PDF翻译工具 - 英译中") as app:
        gr.Markdown("# PDF 翻译工具\n**支持大型PDF (800+页) 英文翻译为中文**")

        with gr.Row():
            # ---- 左栏：设置 ----
            with gr.Column(scale=1):
                file_input = gr.File(
                    label="上传PDF文件",
                    file_types=[".pdf"],
                    type="filepath",
                )
                pdf_info = gr.Textbox(label="文件信息", interactive=False)

                gr.Markdown("### 翻译设置")
                backend = gr.Dropdown(
                    choices=[
                        ("Google翻译 (免费联网)", "google"),
                        ("MarianMT (本地离线)", "marian"),
                        ("Argos Translate (本地轻量)", "argos"),
                        ("DeepL (需API密钥)", "deepl"),
                        ("Claude (需API密钥)", "claude"),
                    ],
                    value="google",
                    label="翻译引擎",
                )
                api_key = gr.Textbox(
                    label="API密钥 (DeepL/Claude需要，其他留空)",
                    type="password",
                    placeholder="留空 = 不需要",
                )

                gr.Markdown("### 页面范围")
                with gr.Row():
                    start_page = gr.Number(value=1, label="起始页", minimum=1, precision=0)
                    end_page = gr.Number(value=1, label="结束页", minimum=1, precision=0)

                gr.Markdown("### 输出选项")
                output_format = gr.Radio(
                    choices=["TXT", "PDF"],
                    value="TXT",
                    label="输出格式",
                )
                bilingual = gr.Checkbox(label="双语对照 (原文 + 译文)", value=False)

                gr.Markdown("### 高级选项")
                with gr.Row():
                    workers = gr.Slider(
                        minimum=1, maximum=8, value=2, step=1,
                        label="并发线程数",
                    )
                    batch_size = gr.Slider(
                        minimum=1, maximum=50, value=10, step=1,
                        label="每批页数",
                    )

                translate_btn = gr.Button("开始翻译", variant="primary", size="lg")

            # ---- 右栏：结果 ----
            with gr.Column(scale=1):
                output_file = gr.File(label="下载翻译文件")
                summary = gr.Textbox(label="翻译摘要", lines=6, interactive=False)
                preview = gr.Textbox(label="译文预览 (前3页)", lines=15, interactive=False)

        # ---- 事件绑定 ----
        file_input.change(
            fn=get_pdf_info,
            inputs=[file_input],
            outputs=[pdf_info, start_page, end_page],
        )

        translate_btn.click(
            fn=translate_pdf,
            inputs=[
                file_input, backend, api_key,
                start_page, end_page,
                output_format, bilingual,
                workers, batch_size,
            ],
            outputs=[output_file, summary, preview],
        )

    return app


if __name__ == "__main__":
    app = build_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        theme=gr.themes.Soft(),
    )
