#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arxiv Old Data Migration Script - Recovery Version
从备份目录迁移数据到新结构
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

# 从备份恢复
OLD_ARXIV_PATH = Path(r"D:\obsidian\Vault\Arxiv-backup-20260303-042331")
NEW_ARXIV_ROOT = Path(r"D:\obsidian\Vault\arxiv")

DOMAIN_KEYWORDS = {
    'csAI': ['agent', 'llm', 'language model', 'reasoning', 'planning', 'cognitive', 'autonomous'],
    'csLG': ['learning', 'training', 'optimization', 'gradient', 'neural network', 'deep learning', 'ml'],
    'csCV': ['image', 'vision', 'visual', 'detection', 'segmentation', 'recognition', 'cnn'],
    'csCL': ['speech', 'language', 'nlp', 'translation', 'text', 'linguistic'],
    'csIR': ['retrieval', 'search', 'recommendation', 'ranking', 'query'],
    'csSE': ['software', 'code', 'programming', 'development', 'testing', 'debug'],
    'csDC': ['distributed', 'parallel', 'cloud', 'workflow', 'system'],
    'csRO': ['robot', 'robotic', 'control', 'manipulation', 'autonomous'],
    'csSY': ['system', 'architecture', 'hardware', 'os', 'kernel'],
}

# ==================== 工具函数 ====================

def parse_old_filename(filename):
    match = re.match(r'(\d{8})-(\d{6})-(.+)\.md', filename)
    if match:
        date_str = match.group(1)
        time_str = match.group(2)
        title = match.group(3)
        return {
            'date': f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}",
            'time': f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:]}",
            'title': title,
            'datetime': datetime.strptime(f"{date_str}{time_str}", '%Y%m%d%H%M%S')
        }
    return None

def detect_domain(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().lower()

        if '---' in content:
            frontmatter = content.split('---')[1]
            if 'tag:' in frontmatter or 'tags:' in frontmatter:
                for line in frontmatter.split('\n'):
                    if 'cs' in line.lower():
                        match = re.search(r'cs([A-Z]{2})', line, re.IGNORECASE)
                        if match:
                            return f"cs{match.group(1)}"

        for domain, keywords in DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content:
                    return domain

        return 'csAI'
    except Exception as e:
        print(f"  [WARN] Domain detection failed: {e}")
        return 'csAI'

def get_new_path(parsed, domain):
    date = parsed['datetime']
    year = date.strftime('%Y')
    month = date.strftime('%m')
    day = date.strftime('%Y-%m-%d')

    new_dir = NEW_ARXIV_ROOT / "daily" / year / month / day / domain
    new_filename = f"{day}-{parsed['time'].replace(':', '')}-{parsed['title']}.md"

    return new_dir / new_filename

def ensure_directory(path):
    path.parent.mkdir(parents=True, exist_ok=True)

# ==================== 主流程 ====================

def migrate_execute():
    print("=" * 70)
    print("Arxiv Data Migration - Recovery from Backup")
    print("=" * 70)

    if not OLD_ARXIV_PATH.exists():
        print(f"[ERROR] Backup directory not found: {OLD_ARXIV_PATH}")
        return

    # 1. Ensure new root
    print(f"\n[1/3] Initializing new directory...")
    NEW_ARXIV_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"  [OK] Ready: {NEW_ARXIV_ROOT}")

    # 2. Migrate files
    print(f"\n[2/3] Migrating files...")
    files = list(OLD_ARXIV_PATH.glob("*.md"))
    stats = {'total': len(files), 'success': 0, 'failed': 0, 'by_domain': {}, 'by_date': {}}

    for i, filepath in enumerate(files, 1):
        filename = filepath.name
        parsed = parse_old_filename(filename)

        if not parsed:
            print(f"  [{i}/{len(files)}] [SKIP] Cannot parse: {filename}")
            stats['failed'] += 1
            continue

        domain = detect_domain(filepath)
        new_path = get_new_path(parsed, domain)

        try:
            ensure_directory(new_path)
            shutil.copy2(filepath, new_path)
            print(f"  [{i}/{len(files)}] [OK] {domain}: {filename[:50]}...")
            stats['success'] += 1
            stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1
            date_key = parsed['date']
            stats['by_date'][date_key] = stats['by_date'].get(date_key, 0) + 1
        except Exception as e:
            print(f"  [{i}/{len(files)}] [FAIL] {filename} - {e}")
            stats['failed'] += 1

    # 3. Generate report
    print(f"\n[3/3] Generating report...")
    report_path = NEW_ARXIV_ROOT / "migration-report-recovery.md"

    content = f"""---
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
tags: [arxiv, migration, log, recovery]
---

# Arxiv Data Migration Report (Recovery)

## Execution Time

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Source

Backup: {OLD_ARXIV_PATH}

## Statistics

| Metric | Value |
|--------|-------|
| Total files | {stats['total']} |
| Success | {stats['success']} |
| Failed | {stats['failed']} |
| Domains | {len(stats['by_domain'])} |
| Dates | {len(stats['by_date'])} |

## Domain Distribution

| Domain | Count |
|--------|-------|
"""

    for domain, count in sorted(stats['by_domain'].items()):
        content += f"| {domain} | {count} |\n"

    content += "\n## Date Distribution\n\n"
    for date, count in sorted(stats['by_date'].items()):
        content += f"- {date}: {count} papers\n"

    content += f"""
## Output Path

{NEW_ARXIV_ROOT}

---
*Auto-generated*
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  [OK] Report: {report_path}")

    # Output
    print("\n" + "=" * 70)
    print(f"[SUCCESS] Migration complete")
    print(f"  Total: {stats['total']}")
    print(f"  Success: {stats['success']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Domains: {len(stats['by_domain'])}")
    print(f"  Dates: {len(stats['by_date'])}")
    print(f"\n  Output: {NEW_ARXIV_ROOT}")
    print("=" * 70)

if __name__ == '__main__':
    migrate_execute()
