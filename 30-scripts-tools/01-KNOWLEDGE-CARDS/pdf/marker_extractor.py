#!/usr/bin/env python3
# marker_extractor.py - PDF 转 Markdown 提取器 (基于 Marker)
# 用法：py marker_extractor.py <pdf_file> [--output <output_dir>]

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
from pathlib import Path
from datetime import datetime

try:
    from marker.models import load_all_models
    from marker import convert_single_pdf
    MARKER_AVAILABLE = True
except ImportError:
    MARKER_AVAILABLE = False
    print("⚠️ Marker 未安装")
    print("   安装：py -m pip install marker-pdf --user")

def extract_pdf(pdf_path, output_dir=None, max_pages=0):
    """提取 PDF 内容为 Markdown"""

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"❌ 文件不存在：{pdf_path}")
        return None

    print(f"📄 处理 PDF: {pdf_path.name}")
    print(f"   路径：{pdf_path}")

    if not MARKER_AVAILABLE:
        print("❌ Marker 不可用，请先安装")
        return None

    # 加载模型 (首次运行会下载)
    print("🔧 加载模型...")
    try:
        model_refs = load_all_models()
        print("✅ 模型加载完成")
    except Exception as e:
        print(f"⚠️ 模型加载警告：{e}")
        model_refs = None

    # 转换
    print("📝 转换中...")
    try:
        converter = PdfConverter()
        result = converter(str(pdf_path))

        full_text = result.text
        images = result.images
        out_meta = {"n_pages": len(result.pages)}

        print(f"✅ 转换完成")
        print(f"   页数：{out_meta.get('n_pages', 'N/A')}")
        print(f"   字符数：{len(full_text)}")
        print(f"   图片数：{len(images)}")

        # 输出
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / f"{pdf_path.stem}.md"
            output_file.write_text(full_text, encoding='utf-8')
            print(f"\n📁 已保存：{output_file}")

            # 保存元数据
            meta_file = output_path / f"{pdf_path.stem}.meta.json"
            import json
            meta_file.write_text(
                json.dumps(out_meta, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            print(f"📁 元数据：{meta_file}")

        return full_text, images, out_meta

    except Exception as e:
        print(f"❌ 转换失败：{e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    parser = argparse.ArgumentParser(description="PDF 转 Markdown 提取器 (Marker)")
    parser.add_argument("pdf_file", type=str, help="PDF 文件路径")
    parser.add_argument("--output", "-o", type=str, help="输出目录")
    parser.add_argument("--max-pages", "-m", type=int, default=0, help="最大处理页数 (0=全部)")
    parser.add_argument("--preview", "-p", action="store_true", help="预览前 1000 字符")

    args = parser.parse_args()

    result = extract_pdf(args.pdf_file, args.output, args.max_pages)

    if result and args.preview:
        full_text, _, _ = result
        print("\n" + "="*60)
        print("📖 预览 (前 1000 字符):")
        print("="*60)
        print(full_text[:1000])
        if len(full_text) > 1000:
            print(f"\n... (共{len(full_text)}字符)")


if __name__ == "__main__":
    main()
