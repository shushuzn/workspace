#!/usr/bin/env python3
# layoutlm_extractor.py - PDF 布局分析提取器 (LayoutLMv3)
# 用法：py layoutlm_extractor.py <pdf_file> [--output <output_dir>]

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime

try:
    from transformers import LayoutLMv3Processor, LayoutLMv3ForTokenClassification
    LAYOUTLM_AVAILABLE = True
except ImportError:
    LAYOUTLM_AVAILABLE = False
    print("⚠️ LayoutLMv3 未安装，使用基础提取模式")
    print("   安装：pip install layoutlmv3 transformers")

class PDFLayoutExtractor:
    """PDF 布局分析提取器"""

    def __init__(self, use_layoutlm=False):
        self.use_layoutlm = use_layoutlm and LAYOUTLM_AVAILABLE

        if self.use_layoutlm:
            print("🔧 加载 LayoutLMv3 模型...")
            self.processor = LayoutLMv3Processor.from_pretrained("microsoft/layoutlmv3-base")
            self.model = LayoutLMv3ForTokenClassification.from_pretrained("microsoft/layoutlmv3-base")
            print("✅ 模型加载完成")
        else:
            print("📝 使用基础提取模式 (PyMuPDF)")

    def extract_page(self, pdf_path, page_num=0):
        """提取单页内容"""
        doc = fitz.open(pdf_path)

        if page_num >= len(doc):
            raise ValueError(f"页码超出范围 (共{len(doc)}页)")

        page = doc[page_num]

        # 获取页面信息
        page_info = {
            "number": page_num + 1,
            "width": page.rect.width,
            "height": page.rect.height,
            "blocks": []
        }

        # 获取文本块 (按位置排序)
        blocks = page.get_text("dict")["blocks"]

        # 分类处理
        for block in blocks:
            block_type = block.get("type", 0)

            if block_type == 0:  # 文本块
                text_block = self._extract_text_block(block)
                page_info["blocks"].append(text_block)
            elif block_type == 1:  # 图片块
                image_block = self._extract_image_block(block)
                page_info["blocks"].append(image_block)

        doc.close()
        return page_info

    def _extract_text_block(self, block):
        """提取文本块"""
        lines = []
        bbox = block.get("bbox", [0, 0, 0, 0])

        for line in block.get("lines", []):
            line_text = ""
            for span in line.get("spans", []):
                line_text += span.get("text", "")
            lines.append(line_text)

        return {
            "type": "text",
            "bbox": bbox,
            "text": "\n".join(lines),
            "lines": lines
        }

    def _extract_image_block(self, block):
        """提取图片块"""
        return {
            "type": "image",
            "bbox": block.get("bbox", [0, 0, 0, 0]),
            "width": block.get("image", {}).get("width", 0),
            "height": block.get("image", {}).get("height", 0)
        }

    def extract_full(self, pdf_path, max_pages=0):
        """提取完整 PDF"""
        doc = fitz.open(pdf_path)
        total_pages = len(doc)

        if max_pages > 0:
            total_pages = min(total_pages, max_pages)

        print(f"📄 处理 PDF: {pdf_path}")
        print(f"   总页数：{len(doc)}, 处理：{total_pages} 页")

        results = []
        for i in range(total_pages):
            print(f"   第 {i +1}/{total_pages} 页...", end="\r")
            result = self.extract_page(pdf_path, i)
            results.append(result)

        print(f"\n✅ 处理完成")
        return results

    def to_markdown(self, results):
        """转换为 Markdown 格式"""
        md = []

        for page in results:
            md.append(f"<!-- Page {page['number']} -->\n")

            for block in page["blocks"]:
                if block["type"] == "text":
                    md.append(block["text"])
                    md.append("")
                elif block["type"] == "image":
                    md.append(f"![Image]({block['bbox']})")
                    md.append("")

        return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="PDF 布局分析提取器")
    parser.add_argument("pdf_file", type=str, help="PDF 文件路径")
    parser.add_argument("--output", "-o", type=str, help="输出目录")
    parser.add_argument("--max-pages", "-m", type=int, default=0, help="最大处理页数 (0=全部)")
    parser.add_argument("--layoutlm", action="store_true", help="使用 LayoutLMv3 (需先安装)")

    args = parser.parse_args()

    # 检查文件
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"❌ 文件不存在：{pdf_path}")
        sys.exit(1)

    # 创建提取器
    extractor = PDFLayoutExtractor(use_layoutlm=args.layoutlm)

    # 提取
    results = extractor.extract_full(pdf_path, max_pages=args.max_pages)

    # 转换为 Markdown
    markdown = extractor.to_markdown(results)

    # 输出
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{pdf_path.stem}.md"
        output_file.write_text(markdown, encoding="utf-8")
        print(f"\n📁 已保存：{output_file}")
    else:
        print("\n" + "=" *60)
        print(markdown[:2000])  # 只显示前 2000 字符
        if len(markdown) > 2000:
            print(f"\n... (共{len(markdown)}字符，使用 -o 参数保存完整内容)")


if __name__ == "__main__":
    main()
