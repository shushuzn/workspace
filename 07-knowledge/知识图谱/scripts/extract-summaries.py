#!/usr/bin/env python3
"""
知识图谱增强 - 第 1 阶段：摘要提取

从 P-Note 提取论文摘要并添加到知识图谱
"""

import json
import re
from pathlib import Path

def extract_summary_from_pnote(file_path: Path) -> dict:
    """从 P-Note 提取摘要"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [ERROR] 读取失败：{e}")
        return None

    summary = {
        "title": "",
        "arxiv_id": "",
        "authors": "",
        "key_findings": [],
        "methods": [],
        "confidence": 0.0,
        "source_file": str(file_path.name)
    }

    # 1. 提取标题 (P-Note 格式)
    title_patterns = [
        r'# P-Note:\s*(.+?)(?:\n|$)',
        r'# P-Note\s+(.+?)(?:\n|$)',
        r'^#\s+(.+?)(?:\n|$)'
    ]
    for pattern in title_patterns:
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            summary["title"] = match.group(1).strip()
            break

    # 2. 提取 arXiv ID
    arxiv_patterns = [
        r'arXiv[:\s]+(\d+\.\d+)',
        r'https?://arxiv\.org/abs/(\d+\.\d+)'
    ]
    for pattern in arxiv_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            summary["arxiv_id"] = match.group(1)
            break

    # 3. 提取作者
    author_match = re.search(r'作者 [：:\s]*(.+?)(?:\n|$)', content, re.IGNORECASE)
    if author_match:
        summary["authors"] = author_match.group(1).strip()

    # 4. 提取 10 维度分析 (关键发现)
    dims_section = re.search(r'## 📝 10 维度分析.*?(?=## |$)', content, re.DOTALL)
    if dims_section:
        dims_text = dims_section.group(0)
        # 提取各维度标题
        dim_titles = re.findall(r'### \d+\.\s*(.+?)(?:\n|$)', dims_text)
        summary["key_findings"] = [d.strip() for d in dim_titles[:5]]

    # 5. 提取核心方法
    method_patterns = [
        r'### 2\. 核心方法\s*\n(.+?)(?=### |$)',
        r'## 核心方法\s*\n(.+?)(?=## |$)'
    ]
    for pattern in method_patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            method_text = match.group(1).strip()
            # 清理格式
            method_text = re.sub(r'^#+\s*', '', method_text)
            summary["methods"] = [method_text[:300]]
            break

    # 6. 计算置信度
    score = 0
    if summary["title"]: score += 0.3
    if summary["arxiv_id"]: score += 0.3
    if summary["key_findings"]: score += 0.2
    if summary["methods"]: score += 0.2
    summary["confidence"] = round(score, 1)

    return summary

def enhance_knowledge_graph():
    """增强知识图谱"""
    print("=" * 50)
    print("知识图谱增强 - 第 1 阶段：摘要提取")
    print("=" * 50)
    print()

    # 扫描 Medium 目录中的 P-Note
    medium_dir = Path("D:/OpenClaw/workspace/Medium")
    summaries = {}

    print(f"[INFO] 扫描目录：{medium_dir}")
    print()

    if medium_dir.exists():
        # 查找 P-Note 文件
        pnote_files = list(medium_dir.glob("P-*.md"))
        print(f"[INFO] 找到 {len(pnote_files)} 篇 P-Note")
        print()

        for pnote_file in pnote_files:
            print(f"[EXTRACT] {pnote_file.stem}")
            summary = extract_summary_from_pnote(pnote_file)

            if summary and summary["arxiv_id"]:
                key = f"paper_{summary['arxiv_id'].replace('.', '_')}"
                summaries[key] = summary
                print(f"  [OK] 标题：{summary['title'][:60]}...")
                print(f"  [OK] arXiv: {summary['arxiv_id']}")
                print(f"  [OK] 发现：{len(summary['key_findings'])} 个维度")
                print(f"  [OK] 置信度：{summary['confidence']}\n")
            elif summary:
                print(f"  [WARN] 缺少 arXiv ID\n")
            else:
                print(f"  [SKIP] 提取失败\n")

    # 保存摘要
    output_file = Path("D:/OpenClaw/workspace/knowledge-graph/paper-summaries.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

    print("=" * 50)
    print(f"[OK] 摘要已保存：{output_file}")
    print(f"[INFO] 共提取 {len(summaries)} 篇论文摘要")
    print("=" * 50)

    return summaries

if __name__ == "__main__":
    enhance_knowledge_graph()
