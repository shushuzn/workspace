#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Quality Checker v1
数据质量检查与清理系统
"""

import json
from datetime import datetime
from pathlib import Path

# 配置
ARXIV_DIR = Path(r"D:\obsidian\Vault\Arxiv\daily")
OUTPUT_DIR = Path(r"D:\obsidian\Vault\AI-Research\Data-Quality")

def check_duplicate_papers():
    """检查重复论文"""
    duplicates = []
    seen_ids = set()

    for date_dir in ARXIV_DIR.iterdir():
        if not date_dir.is_dir():
            continue

        for domain_dir in date_dir.iterdir():
            if not domain_dir.is_dir() or domain_dir.name == 'logs':
                continue

            for paper_file in domain_dir.glob('*.md'):
                arxiv_id = paper_file.stem.split('-')[0]
                if arxiv_id in seen_ids:
                    duplicates.append(str(paper_file))
                else:
                    seen_ids.add(arxiv_id)

    return duplicates

def check_pdf_downloads():
    """检查 PDF 下载状态"""
    pdf_dir = Path(r"D:\obsidian\Vault\Arxiv\PDF")
    stats = {'total': 0, 'empty': 0, 'normal': 0}

    if pdf_dir.exists():
        for pdf_file in pdf_dir.rglob('*.pdf'):
            stats['total'] += 1
            if pdf_file.stat().st_size < 1000:  # 小于 1KB 视为空文件
                stats['empty'] += 1
            else:
                stats['normal'] += 1

    return stats

def generate_quality_report(duplicates, pdf_stats):
    """生成质量报告"""
    return {
        'generated_at': datetime.now().isoformat(),
        'duplicates': {
            'count': len(duplicates),
            'files': duplicates[:10]  # 只显示前 10 个
        },
        'pdf_downloads': pdf_stats,
        'quality_score': calculate_quality_score(duplicates, pdf_stats)
    }

def calculate_quality_score(duplicates, pdf_stats):
    """计算质量分数"""
    score = 100

    # 重复论文扣分
    score -= len(duplicates) * 2

    # PDF 空文件扣分
    if pdf_stats['total'] > 0:
        empty_ratio = pdf_stats['empty'] / pdf_stats['total']
        score -= empty_ratio * 20

    return max(0, min(100, score))

def save_quality_report(report):
    """保存质量报告"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    md_file = OUTPUT_DIR / f"data-quality-{date_str}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# 数据质量报告 - {date_str}\n\n")
        f.write(f"**生成时间:** {report['generated_at']}\n\n")
        f.write("---\n\n")

        f.write(f"## 📊 质量评分：**{report['quality_score']:.1f}/100**\n\n")
        f.write("---\n\n")

        f.write("## 🔍 重复论文检查\n\n")
        f.write(f"**发现重复:** {report['duplicates']['count']} 个\n\n")
        if report['duplicates']['files']:
            f.write("**文件列表:**\n")
            for f_path in report['duplicates']['files']:
                f.write(f"- `{f_path}`\n")
        f.write("\n---\n\n")

        f.write("## 📥 PDF 下载状态\n\n")
        pdf = report['pdf_downloads']
        f.write(f"- **总数:** {pdf['total']}\n")
        f.write(f"- **正常:** {pdf['normal']}\n")
        f.write(f"- **空文件:** {pdf['empty']}\n")
        f.write("\n---\n\n")

        f.write("## 💡 建议\n\n")
        if report['duplicates']['count'] > 0:
            f.write("1. 清理重复论文文件\n")
        if pdf['empty'] > 0:
            f.write("2. 重新下载空 PDF 文件\n")
        if report['quality_score'] < 80:
            f.write("3. 执行全面数据清理\n")

    print(f"[OK] Saved quality report to {md_file}")
    return md_file

def check_quality():
    """主流程"""
    print("=" * 60)
    print("Data Quality Checker v1")
    print("=" * 60)

    print("\n[1/3] Checking duplicates...")
    duplicates = check_duplicate_papers()
    print(f"  Found {len(duplicates)} duplicates")

    print("\n[2/3] Checking PDF downloads...")
    pdf_stats = check_pdf_downloads()
    print(f"  Total: {pdf_stats['total']}, Empty: {pdf_stats['empty']}")

    print("\n[3/3] Generating report...")
    report = generate_quality_report(duplicates, pdf_stats)
    save_quality_report(report)

    print("-" * 60)
    print(f"[COMPLETE] Quality Score: {report['quality_score']:.1f}/100")
    print("=" * 60)

if __name__ == "__main__":
    check_quality()
