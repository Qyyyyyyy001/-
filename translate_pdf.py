#!/usr/bin/env python3
"""
PDF翻译工具 - 支持大型PDF（800+页）英译中翻译

功能特性：
  - 支持800+页超大PDF文件
  - 多种翻译后端：Google翻译（免费）、DeepL、Claude
  - 断点续传：中断后可从上次进度继续
  - 批量处理 + 并发翻译，提升速度
  - 进度条实时显示
  - 输出格式：PDF（中文）或TXT双语对照
  - 可指定翻译页面范围

使用示例：
  # 基本用法（Google翻译，输出PDF）
  python translate_pdf.py input.pdf

  # 输出为双语对照文本
  python translate_pdf.py input.pdf -o output.txt --bilingual

  # 只翻译第10-50页
  python translate_pdf.py input.pdf --start 10 --end 50

  # 使用Claude翻译（更高质量）
  python translate_pdf.py input.pdf --backend claude --api-key sk-xxx

  # 本地离线翻译（MarianMT模型，无需API密钥）
  python translate_pdf.py input.pdf --backend marian

  # 本地离线翻译（Argos Translate，更轻量）
  python translate_pdf.py input.pdf --backend argos

  # 本地GPU加速翻译
  python translate_pdf.py input.pdf --backend marian --device cuda

  # 从断点恢复翻译
  python translate_pdf.py input.pdf --resume

  # 4线程并发翻译
  python translate_pdf.py input.pdf --workers 4
"""

import argparse
import os
import sys
import time

from pdf_translator.extractor import get_page_count, extract_pages_batch
from pdf_translator.translator import create_backend, BatchTranslator
from pdf_translator.writer import create_writer
from pdf_translator.checkpoint import Checkpoint


