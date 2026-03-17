#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 元数据提取器
从 PDF 文件提取结构化元数据，用于 P-Note 自动填充
"""

import subprocess
import json
import re
from pathlib import Path

# 配置
PDF_DIR = Path(r"D:\obsidian\Vault\Arxiv\PDF")
OUTPUT_DIR = Path(r"D:\obsidian\Vault\Arxiv\metadata")

def extract_metadata_with_pdftotext(pdf_path):
    """使用 pdftotext 提取 PDF 文本"""
    try:
        result = subprocess.run(
            ['pdftotext', '-layout', str(pdf_path), '-'],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except FileNotFoundError:
        print(f"[WARN] pdftotext not found, trying alternative method")
        return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def extract_metadata_from_filename(pdf_path):
    """从文件名提取 arXiv ID"""
    match = re.search(r'(\d+\.\d+)\.pdf', pdf_path.name)
    if match:
        return {'arxiv_id': match.group(1)}
    return {}

def parse_first_page(text):
    """解析第一页提取关键信息"""
    metadata = {
        'title': None,
        'authors': [],
        'abstract': None,
        'keywords': []
    }
    
    lines = text.split('\n')[:50]  # 只分析前 50 行
    text_block = '\n'.join(lines)
    
    # 提取标题 (通常在第一行，大写或居中)
    for i, line in enumerate(lines[:5]):
        if len(line.strip()) > 20 and not line.strip().startswith('arXiv:'):
            metadata['title'] = line.strip()
            break
    
    # 提取作者 (包含"and"或逗号分隔的名字)
    author_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+(?: and [A-Z][a-z]+ [A-Z][a-z]+)*)'
    authors_match = re.search(author_pattern, text_block)
    if authors_match:
        authors_str = authors_match.group(1)
        metadata['authors'] = [a.strip() for a in re.split(r',| and ', authors_str)]
    
    # 提取摘要
    abstract_match = re.search(r'Abstract[:\s]*(.*?)(?:\n\n|\Z)', text_block, re.DOTALL)
    if abstract_match:
        metadata['abstract'] = abstract_match.group(1).strip()
    
    return metadata

def extract_metadata_from_pdf(pdf_path):
    """从单个 PDF 提取元数据"""
    metadata = extract_metadata_from_filename(pdf_path)
    
    # 尝试提取 PDF 内容
    text = extract_metadata_with_pdftotext(pdf_path)
    if text:
        content_metadata = parse_first_page(text)
        metadata.update(content_metadata)
    
    # 添加文件信息
    metadata['pdf_path'] = str(pdf_path)
    metadata['file_size'] = pdf_path.stat().st_size
    
    return metadata

def batch_extract_metadata(date_str=None):
    """批量提取指定日期的 PDF 元数据"""
    if date_str:
        pdf_dir = PDF_DIR / date_str
    else:
        pdf_dir = PDF_DIR
    
    if not pdf_dir.exists():
        print(f"[ERROR] Directory not found: {pdf_dir}")
        return []
    
    pdf_files = list(pdf_dir.glob('*.pdf'))
    print(f"Found {len(pdf_files)} PDF files in {pdf_dir}")
    
    metadata_list = []
    for pdf_file in pdf_files:
        print(f"Extracting: {pdf_file.name}")
        try:
            metadata = extract_metadata_from_pdf(pdf_file)
            metadata_list.append(metadata)
        except Exception as e:
            print(f"[ERROR] Failed to extract {pdf_file.name}: {e}")
    
    # 保存为 JSON
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"metadata-{date_str or 'latest'}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Metadata saved to: {output_file}")
    print(f"  Total: {len(metadata_list)} files")
    
    return metadata_list

if __name__ == "__main__":
    import sys
    
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    batch_extract_metadata(date_str)
