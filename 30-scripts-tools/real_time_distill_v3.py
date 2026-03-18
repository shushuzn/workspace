#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
实时蒸馏工具 v3.0
功能：会话结束时自动提取高价值观点并更新 MEMORY.md
"""

import os
import sys
import re
import json
from datetime import datetime

def extract_key_insights(daily_note_file):
    """从日常笔记中提取关键洞察"""
    
    if not os.path.exists(daily_note_file):
        print(f"[ERROR] 文件不存在：{daily_note_file}")
        return []
    
    with open(daily_note_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取模式：查找带有标记的洞察
    # 支持：[XXX-001] 标题 或 ### [XXX-001] 标题
    pattern = r'(?:###\s*)?\[([A-Z]{2,4}-\d{3})\]\s*([^\n]+)'
    
    matches = re.findall(pattern, content)
    
    insights = []
    for match_id, title in matches:
        insights.append({
            'id': match_id,
            'title': title.strip(),
            'source': daily_note_file,
            'extracted_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    
    return insights

def generate_memory_entry(insight, daily_note_content):
    """生成标准化记忆条目"""
    
    template = f"""
### [{insight['id']}] {insight['title']}

**日期:** {datetime.now().strftime("%Y-%m-%d")}  
**来源:** 实时蒸馏 v3.0 - {os.path.basename(insight['source'])}  
**置信度:** 中  
**类别:** 洞察  
**状态:** 活跃  

**核心观点:**
[待补充 - 一句话概括]

**详细内容:**
- **背景:** [待补充]
- **论据:** [待补充]
- **结论:** [待补充]

**可迁移模式:**
```
[待补充]
```

**关联记忆:**
- [待补充]

**元数据:**
- 新颖度：[待评分 0-100]
- 可迁移性：[待评分 0-100]
- 重要性：[待评分 0-100]
- 最后复习：{datetime.now().strftime("%Y-%m-%d")}
- 强度：1.0 (新记忆)
- 访问次数：0

**版本历史:**
- v1.0 ({datetime.now().strftime("%Y-%m-%d")}): 实时蒸馏创建
"""
    return template

def append_to_memory(memory_file, insights, daily_note_content):
    """追加到 MEMORY.md"""
    
    if not os.path.exists(memory_file):
        print(f"[ERROR] MEMORY.md 不存在：{memory_file}")
        return False
    
    # 读取现有内容
    with open(memory_file, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    # 查找"## 🆕 最新记忆"部分
    latest_section_pattern = r'(## 🆕 最新记忆.*?)(\n##|\Z)'
    match = re.search(latest_section_pattern, existing_content, re.DOTALL)
    
    if not match:
        print("[WARN] 未找到'最新记忆'部分，追加到文件末尾")
        # 追加到末尾
        new_entries = ""
        for insight in insights:
            entry = generate_memory_entry(insight, daily_note_content)
            new_entries += entry + "\n"
        
        updated_content = existing_content + "\n\n" + new_entries
    else:
        # 插入到最新记忆部分
        insert_pos = match.start(2)
        new_entries = ""
        for insight in insights:
            entry = generate_memory_entry(insight, daily_note_content)
            new_entries += entry + "\n"
        
        updated_content = (
            existing_content[:insert_pos] + 
            "\n" + new_entries + 
            existing_content[insert_pos:]
        )
    
    # 写回文件
    with open(memory_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"[OK] 已添加 {len(insights)} 条新记忆到 MEMORY.md")
    return True

def update_daily_note_header(daily_note_file, distilled=True):
    """更新日常笔记头部标记"""
    
    if not os.path.exists(daily_note_file):
        return False
    
    with open(daily_note_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加蒸馏标记
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    marker = f"\n\n*已蒸馏：{timestamp} | 实时蒸馏 v3.0*"
    
    if "*已蒸馏：" not in content:
        content += marker
        
        with open(daily_note_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] 已更新日常笔记标记")
    
    return True

def real_time_distill(daily_note_file=None, memory_file=None, auto_commit=True):
    """实时蒸馏主函数"""
    
    # 自动检测文件（支持双工作区）
    if not daily_note_file:
        today = datetime.now().strftime("%Y-%m-%d")
        possible_files = [
            os.path.join('memory', f'{today}.md'),
            os.path.join('13-memory', f'{today}.md'),
            f'{today}.md',
            # CoPaw 工作区
            r'C:\Users\华为\.copaw\workspaces\default\memory' + f'\\{today}.md',
        ]
        
        for pf in possible_files:
            if os.path.exists(pf):
                daily_note_file = pf
                break
        
        if not daily_note_file:
            print("[ERROR] 未找到今日日常笔记")
            return False
    
    if not memory_file:
        possible_memory = [
            'MEMORY.md',
            os.path.join('memory', 'MEMORY.md'),
            os.path.join('13-memory', 'MEMORY.md'),
            os.path.join('20-MEMORY', 'MEMORY.md'),
            # CoPaw 工作区
            r'C:\Users\华为\.copaw\workspaces\default\memory\MEMORY.md',
        ]
        
        for pm in possible_memory:
            if os.path.exists(pm):
                memory_file = pm
                break
        
        if not memory_file:
            print("[ERROR] 未找到 MEMORY.md")
            return False
    
    print(f"[INFO] 实时蒸馏 v3.0")
    print(f"[INFO] 来源：{daily_note_file}")
    print(f"[INFO] 目标：{memory_file}")
    
    # 提取洞察
    insights = extract_key_insights(daily_note_file)
    
    if not insights:
        print("[WARN] 未提取到洞察，可能需要手动整理")
        # 仍然标记为已蒸馏
        update_daily_note_header(daily_note_file, distilled=True)
        return True
    
    print(f"[INFO] 提取到 {len(insights)} 条洞察:")
    for insight in insights:
        print(f"  - [{insight['id']}] {insight['title']}")
    
    # 读取日常笔记内容
    with open(daily_note_file, 'r', encoding='utf-8') as f:
        daily_content = f.read()
    
    # 追加到 MEMORY.md
    success = append_to_memory(memory_file, insights, daily_content)
    
    if not success:
        return False
    
    # 更新日常笔记标记
    update_daily_note_header(daily_note_file, distilled=True)
    
    # 自动 Git 提交
    if auto_commit:
        print("\n[INFO] 触发自动 Git 提交...")
        from memory_git_auto_commit import auto_commit_memory
        auto_commit_memory(memory_file, f"实时蒸馏：添加 {len(insights)} 条记忆")
    
    return True

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='实时蒸馏工具 v3.0')
    parser.add_argument('--daily', type=str, help='日常笔记文件路径')
    parser.add_argument('--memory', type=str, help='MEMORY.md 文件路径')
    parser.add_argument('--no-commit', action='store_true', help='禁用自动 Git 提交')
    
    args = parser.parse_args()
    
    success = real_time_distill(
        daily_note_file=args.daily,
        memory_file=args.memory,
        auto_commit=not args.no_commit
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
