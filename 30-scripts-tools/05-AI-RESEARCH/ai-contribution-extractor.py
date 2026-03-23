#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 核心贡献提取器
使用 AI 从 PDF 元数据中提取核心贡献点
"""

import json
from pathlib import Path
from datetime import datetime

# 配置
METADATA_DIR = Path(r"D:\obsidian\Vault\Arxiv\metadata")
PNOTE_OUTPUT_DIR = Path(r"D:\obsidian\Vault\AI-Research\P-Note")
TEMPLATE_FILE = Path(r"str(Path(__file__).parent.parent)\templates\P-Note-Template-v2.md")

def load_metadata(metadata_file):
    """加载元数据 JSON"""
    with open(metadata_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_key_contributions_with_ai(abstract, title):
    """
    使用 AI 从摘要提取核心贡献
    实际部署时调用 AI API，这里使用规则提取
    """
    # 简化版：基于关键词和句子结构提取
    contributions = []

    # 常见贡献模式
    patterns = [
        (r'we propose (.*?)\.', '提出方法'),
        (r'we introduce (.*?)\.', '引入技术'),
        (r'our approach (.*?)\.', '方法特点'),
        (r'our method (.*?)\.', '方法优势'),
        (r'we demonstrate (.*?)\.', '实验证明'),
        (r'we achieve (.*?)\.', '达成效果'),
    ]

    import re
    text = abstract.lower()

    for pattern, label in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            contributions.append(f"{label}: {match.capitalize()}")

    # 如果规则提取失败，返回摘要前 3 句
    if not contributions:
        sentences = abstract.split('.')[:3]
        contributions = [s.strip() + '.' for s in sentences if len(s.strip()) > 20]

    return contributions[:5]  # 最多 5 个贡献点

def extract_methods(abstract):
    """提取方法关键词"""
    method_keywords = [
        'transformer', 'attention', 'bert', 'gpt', 'llm',
        'reinforcement learning', 'rl', 'ppo',
        'diffusion', 'gan', 'vae',
        'fine-tuning', 'prompt', 'in-context learning'
    ]

    methods = []
    abstract_lower = abstract.lower()
    for keyword in method_keywords:
        if keyword in abstract_lower:
            methods.append(keyword.title())

    return methods if methods else ['方法待补充']

def extract_experiment_info(abstract):
    """提取实验信息"""
    exp_keywords = [
        'experiment', 'evaluation', 'benchmark', 'dataset',
        'accuracy', 'performance', 'result', 'comparison'
    ]

    exp_info = []
    abstract_lower = abstract.lower()
    for keyword in exp_keywords:
        if keyword in abstract_lower:
            exp_info.append(f"包含 {keyword} 分析")

    return exp_info if exp_info else ['实验信息待补充']

def fill_pnote_template(metadata, contributions, methods, experiments):
    """填充 P-Note 模板"""

    # 读取模板
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    # 准备数据
    arxiv_id = metadata.get('arxiv_id', 'unknown')
    title = metadata.get('title', '标题待确认')
    authors = metadata.get('authors', ['作者待确认'])
    abstract = metadata.get('abstract', '摘要待提取')

    # 替换占位符
    replacements = {
        '{{date}}': datetime.now().strftime('%Y-%m-%d'),
        '{{arxiv_id}}': arxiv_id,
        '{{title}}': title,
        '{{authors}}': ', '.join(authors) if isinstance(authors, list) else authors,
        '{{categories}}': metadata.get('categories', '待分类'),
        '{{priority_score}}': metadata.get('priority_score', '3'),
        '{{pub_date}}': datetime.now().strftime('%Y-%m-%d'),
        '{{abstract}}': abstract,
        '{{created_at}}': datetime.now().strftime('%Y-%m-%d %H:%M'),
        '{{updated_at}}': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }

    # 替换简单占位符
    for key, value in replacements.items():
        template = template.replace(key, str(value))

    # 替换列表占位符 (核心贡献)
    contributions_text = '\n'.join([f"{i +1}. {c}" for i, c in enumerate(contributions)])
    template = template.replace('{{core_contributions}}', contributions_text)

    # 替换方法列表
    methods_text = '\n- ' + '\n- '.join(methods)
    template = template.replace('{{methods}}', methods_text)

    # 替换实验信息
    exp_text = '\n- ' + '\n- '.join(experiments)
    template = template.replace('{{experiments}}', exp_text)

    return template

def generate_pnote(metadata_entry):
    """为单个论文生成 P-Note"""
    arxiv_id = metadata_entry.get('arxiv_id', 'unknown')
    abstract = metadata_entry.get('abstract', '')
    title = metadata_entry.get('title', '')

    print(f"Generating P-Note for {arxiv_id}...")

    # AI 提取核心贡献
    contributions = extract_key_contributions_with_ai(abstract, title)

    # 提取方法
    methods = extract_methods(abstract)

    # 提取实验信息
    experiments = extract_experiment_info(abstract)

    # 填充模板
    pnote_content = fill_pnote_template(metadata_entry, contributions, methods, experiments)

    # 保存 P-Note
    PNOTE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_title = ''.join(c for c in title[:50] if c.isalnum() or c in ' -_').strip()
    filename = f"P-{arxiv_id}-{safe_title}.md"
    output_file = PNOTE_OUTPUT_DIR / filename

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(pnote_content)

    print(f"  [OK] Saved: {filename}")
    print(f"       Contributions: {len(contributions)} points")

    return output_file

def batch_generate_pnotes(metadata_file):
    """批量生成 P-Note"""
    print(f"Loading metadata from: {metadata_file}")
    metadata_list = load_metadata(metadata_file)

    print(f"Found {len(metadata_list)} papers")
    print("-" * 60)

    results = []
    for metadata in metadata_list:
        try:
            output_file = generate_pnote(metadata)
            results.append({
                'arxiv_id': metadata.get('arxiv_id'),
                'output': str(output_file),
                'status': 'success'
            })
        except Exception as e:
            print(f"  [FAIL] {metadata.get('arxiv_id')}: {e}")
            results.append({
                'arxiv_id': metadata.get('arxiv_id'),
                'error': str(e),
                'status': 'failed'
            })

    # 保存结果统计
    summary_file = PNOTE_OUTPUT_DIR / f"generation-summary-{datetime.now().strftime('%Y%m%d-%H%M')}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(metadata_list),
            'success': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'results': results
        }, f, ensure_ascii=False, indent=2)

    print("-" * 60)
    print(f"[COMPLETE] Generated {len([r for r in results if r['status'] == 'success'])}/{len(metadata_list)} P-Notes")
    print(f"Output dir: {PNOTE_OUTPUT_DIR}")

    return results

if __name__ == "__main__":
    import sys

    # 用法：py ai-contribution-extractor.py [metadata_file]
    metadata_file = sys.argv[1] if len(sys.argv) > 1 else None

    if not metadata_file:
        # 默认使用最新元数据文件
        metadata_files = list(METADATA_DIR.glob('metadata-*.json'))
        if metadata_files:
            metadata_file = sorted(metadata_files)[-1]
            print(f"Using latest metadata: {metadata_file}")
        else:
            print("[ERROR] No metadata file found")
            print("Usage: py ai-contribution-extractor.py [metadata_file]")
            sys.exit(1)

    batch_generate_pnotes(metadata_file)
