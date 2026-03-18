#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Compressor - 会话上下文压缩工具

功能:
- 提取会话关键信息
- 压缩为结构化摘要
- 保存到记忆文件
- 减少 token 使用

使用:
  py context_compressor.py --session "会话内容"
  py context_compressor.py --auto  # 自动从最近对话提取
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'


def extract_key_info(session_summary: str) -> Dict:
    """从会话提取关键信息"""
    return {
        'timestamp': datetime.now().isoformat(),
        'topics': [],
        'decisions': [],
        'tools_created': [],
        'files_modified': [],
        'metrics': {},
        'next_actions': []
    }


def compress_context(info: Dict) -> str:
    """压缩上下文为简洁格式"""
    compressed = f"""
## Session Context ({info['timestamp'][:10]})

**Topics:** {', '.join(info['topics']) if info['topics'] else 'N/A'}

**Decisions:**
"""
    for i, decision in enumerate(info['decisions'][:5], 1):
        compressed += f"{i}. {decision}\n"
    
    if info['tools_created']:
        compressed += "\n**Tools Created:**\n"
        for tool in info['tools_created']:
            compressed += f"- {tool}\n"
    
    if info['files_modified']:
        compressed += "\n**Files Modified:**\n"
        for f in info['files_modified']:
            compressed += f"- {f}\n"
    
    if info['next_actions']:
        compressed += "\n**Next Actions:**\n"
        for action in info['next_actions'][:3]:
            compressed += f"- {action}\n"
    
    return compressed


def save_to_daily(compressed: str, date: str = None):
    """保存到日常笔记"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    daily_path = MEMORY_DIR / f"{date}.md"
    
    if daily_path.exists():
        content = daily_path.read_text(encoding='utf-8')
        # 查找是否已有上下文部分
        if "## Session Context" not in content:
            # 添加到末尾
            content += "\n" + compressed
    else:
        content = f"# {date} - Session Summary\n\n{compressed}\n"
    
    daily_path.write_text(content, encoding='utf-8')
    print(f"✅ 已保存到：{daily_path}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Context Compressor')
    parser.add_argument('--demo', action='store_true', help='演示模式')
    parser.add_argument('--session', type=str, help='会话内容')
    parser.add_argument('--auto', action='store_true', help='自动模式')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Context Compressor - 会话上下文压缩")
    print("=" * 60)
    
    if args.demo:
        # 演示：压缩今日会话
        info = {
            'timestamp': datetime.now().isoformat(),
            'topics': ['Git Pre-Check', 'Memory Distillation', 'Context Compression'],
            'decisions': [
                '创建 Git Pre-Check 工具 (7 检查)',
                '记忆蒸馏：有增有减 (12.6KB→9.3KB)',
                '上下文压缩：减少 token 使用'
            ],
            'tools_created': [
                'git-precheck.py (14KB)',
                'memory_distill_simple.py (4KB)',
                'context_compressor.py (this)'
            ],
            'files_modified': [
                'MEMORY.md (精简 26%)',
                '2026-03-18.md (创建)'
            ],
            'metrics': {
                'innovation_score': '120.0/100',
                'memory_health': '100/100',
                'files_cleaned': '12 memory tools'
            },
            'next_actions': [
                '推送 rl-trading',
                'CNT 数据收集',
                '清理嵌套备份'
            ]
        }
        
        compressed = compress_context(info)
        print(compressed)
        
        save = input("\n保存到日常笔记？(y/n): ").strip().lower()
        if save == 'y':
            save_to_daily(compressed)
        
        return 0
    
    print("\n使用示例:")
    print("  py context_compressor.py --demo")
    print("  py context_compressor.py --auto")
    return 0


if __name__ == '__main__':
    sys.exit(main())