def parse_args():
    parser = argparse.ArgumentParser(
        description="PDF翻译工具 - 大型PDF英译中翻译",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s book.pdf                          # 基本翻译（Google免费）
  %(prog)s book.pdf -o book_cn.txt           # 输出为文本文件
  %(prog)s book.pdf --bilingual              # 双语对照
  %(prog)s book.pdf --start 100 --end 200    # 翻译100-200页
  %(prog)s book.pdf --resume                 # 从断点继续
  %(prog)s book.pdf --backend claude --api-key YOUR_KEY  # 用Claude翻译
  %(prog)s book.pdf --backend marian                     # 本地MarianMT翻译
  %(prog)s book.pdf --backend argos                      # 本地Argos翻译
  %(prog)s book.pdf --backend marian --device cuda       # 本地GPU加速
        """,
    )
    parser.add_argument("input", help="输入PDF文件路径")
    parser.add_argument(
        "-o", "--output",
        help="输出文件路径（默认: input_translated.pdf 或 .txt）",
    )
    parser.add_argument(
        "--format", choices=["pdf", "txt"], default=None,
        help="输出格式（默认根据输出文件名判断，无指定则为txt）",
    )
    parser.add_argument(
        "--backend",
        choices=["google", "deepl", "claude", "marian", "argos"],
        default="google",
        help="翻译后端: google(默认), deepl, claude, marian(本地), argos(本地)",
    )
    parser.add_argument("--api-key", help="翻译API密钥（DeepL/Claude需要）")
    parser.add_argument(
        "--start", type=int, default=1,
        help="起始页码（从1开始，默认: 1）",
    )
    parser.add_argument(
        "--end", type=int, default=None,
        help="结束页码（含，默认: 最后一页）",
    )
    parser.add_argument(
        "--batch-size", type=int, default=10,
        help="每批处理的页数（默认: 10）",
    )
    parser.add_argument(
        "--workers", type=int, default=2,
        help="并发翻译线程数（默认: 2）",
    )
    parser.add_argument(
        "--delay", type=float, default=0.5,
        help="翻译请求间延迟秒数（默认: 0.5）",
    )
    parser.add_argument(
        "--bilingual", action="store_true",
        help="输出双语对照（原文+译文）",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="从上次中断处继续翻译",
    )
    parser.add_argument(
        "--font", help="自定义中文字体文件路径（PDF输出时使用）",
    )
    parser.add_argument(
        "--min-chars", type=int, default=5,
        help="最少字符数：少于此字符的页面跳过翻译（默认: 5）",
    )
    parser.add_argument(
        "--device",
        help="本地模型运行设备: cpu, cuda, mps（仅marian后端有效，默认自动检测）",
    )

    return parser.parse_args()


def determine_output_path(input_path: str, output: str | None, fmt: str | None) -> tuple[str, str]:
    """确定输出文件路径和格式"""
    if output:
        ext = os.path.splitext(output)[1].lower()
        if fmt:
            out_format = fmt
        elif ext == ".pdf":
            out_format = "pdf"
        elif ext in (".txt", ".text"):
            out_format = "txt"
        else:
            out_format = "txt"
        return output, out_format

    base = os.path.splitext(input_path)[0]
    out_format = fmt if fmt else "txt"
    ext = ".pdf" if out_format == "pdf" else ".txt"
    return f"{base}_translated{ext}", out_format


def main():
    args = parse_args()

    # 验证输入文件
    if not os.path.isfile(args.input):
        print(f"错误: 文件不存在 - {args.input}")
        sys.exit(1)

    # 确定输出路径和格式
    output_path, out_format = determine_output_path(args.input, args.output, args.format)

    # 获取PDF信息
    print(f"📄 读取PDF: {args.input}")
    total_pages = get_page_count(args.input)
    print(f"   总页数: {total_pages}")

    # 确定翻译范围（页码：用户输入从1开始，内部从0开始）
    start = max(0, args.start - 1)
    end = min(total_pages, args.end) if args.end else total_pages
    page_range = list(range(start, end))
    print(f"   翻译范围: 第{start + 1}页 - 第{end}页 (共{len(page_range)}页)")

    # 初始化检查点
    checkpoint_path = args.input + ".progress.json"
    checkpoint = Checkpoint(checkpoint_path)
    checkpoint.set_metadata(args.input, total_pages, args.backend)

    # 断点续传：跳过已完成的页面
    if args.resume:
        completed = checkpoint.get_completed_pages()
        done_count = len(completed & set(page_range))
        if done_count > 0:
            print(f"   ✅ 恢复进度: 已完成 {done_count}/{len(page_range)} 页")
            page_range = [p for p in page_range if p not in completed]
            if not page_range:
                print("   所有页面已翻译完成！直接生成输出文件。")
                _generate_output(checkpoint, output_path, out_format, args)
                return
    else:
        checkpoint.clear()
        checkpoint.set_metadata(args.input, total_pages, args.backend)

    print(f"   待翻译: {len(page_range)} 页")

    # 初始化翻译后端
    print(f"🌐 翻译后端: {args.backend}", end="")
    try:
        backend = create_backend(
            args.backend,
            api_key=args.api_key,
            device=getattr(args, "device", None),
        )
        print(f" ({backend.name()})")
    except ValueError as e:
        print(f"\n错误: {e}")
        sys.exit(1)

    translator = BatchTranslator(
        backend=backend,
        workers=args.workers,
        delay=args.delay,
    )

    # 尝试导入tqdm，没有的话用简单进度显示
    try:
        from tqdm import tqdm
        use_tqdm = True
    except ImportError:
        use_tqdm = False

    # 分批翻译
    print(f"🔄 开始翻译 (批大小={args.batch_size}, 线程={args.workers})...\n")
    batches = [
        page_range[i:i + args.batch_size]
        for i in range(0, len(page_range), args.batch_size)
    ]

    if use_tqdm:
        progress = tqdm(total=len(page_range), desc="翻译进度", unit="页")
    else:
        translated_count = 0

    start_time = time.time()
    error_pages = []

    for batch_idx, batch_pages in enumerate(batches):
        # 提取文本
        page_texts = extract_pages_batch(
            args.input, batch_pages[0], batch_pages[-1] + 1
        )

        # 过滤掉文本过少的页面
        translatable = [
            (pn, text) for pn, text in page_texts
            if len(text.strip()) >= args.min_chars
        ]
        skipped = len(page_texts) - len(translatable)

        # 保存跳过的页面
        for pn, text in page_texts:
            if len(text.strip()) < args.min_chars:
                checkpoint.save_page(pn, text, "")

        if translatable:
            try:
                results = translator.translate_batch(translatable)
                for pn, text in translatable:
                    translated = results.get(pn, "")
                    checkpoint.save_page(pn, text, translated)
            except Exception as e:
                error_pages.extend([pn for pn, _ in translatable])
                if not use_tqdm:
                    print(f"\n  ⚠ 第{batch_pages[0]+1}-{batch_pages[-1]+1}页翻译出错: {e}")

        # 定期保存检查点
        checkpoint.save()

        # 更新进度
        if use_tqdm:
            progress.update(len(batch_pages))
        else:
            translated_count += len(batch_pages)
            pct = translated_count / len(page_range) * 100
            elapsed = time.time() - start_time
            speed = translated_count / elapsed if elapsed > 0 else 0
            eta = (len(page_range) - translated_count) / speed if speed > 0 else 0
            print(
                f"\r  进度: {translated_count}/{len(page_range)} "
                f"({pct:.1f}%) | 速度: {speed:.1f}页/秒 | "
                f"预计剩余: {eta:.0f}秒",
                end="", flush=True,
            )

    if use_tqdm:
        progress.close()
    else:
        print()

    elapsed = time.time() - start_time
    print(f"\n✅ 翻译完成! 耗时: {elapsed:.1f}秒")

    if error_pages:
        print(f"  ⚠ {len(error_pages)} 页翻译失败: {error_pages[:20]}{'...' if len(error_pages) > 20 else ''}")

    # 生成输出文件
    _generate_output(checkpoint, output_path, out_format, args)

    # 清理检查点
    checkpoint.clear()


def _generate_output(checkpoint: Checkpoint, output_path: str, out_format: str, args):
    """生成最终输出文件"""
    print(f"\n📝 生成输出文件: {output_path} (格式: {out_format})")

    pages_data = checkpoint.get_all_pages()
    writer = create_writer(out_format, font_path=getattr(args, "font", None))
    writer.write(pages_data, output_path, bilingual=args.bilingual)

    file_size = os.path.getsize(output_path)
    if file_size > 1024 * 1024:
        size_str = f"{file_size / 1024 / 1024:.1f} MB"
    else:
        size_str = f"{file_size / 1024:.1f} KB"

    print(f"   文件大小: {size_str}")
    print(f"\n🎉 完成！输出文件: {output_path}")


if __name__ == "__main__":
    main()
