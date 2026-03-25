#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arxiv Old Data Migration Script
迁移旧版 Arxiv 文件夹数据到新目录结构

旧格式：D:\obsidian\Vault\Arxiv\YYYYMMDD-HHMMSS-Title.md
新格式：D:\obsidian\Vault\arxiv\daily\YYYY\MM\DD\domain\YYYY-MM-DD-HHMMSS-Title.md
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================

OLD_ARXIV_PATH = Path(r"D:\obsidian\Vault\Arxiv")
NEW_ARXIV_ROOT = Path(r"D:\obsidian\Vault\arxiv")
BACKUP_PATH = Path(r"D:\obsidian\Vault\Arxiv-backup-" + datetime.now().strftime('%Y%m%d-%H%M%S'))

# 领域关键词映射 (从标题/内容推断领域)
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
    """解析旧文件名：YYYYMMDD-HHMMSS-Title.md"""
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
    """从文件内容检测领域"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().lower()

        # 检查 YAML frontmatter 中的 tags
        if '---' in content:
            frontmatter = content.split('---')[1]
            if 'tag:' in frontmatter or 'tags:' in frontmatter:
                for line in frontmatter.split('\n'):
                    if 'cs' in line.lower():
                        match = re.search(r'cs([A-Z]{2})', line, re.IGNORECASE)
                        if match:
                            return f"cs{match.group(1)}"

        # 从标题/内容关键词推断
        for domain, keywords in DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content:
                    return domain

        return 'csAI'  # 默认领域
    except Exception as e:
        print(f"  [WARN] 无法检测领域：{e}")
        return 'csAI'

def get_new_path(parsed, domain):
    """生成新路径"""
    date = parsed['datetime']
    year = date.strftime('%Y')
    month = date.strftime('%m')
    day = date.strftime('%Y-%m-%d')

    new_dir = NEW_ARXIV_ROOT / "daily" / year / month / day / domain
    new_filename = f"{day}-{parsed['time'].replace(':', '')}-{parsed['title']}.md"

    return new_dir / new_filename

def ensure_directory(path):
    """确保目录存在"""
    path.parent.mkdir(parents=True, exist_ok=True)

# ==================== 主流程 ====================

def migrate_dry_run():
    """预览模式：只显示将要执行的操作"""
    print("=" * 70)
    print("Arxiv 数据迁移 - 预览模式")
    print("=" * 70)

    if not OLD_ARXIV_PATH.exists():
        print(f"[ERROR] 旧目录不存在：{OLD_ARXIV_PATH}")
        return

    files = list(OLD_ARXIV_PATH.glob("*.md"))
    print(f"\n找到 {len(files)} 个旧文件")

    stats = {'total': 0, 'by_domain': {}, 'by_date': {}}

    for filepath in files[:20]:  # 只显示前 20 个
        filename = filepath.name
        parsed = parse_old_filename(filename)

        if not parsed:
            print(f"  [SKIP] 无法解析：{filename}")
            continue

        domain = detect_domain(filepath)
        new_path = get_new_path(parsed, domain)

        print(f"  {filename}")
        print(f"    → {new_path.relative_to(NEW_ARXIV_ROOT)}")
        print(f"    领域：{domain}, 日期：{parsed['date']}")

        stats['total'] += 1
        stats['by_domain'][domain] = stats['by_domain'].get(domain, 0) + 1
        stats['by_date'][parsed['date']] = stats['by_date'].get(parsed['date'], 0) + 1

    if len(files) > 20:
        print(f"  ... 还有 {len(files) - 20} 个文件")

    print(f"\n统计 (预览前 20 个):")
    print(f"  总文件数：{stats['total']}")
    print(f"  领域分布：{stats['by_domain']}")
    print(f"  日期分布：{stats['by_date']}")

def migrate_execute():
    """执行迁移"""
    print("=" * 70)
    print("Arxiv 数据迁移 - 执行模式")
    print("=" * 70)

    if not OLD_ARXIV_PATH.exists():
        print(f"[ERROR] 旧目录不存在：{OLD_ARXIV_PATH}")
        return

    # 1. 备份旧数据
    print(f"\n[1/4] 备份旧数据...")
    print(f"  备份到：{BACKUP_PATH}")
    shutil.copytree(OLD_ARXIV_PATH, BACKUP_PATH)
    print(f"  [OK] 备份完成")

    # 2. 确保新目录根存在
    print(f"\n[2/4] 初始化新目录...")
    NEW_ARXIV_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"  [OK] 新目录就绪：{NEW_ARXIV_ROOT}")

    # 3. 迁移文件
    print(f"\n[3/4] 迁移文件...")
    files = list(OLD_ARXIV_PATH.glob("*.md"))
    stats = {'total': len(files), 'success': 0, 'failed': 0, 'by_domain': {}}

    for i, filepath in enumerate(files, 1):
        filename = filepath.name
        parsed = parse_old_filename(filename)

        if not parsed:
            print(f"  [{i}/{len(files)}] [SKIP] 无法解析：{filename}")
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
        except Exception as e:
            print(f"  [{i}/{len(files)}] [FAIL] {filename} - {e}")
            stats['failed'] += 1

    # 4. 生成迁移报告
    print(f"\n[4/4] 生成迁移报告...")
    report_path = NEW_ARXIV_ROOT / "migration-report.md"

    content = f"""---
created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
tags: [arxiv, migration, log]
---

# Arxiv 数据迁移报告

## 执行时间

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计

| 指标 | 数值 |
|------|------|
| 总文件数 | {stats['total']} |
| 成功迁移 | {stats['success']} |
| 失败 | {stats['failed']} |
| 领域覆盖 | {len(stats['by_domain'])} |

## 领域分布

| 领域 | 数量 |
|------|------|
"""

    for domain, count in sorted(stats['by_domain'].items()):
        content += f"| {domain} | {count} |\n"

    content += f"""
## 备份位置

{BACKUP_PATH}

## 后续操作

1. ✅ 验证新目录结构正确
2. ✅ 确认所有文件可访问
3. ⬜ 删除旧目录 (D:\\obsidian\\Vault\\Arxiv)
4. ⬜ 更新相关链接/引用

---
*自动生成*
"""

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  [OK] 报告已生成：{report_path}")

    # 输出结果
    print("\n" + "=" * 70)
    print(f"[SUCCESS] 迁移完成")
    print(f"  总文件数：{stats['total']}")
    print(f"  成功：{stats['success']}")
    print(f"  失败：{stats['failed']}")
    print(f"  领域：{len(stats['by_domain'])}")
    print(f"\n  备份：{BACKUP_PATH}")
    print(f"  报告：{report_path}")
    print("=" * 70)

# ==================== 主入口 ====================

if __name__ == '__main__':
    import sys

    print("\nArxiv 数据迁移工具")
    print("=" * 70)

    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        migrate_execute()
    else:
        migrate_dry_run()
        print("\n" + "=" * 70)
        print("提示：运行以下命令执行实际迁移:")
        print("  python arxiv-migrate.py --execute")
        print("=" * 70)
