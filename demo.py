#!/usr/bin/env python3
"""
PDF翻译工具 - 交互式演示
在终端中交互式地选择PDF、翻译引擎、页面范围并执行翻译。
"""

import os
import sys
import glob
import time

from pdf_translator.extractor import get_page_count, extract_pages_batch
from pdf_translator.translator import create_backend, BatchTranslator
from pdf_translator.writer import create_writer
from pdf_translator.checkpoint import Checkpoint


def find_pdfs(directory="."):
    """在当前目录查找所有PDF文件"""
    patterns = [
        os.path.join(directory, "*.pdf"),
        os.path.join(directory, "**/*.pdf"),
    ]
    files = []
    for p in patterns:
        files.extend(glob.glob(p, recursive=True))
    return sorted(set(files))


def prompt_choice(prompt, options, default=0):
    """交互式选择"""
    print(f"\n{prompt}")
    for i, (label, _) in enumerate(options):
        marker = " *" if i == default else ""
        print(f"  [{i+1}] {label}{marker}")
    while True:
        raw = input(f"请选择 [1-{len(options)}] (默认={default+1}): ").strip()
        if not raw:
            return options[default][1]
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx][1]
        except ValueError:
            pass
        print("  无效选择，请重试")


def prompt_int(prompt, default, min_val=1, max_val=None):
    """交互式输入整数"""
    while True:
        raw = input(f"{prompt} (默认={default}): ").strip()
        if not raw:
            return default
        try:
            val = int(raw)
            if val < min_val:
                print(f"  最小值为 {min_val}")
                continue
            if max_val and val > max_val:
                print(f"  最大值为 {max_val}")
                continue
            return val
        except ValueError:
            print("  请输入数字")


def prompt_yn(prompt, default=True):
    """交互式确认"""
    suffix = "[Y/n]" if default else "[y/N]"
    raw = input(f"{prompt} {suffix}: ").strip().lower()
    if not raw:
        return default
    return raw in ("y", "yes", "是")


