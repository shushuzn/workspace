#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简易记忆蒸馏工具

从日常笔记提取关键洞察，更新到 MEMORY.md
"""

import sys
import re
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'
MEMORY_MD = MEMORY_DIR / 'MEMORY.md'


def extract_insights(daily_note_path: Path) -> list:
    """从日常笔记提取洞察"""
    if not daily_note_path.exists():
        return []
    
    content = daily_note_path.read_text(encoding='utf-8')
    insights = []
    
    # 提取关键成就
    achievements = re.findall(r'### \d+\. (.*?)\n(.*?)(?=\n### |\Z)', content, re.DOTALL)
    for title, desc in achievements:
        insights.append({
            'type': 'achievement',
            'title': title.strip(),
            'content': desc.strip()[:200]  # 限制长度
        })
    
    # 提取关键洞察
    insights_section = re.search(r'## 🧠 Key Insights\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if insights_section:
        items = re.findall(r'### \d+\. (.*?)\n(.*?)(?=\n### |\Z)', insights_section.group(1), re.DOTALL)
        for title, desc in items:
            insights.append({
                'type': 'insight',
                'title': title.strip(),
                'content': desc.strip()
            })
    
    # 提取教训
    lessons = re.search(r'## ⚠️ Lessons Learned\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    if lessons:
        items = re.findall(r'### \d+\. (.*?)\n(.*?)(?=\n### |\Z)', lessons.group(1), re.DOTALL)
        for title, desc in items:
            insights.append({
                'type': 'lesson',
                'title': title.strip(),
                'content': desc.strip()
            })
    
    return insights


def update_memory_md(insights: list, memory_md_path: Path):
    """更新 MEMORY.md"""
    if not memory_md_path.exists():
        print(f"❌ MEMORY.md 不存在：{memory_md_path}")
        return
    
    content = memory_md_path.read_text(encoding='utf-8')
    
    # 找到 "## Key Metrics" 或 "## Backlinks" 之前的位置
    insert_marker = "## Backlinks"
    insert_pos = content.find(insert_marker)
    
    if insert_pos == -1:
        insert_pos = len(content)
    
    # 创建新内容
    new_section = f"""
## Latest Distillation ({datetime.now().strftime('%Y-%m-%d')})

**Source:** 2026-03-18.md  
**Distilled Insights:** {len(insights)} items

"""
    
    for i, insight in enumerate(insights[:5], 1):  # 最多 5 个
        new_section += f"""
### {i}. {insight['title']}
{insight['content'][:150]}...

"""
    
    # 插入新内容
    new_content = content[:insert_pos] + new_section + content[insert_pos:]
    
    # 保存
    memory_md_path.write_text(new_content, encoding='utf-8')
    print(f"✅ MEMORY.md 已更新")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='简易记忆蒸馏工具')
    parser.add_argument('--source', type=str, default='2026-03-18.md',
                        help='源日常笔记文件')
    parser.add_argument('--dry-run', action='store_true',
                        help='只显示不写入')
    
    args = parser.parse_args()
    
    source_path = MEMORY_DIR / args.source
    
    print("=" * 60)
    print("记忆蒸馏工具")
    print("=" * 60)
    print()
    
    # 提取洞察
    print(f"📖 读取源文件：{source_path}")
    insights = extract_insights(source_path)
    
    if not insights:
        print("⚠️  未找到可提取的洞察")
        return 0
    
    print(f"✅ 提取 {len(insights)} 个洞察")
    print()
    
    # 显示洞察
    print("【提取的洞察】")
    for i, insight in enumerate(insights[:5], 1):
        print(f"\n{i}. [{insight['type']}] {insight['title']}")
        print(f"   {insight['content'][:100]}...")
    
    if len(insights) > 5:
        print(f"\n... 还有 {len(insights)-5} 个洞察")
    
    print()
    
    # 更新 MEMORY.md
    if not args.dry_run:
        print("🔄 更新 MEMORY.md...")
        update_memory_md(insights, MEMORY_MD)
    else:
        print("📄 Dry-run 模式：未写入 MEMORY.md")
    
    print()
    print("=" * 60)
    print("✅ 记忆蒸馏完成")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
