#!/usr/bin/env python3
# simple_pdf_extractor.py - 简易 PDF 提取器 (基于 PyMuPDF)
# 用法：py simple_pdf_extractor.py <pdf_file> [--output <output_dir>]

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime

class SimplePDFExtractor:
    """简易 PDF 提取器 - 支持双栏检测"""
    
    def __init__(self):
        pass
    
    def detect_layout(self, page):
        """检测页面布局 (单栏/双栏)"""
        blocks = page.get_text("dict")["blocks"]
        text_blocks = [b for b in blocks if b.get("type") == 0]
        
        if not text_blocks:
            return "single"
        
        # 计算页面中心
        page_width = page.rect.width
        center_x = page_width / 2
        
        # 统计左右栏块数
        left_count = 0
        right_count = 0
        
        for block in text_blocks:
            bbox = block.get("bbox", [0, 0, 0, 0])
            block_center_x = (bbox[0] + bbox[2]) / 2
            
            if block_center_x < center_x:
                left_count += 1
            else:
                right_count += 1
        
        # 如果左右都有内容，判断为双栏
        if left_count >= 3 and right_count >= 3:
            return "double"
        return "single"
    
    def extract_page(self, page, layout="single"):
        """提取单页内容"""
        if layout == "double":
            return self._extract_double_column(page)
        else:
            return page.get_text("text")
    
    def _extract_double_column(self, page):
        """提取双栏 PDF 内容"""
        blocks = page.get_text("dict")["blocks"]
        text_blocks = [b for b in blocks if b.get("type") == 0]
        
        if not text_blocks:
            return ""
        
        # 计算页面中心
        page_width = page.rect.width
        center_x = page_width / 2
        
        # 分离左右栏
        left_blocks = []
        right_blocks = []
        
        for block in text_blocks:
            bbox = block.get("bbox", [0, 0, 0, 0])
            block_center_x = (bbox[0] + bbox[2]) / 2
            
            if block_center_x < center_x:
                left_blocks.append(block)
            else:
                right_blocks.append(block)
        
        # 按 Y 坐标排序
        left_blocks.sort(key=lambda b: b["bbox"][1])
        right_blocks.sort(key=lambda b: b["bbox"][1])
        
        # 提取文本
        left_text = self._blocks_to_text(left_blocks)
        right_text = self._blocks_to_text(right_blocks)
        
        return left_text + "\n\n" + right_text
    
    def _blocks_to_text(self, blocks):
        """将文本块转换为文本"""
        lines = []
        for block in blocks:
            for line in block.get("lines", []):
                line_text = ""
                for span in line.get("spans", []):
                    line_text += span.get("text", "")
                lines.append(line_text)
        return "\n".join(lines)
    
    def extract_full(self, pdf_path, max_pages=0):
        """提取完整 PDF"""
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        if max_pages > 0:
            total_pages = min(total_pages, max_pages)
        
        print(f"📄 处理 PDF: {Path(pdf_path).name}")
        print(f"   总页数：{len(doc)}, 处理：{total_pages} 页")
        
        results = []
        for i in range(total_pages):
            page = doc[i]
            layout = self.detect_layout(page)
            text = self.extract_page(page, layout)
            results.append({
                "page": i + 1,
                "layout": layout,
                "text": text
            })
            print(f"   第 {i+1}/{total_pages} 页 ({layout}栏)...", end="\r")
        
        print(f"\n✅ 处理完成")
        doc.close()
        return results
    
    def to_markdown(self, results):
        """转换为 Markdown 格式"""
        md = []
        
        for page in results:
            md.append(f"<!-- Page {page['page']} ({page['layout']}栏) -->\n")
            md.append(page["text"])
            md.append("\n---\n")
        
        return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="简易 PDF 提取器 (PyMuPDF)")
    parser.add_argument("pdf_file", type=str, help="PDF 文件路径")
    parser.add_argument("--output", "-o", type=str, help="输出目录")
    parser.add_argument("--max-pages", "-m", type=int, default=0, help="最大处理页数 (0=全部)")
    parser.add_argument("--preview", "-p", action="store_true", help="预览前 1000 字符")
    
    args = parser.parse_args()
    
    # 检查文件
    pdf_path = Path(args.pdf_file)
    if not pdf_path.exists():
        print(f"❌ 文件不存在：{pdf_path}")
        sys.exit(1)
    
    # 提取
    extractor = SimplePDFExtractor()
    results = extractor.extract_full(pdf_path, max_pages=args.max_pages)
    
    # 转换为 Markdown
    markdown = extractor.to_markdown(results)
    
    # 输出
    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{pdf_path.stem}.md"
        output_file.write_text(markdown, encoding='utf-8')
        print(f"\n📁 已保存：{output_file}")
    elif args.preview:
        print("\n" + "="*60)
        print("📖 预览 (前 1000 字符):")
        print("="*60)
        print(markdown[:1000])
        if len(markdown) > 1000:
            print(f"\n... (共{len(markdown)}字符)")
    else:
        print(f"\n📊 提取完成：{len(markdown)} 字符")


if __name__ == "__main__":
    main()