def run_demo():
    print("=" * 50)
    print("  PDF 翻译工具 - 交互式演示")
    print("  支持大型PDF (800+页) 英译中")
    print("=" * 50)

    # 1. 选择PDF文件
    pdfs = find_pdfs()
    if pdfs:
        print(f"\n找到 {len(pdfs)} 个PDF文件:")
        for i, f in enumerate(pdfs[:10]):
            size = os.path.getsize(f) / 1024 / 1024
            print(f"  [{i+1}] {f} ({size:.1f} MB)")
        raw = input("\n选择文件编号，或输入PDF路径: ").strip()
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(pdfs):
                pdf_path = pdfs[idx]
            else:
                pdf_path = raw
        except ValueError:
            pdf_path = raw
    else:
        pdf_path = input("\n请输入PDF文件路径: ").strip()

    if not os.path.isfile(pdf_path):
        print(f"错误: 文件不存在 - {pdf_path}")
        sys.exit(1)

    total_pages = get_page_count(pdf_path)
    file_size = os.path.getsize(pdf_path) / 1024 / 1024
    print(f"\n文件: {pdf_path}")
    print(f"页数: {total_pages} 页  |  大小: {file_size:.1f} MB")

    # 2. 选择翻译引擎
    backend_name = prompt_choice(
        "选择翻译引擎:",
        [
            ("Google翻译 (免费，需联网)", "google"),
            ("MarianMT (本地离线，需安装transformers+torch)", "marian"),
            ("Argos Translate (本地轻量，需安装argostranslate)", "argos"),
            ("DeepL (需API密钥)", "deepl"),
            ("Claude (需API密钥，质量最高)", "claude"),
        ],
        default=0,
    )

    api_key = None
    if backend_name in ("deepl", "claude"):
        api_key = input("请输入API密钥: ").strip()
        if not api_key:
            print("错误: 该翻译引擎需要API密钥")
            sys.exit(1)

    # 3. 页面范围
    start = prompt_int("起始页", default=1, min_val=1, max_val=total_pages)
    end = prompt_int("结束页", default=total_pages, min_val=start, max_val=total_pages)

    # 4. 输出选项
    out_format = prompt_choice(
        "输出格式:",
        [("TXT 文本文件 (推荐)", "txt"), ("PDF 文件", "pdf")],
        default=0,
    )
    bilingual = prompt_yn("是否输出双语对照 (原文+译文)?", default=False)

    # 5. 确认
    ext = ".txt" if out_format == "txt" else ".pdf"
    base = os.path.splitext(pdf_path)[0]
    output_path = f"{base}_translated{ext}"

    print(f"\n{'─' * 50}")
    print(f"  文件:   {pdf_path}")
    print(f"  引擎:   {backend_name}")
    print(f"  范围:   第{start}页 - 第{end}页 (共{end - start + 1}页)")
    print(f"  输出:   {output_path}")
    print(f"  双语:   {'是' if bilingual else '否'}")
    print(f"{'─' * 50}")

    if not prompt_yn("\n确认开始翻译?", default=True):
        print("已取消")
        return

    # 6. 执行翻译
    print(f"\n初始化翻译引擎 [{backend_name}]...")
    try:
        engine = create_backend(backend_name, api_key=api_key)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
    print(f"引擎: {engine.name()}")

    translator = BatchTranslator(
        backend=engine,
        workers=2,
        delay=0.3 if backend_name == "google" else 0.0,
    )

    # 检查点
    ckpt_path = pdf_path + ".progress.json"
    checkpoint = Checkpoint(ckpt_path)
    checkpoint.set_metadata(pdf_path, total_pages, backend_name)

    page_range = list(range(start - 1, end))
    batch_size = 10
    batches = [page_range[i:i + batch_size] for i in range(0, len(page_range), batch_size)]

    done = 0
    total = len(page_range)
    errors = []
    start_time = time.time()

    print(f"\n开始翻译 {total} 页...\n")

    for batch_pages in batches:
        page_texts = extract_pages_batch(pdf_path, batch_pages[0], batch_pages[-1] + 1)

        translatable = [(pn, text) for pn, text in page_texts if len(text.strip()) >= 5]
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
        eta = (total - done) / speed if speed > 0 else 0
        bar_len = 30
        filled = int(bar_len * done / total)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(
            f"\r  [{bar}] {done}/{total} ({done*100//total}%) "
            f"| {speed:.1f}页/秒 | 剩余{eta:.0f}秒",
            end="", flush=True,
        )

    elapsed = time.time() - start_time
    print(f"\n\n翻译完成! 耗时 {elapsed:.1f} 秒")

    if errors:
        print(f"  {len(errors)} 页翻译失败: {errors[:20]}")

    # 7. 生成输出
    print(f"\n生成输出文件: {output_path}")
    writer = create_writer(out_format)
    pages_data = checkpoint.get_all_pages()
    writer.write(pages_data, output_path, bilingual=bilingual)
    checkpoint.clear()

    file_size = os.path.getsize(output_path)
    size_str = f"{file_size / 1024 / 1024:.1f} MB" if file_size > 1024 * 1024 else f"{file_size / 1024:.1f} KB"
    print(f"文件大小: {size_str}")

    # 8. 预览
    print(f"\n{'═' * 50}")
    print("  译文预览 (前2页)")
    print(f"{'═' * 50}")
    sorted_pages = sorted(pages_data.keys())[:2]
    for pn in sorted_pages:
        translated = pages_data[pn].get("translated", "")
        snippet = translated[:500] + "..." if len(translated) > 500 else translated
        print(f"\n--- 第 {pn + 1} 页 ---")
        print(snippet if snippet else "[无文本]")

    print(f"\n完成! 输出文件: {output_path}")


if __name__ == "__main__":
    run_demo()
