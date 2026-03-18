#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post-Session Compressor - 会话后自动压缩工具

功能:
- 会话结束后自动调用
- 提取关键信息
- 压缩并保存到日常笔记
- 保持上下文<100KB

使用:
  py post_session_compress.py [--auto]
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
SCRIPTS_DIR = WORKSPACE / '30-scripts-tools'


def extract_session_summary() -> Dict:
    """
    从当前会话提取关键信息
    
    实际使用时，这里应该解析会话历史
    简化版：手动输入或从临时文件读取
    """
    # 尝试从临时文件读取会话内容
    temp_file = SCRIPTS_DIR / 'session_temp.json'
    
    if temp_file.exists():
        with open(temp_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        return session_data
    
    # 默认模板
    return {
        'timestamp': datetime.now().isoformat(),
        'topics': [],
        'decisions': [],
        'tools_created': [],
        'files_modified': [],
        'metrics': {},
        'next_actions': []
    }


def compress_to_summary(session: Dict) -> str:
    """压缩会话为结构化摘要"""
    date_str = session['timestamp'][:10]
    
    summary = f"""## Session Summary ({date_str} {session['timestamp'][11:19]})

**Topics:** {', '.join(session['topics']) if session['topics'] else 'N/A'}

**Key Decisions:**
"""
    for i, decision in enumerate(session.get('decisions', [])[:5], 1):
        summary += f"{i}. {decision}\n"
    
    if session.get('tools_created'):
        summary += "\n**Tools Created:**\n"
        for tool in session['tools_created']:
            summary += f"- {tool}\n"
    
    if session.get('files_modified'):
        summary += "\n**Files Modified:**\n"
        for f in session['files_modified']:
            summary += f"- {f}\n"
    
    if session.get('metrics'):
        summary += "\n**Metrics:**\n"
        for key, value in session['metrics'].items():
            summary += f"- {key.replace('_', ' ').title()}: {value}\n"
    
    if session.get('next_actions'):
        summary += "\n**Next Actions:**\n"
        for action in session['next_actions'][:5]:
            summary += f"- {action}\n"
    
    return summary


def save_to_daily(summary: str, date: str = None) -> Path:
    """保存到日常笔记"""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    daily_path = MEMORY_DIR / f"{date}.md"
    
    # 读取或创建文件
    if daily_path.exists():
        content = daily_path.read_text(encoding='utf-8')
        
        # 检查是否已有 Session Summary
        if "## Session Summary" not in content:
            # 添加到末尾
            content += "\n" + summary
        else:
            # 追加新的 summary (带时间戳区分)
            content += "\n" + summary
            
        daily_path.write_text(content, encoding='utf-8')
    else:
        content = f"# {date} - Daily Session\n\n{summary}\n"
        daily_path.write_text(content, encoding='utf-8')
    
    return daily_path


def cleanup_temp():
    """清理临时文件"""
    temp_file = SCRIPTS_DIR / 'session_temp.json'
    if temp_file.exists():
        temp_file.unlink()
        print(f"[OK] Cleaned up temp file")


def verify_context_size() -> Dict:
    """验证上下文大小"""
    core_files = [
        'SOUL.md',
        'USER.md', 
        'AGENTS.md',
        'TOOLS.md',
        'HEARTBEAT.md',
        '13-memory/MEMORY.md',
        '13-memory/' + datetime.now().strftime('%Y-%m-%d') + '.md'
    ]
    
    total_size = 0
    file_sizes = {}
    
    for file_path in core_files:
        full_path = WORKSPACE / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            file_sizes[file_path] = size
            total_size += size
    
    return {
        'total_kb': round(total_size / 1024, 2),
        'total_mb': round(total_size / 1024 / 1024, 4),
        'files': file_sizes,
        'under_limit': total_size < 100 * 1024  # <100KB
    }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Post-Session Compressor')
    parser.add_argument('--auto', action='store_true', help='自动模式 (无交互)')
    parser.add_argument('--verify', action='store_true', help='只验证上下文大小')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Post-Session Compressor - 会话后自动压缩")
    print("=" * 60)
    
    # 验证上下文大小
    context_stats = verify_context_size()
    print(f"\n[Context Size]")
    print(f"  Total: {context_stats['total_kb']}KB ({context_stats['total_mb']}MB)")
    print(f"  Under 100KB limit: {'Yes' if context_stats['under_limit'] else 'No'}")
    
    if args.verify:
        return 0
    
    # 提取会话摘要
    session = extract_session_summary()
    
    if not session['topics'] and not session['decisions']:
        print("\n[WARN] No session data found. Create session_temp.json first.")
        print("\nUsage:")
        print("  1. Create 30-scripts-tools/session_temp.json with session data")
        print("  2. Run: py post_session_compress.py --auto")
        return 0
    
    # 压缩
    summary = compress_to_summary(session)
    print(f"\n[Compressed Summary]")
    print(summary)
    
    # 保存
    daily_path = save_to_daily(summary)
    print(f"\n[OK] Saved to: {daily_path}")
    
    # 清理
    cleanup_temp()
    
    # 最终验证
    final_stats = verify_context_size()
    print(f"\n[Final Context Size]")
    print(f"  Total: {final_stats['total_kb']}KB")
    print(f"  Status: {'OK' if final_stats['under_limit'] else 'OVER LIMIT'}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
