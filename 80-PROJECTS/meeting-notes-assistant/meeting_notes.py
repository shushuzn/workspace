#!/usr/bin/env python3
"""
会议纪要助手 - Meeting Notes Assistant
输入会议讨论要点，自动整理成结构化的 Markdown 格式
"""

import sys
import re
from datetime import datetime
from typing import List, Dict


def parse_input(raw_text: str) -> Dict:
    """解析输入文本，提取各部分内容"""
    lines = raw_text.strip().split('\n')
    
    result = {
        'title': '',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'attendees': [],
        'discussions': [],
        'action_items': [],
        'next_meeting': ''
    }
    
    current_section = 'discussions'
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检测标题
        if line.startswith('# '):
            result['title'] = line[2:].strip()
            continue
            
        # 检测日期
        if line.startswith('日期:'):
            result['date'] = line[3:].strip()
            continue
            
        # 检测参会人
        if line.startswith('参会人:'):
            attendees_str = line[4:].strip()
            result['attendees'] = [a.strip() for a in attendees_str.split(',')]
            continue
            
        # 检测下一会议
        if line.startswith('下次会议:'):
            result['next_meeting'] = line[5:].strip()
            continue
            
        # 检测待办事项
        if line.startswith('- [ ]') or line.startswith('- [x]'):
            result['action_items'].append(line)
            continue
            
        # 其他内容作为讨论要点
        if line.startswith('- '):
            result['discussions'].append(line[2:].strip())
        elif line.startswith('* '):
            result['discussions'].append(line[2:].strip())
        else:
            result['discussions'].append(line)
    
    return result


def format_discussions(discussions: List[str]) -> str:
    """格式化讨论要点"""
    if not discussions:
        return "- （无）"
    
    formatted = []
    for i, d in enumerate(discussions, 1):
        formatted.append(f"{i}. {d}")
    return '\n'.join(formatted)


def format_action_items(action_items: List[str]) -> str:
    """格式化待办事项"""
    if not action_items:
        return "- [ ] （无）"
    return '\n'.join(action_items)


def generate_markdown(data: Dict) -> str:
    """生成 Markdown 格式的会议纪要"""
    
    md = f"""# {data['title'] or '会议纪要'}

## 基本信息

- **日期**: {data['date']}
- **参会人**: {', '.join(data['attendees']) if data['attendees'] else '（未记录）'}
- **下次会议**: {data['next_meeting'] or '（待定）'}

## 讨论要点

{format_discussions(data['discussions'])}

## 待办事项

{format_action_items(data['action_items'])}

---

*本纪要由 Meeting Notes Assistant 自动生成*
"""
    
    return md.strip()


def main():
    print("=" * 50)
    print("       会议纪要助手 Meeting Notes Assistant")
    print("=" * 50)
    print()
    print("输入格式示例:")
    print("  # 项目周会")
    print("  日期: 2024-01-15")
    print("  参会人: 张三, 李四, 王五")
    print("  讨论了A功能开发进度")
    print("  讨论了B问题解决方案")
    print("  - [ ] 张三：完成功能A")
    print("  - [ ] 李四：修复BUG")
    print("  下次会议: 2024-01-22")
    print()
    print("-" * 50)
    print("请粘贴会议内容（输入空行结束）:")
    print("-" * 50)
    
    # 读取多行输入
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == '':
                break
            lines.append(line)
        except EOFError:
            break
    
    raw_text = '\n'.join(lines)
    
    if not raw_text.strip():
        print("错误: 未输入内容")
        sys.exit(1)
    
    # 解析并生成
    data = parse_input(raw_text)
    markdown = generate_markdown(data)
    
    print()
    print("=" * 50)
    print("生成的会议纪要:")
    print("=" * 50)
    print()
    print(markdown)
    print()
    
    # 可选：保存到文件
    save = input("是否保存到文件? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("输入文件名 (默认: meeting_notes.md): ").strip()
        if not filename:
            filename = "meeting_notes.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"已保存到: {filename}")


if __name__ == "__main__":
    main()
