#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post-Session Compressor v2.0 - 分层压缩 + 重要性评估

功能:
- 会话结束后自动调用
- 分层压缩策略（热/温/冷数据）
- 重要性评估（质量评分）
- 保持上下文<100KB

压缩层级:
- Layer 1 (0-7 天): 热数据 - 保留原始，轻度压缩
- Layer 2 (7-30 天): 温数据 - 提取关键决策
- Layer 3 (>30 天): 冷数据 - 蒸馏到 MEMORY.md

使用:
  py post_session_compress.py [--auto] [--tiered]
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'
SCRIPTS_DIR = WORKSPACE / '30-scripts-tools'


# ============================================================================
# 重要性评估 (Importance-Aware Compression)
# ============================================================================

def calculate_importance(session: Dict) -> float:
    """
    计算会话重要性评分 (0-1)
    
    因素:
    - frequency: 被引用次数 (0.3)
    - recency: 时间衰减 (0.2)
    - uniqueness: 信息熵/独特性 (0.25)
    - actionability: 可执行性 (0.15)
    - emotional_weight: 关键决策 (0.1)
    """
    score = 0.0
    
    # 1. 可执行性 (15%) - 有 next_actions
    actionability = min(len(session.get('next_actions', [])) / 5, 1.0)
    score += actionability * 0.15
    
    # 2. 关键决策 (10%) - 有重大决策
    decisions = session.get('decisions', [])
    critical_keywords = ['architecture', 'critical', 'major', 'phase', 'complete']
    critical_decisions = sum(1 for d in decisions if any(kw in d.lower() for kw in critical_keywords))
    emotional_weight = min(critical_decisions / 3, 1.0)
    score += emotional_weight * 0.10
    
    # 3. 独特性 (25%) - 创建了新工具/文件
    tools_created = len(session.get('tools_created', []))
    files_modified = len(session.get('files_modified', []))
    uniqueness = min((tools_created + files_modified) / 10, 1.0)
    score += uniqueness * 0.25
    
    # 4. 时间衰减 (20%) - 越近越重要
    timestamp = session.get('timestamp', datetime.now().isoformat())
    try:
        session_time = datetime.fromisoformat(timestamp)
        days_old = (datetime.now() - session_time).days
        recency = max(0, 1.0 - (days_old / 30))  # 30 天后衰减到 0
        score += recency * 0.20
    except:
        score += 0.20  # 默认满分
    
    # 5. 被引用次数 (30%) - 简化版：根据 topics 数量估算
    topics = len(session.get('topics', []))
    frequency = min(topics / 5, 1.0)
    score += frequency * 0.30
    
    return min(score, 1.0)


def get_compression_strategy(importance: float) -> str:
    """根据重要性选择压缩策略"""
    if importance >= 0.8:
        return "retain_full"  # 完整保留
    elif importance >= 0.5:
        return "compress_light"  # 轻度压缩
    elif importance >= 0.3:
        return "compress_heavy"  # 重度压缩
    else:
        return "archive_only"  # 仅归档


# ============================================================================
# 分层压缩 (Tiered Compression)
# ============================================================================

def get_tier(days_old: int) -> str:
    """根据天数确定数据层级"""
    if days_old <= 7:
        return "hot"  # 热数据
    elif days_old <= 30:
        return "warm"  # 温数据
    else:
        return "cold"  # 冷数据


def compress_tiered(session: Dict, tier: str, importance: float) -> str:
    """
    分层压缩
    
    - Hot (0-7 天): 保留 80% 内容，只压缩格式
    - Warm (7-30 天): 保留 50% 内容，提取关键决策
    - Cold (>30 天): 保留 20% 内容，蒸馏到 MEMORY
    """
    importance_strategy = get_compression_strategy(importance)
    
    # 高重要性内容升级处理
    if importance_strategy == "retain_full" and tier == "warm":
        tier = "hot"  # 升级为热数据处理
    elif importance_strategy == "archive_only" and tier == "hot":
        tier = "warm"  # 降级为温数据处理
    
    if tier == "hot":
        return compress_hot(session)
    elif tier == "warm":
        return compress_warm(session)
    else:  # cold
        return compress_cold(session)


def compress_hot(session: Dict) -> str:
    """热数据压缩 - 保留 80% 内容"""
    date_str = session['timestamp'][:10]
    time_str = session['timestamp'][11:19]
    
    summary = f"""## Session Summary ({date_str} {time_str}) 🔥 HOT

**Importance Score:** {calculate_importance(session):.2f}

**Topics:** {', '.join(session['topics']) if session['topics'] else 'N/A'}

**Key Decisions:**
"""
    for i, decision in enumerate(session.get('decisions', [])[:10], 1):  # 最多 10 个
        summary += f"{i}. {decision}\n"
    
    if session.get('tools_created'):
        summary += "\n**Tools Created:**\n"
        for tool in session['tools_created']:
            summary += f"- {tool}\n"
    
    if session.get('files_modified'):
        summary += "\n**Files Modified:**\n"
        for f in session['files_modified'][:15]:  # 最多 15 个
            summary += f"- {f}\n"
    
    if session.get('metrics'):
        summary += "\n**Metrics:**\n"
        for key, value in session['metrics'].items():
            summary += f"- {key.replace('_', ' ').title()}: {value}\n"
    
    if session.get('next_actions'):
        summary += "\n**Next Actions:**\n"
        for action in session['next_actions'][:10]:  # 最多 10 个
            summary += f"- {action}\n"
    
    # 保留详细 notes（热数据特性）
    if session.get('notes'):
        summary += "\n**Detailed Notes:**\n"
        summary += session['notes'][:2000] + "..." if len(session.get('notes', '')) > 2000 else session['notes']
    
    return summary


def compress_warm(session: Dict) -> str:
    """温数据压缩 - 保留 50% 内容"""
    date_str = session['timestamp'][:10]
    
    summary = f"""## Session Summary ({date_str}) 🔶 WARM

**Importance Score:** {calculate_importance(session):.2f}

**Key Decisions (Top 5):**
"""
    for i, decision in enumerate(session.get('decisions', [])[:5], 1):
        summary += f"{i}. {decision}\n"
    
    if session.get('tools_created'):
        summary += "\n**Tools:** " + ", ".join(session['tools_created'][:5])
    
    if session.get('files_modified'):
        summary += "\n**Files:** " + ", ".join(session['files_modified'][:10])
    
    if session.get('metrics'):
        summary += "\n**Key Metrics:**\n"
        for key, value in list(session['metrics'].items())[:5]:
            summary += f"- {key.replace('_', ' ').title()}: {value}\n"
    
    if session.get('next_actions'):
        summary += "\n**Next Actions:**\n"
        for action in session['next_actions'][:5]:
            summary += f"- {action}\n"
    
    return summary


def compress_cold(session: Dict) -> str:
    """冷数据压缩 - 保留 20% 内容，蒸馏到 MEMORY"""
    date_str = session['timestamp'][:10]
    
    # 提取最关键的 3 个决策
    decisions = session.get('decisions', [])[:3]
    
    if not decisions:
        return ""  # 无关键内容，跳过
    
    summary = f"""## Session Summary ({date_str}) ❄️ COLD → MEMORY.md

**Distilled Insights:**
"""
    for i, decision in enumerate(decisions, 1):
        summary += f"{i}. {decision}\n"
    
    # 只保留高价值工具
    if session.get('tools_created'):
        high_value_tools = [t for t in session['tools_created'] if any(
            kw in t.lower() for kw in ['critical', 'core', 'engine', 'system']
        )][:2]
        if high_value_tools:
            summary += "\n**Core Tools:** " + ", ".join(high_value_tools)
    
    # 标记为已蒸馏到 MEMORY.md
    summary += "\n\n> 📌 Full details distilled to MEMORY.md"
    
    return summary


# ============================================================================
# 原有函数（保留兼容性）
# ============================================================================

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
        'next_actions': [],
        'notes': ''
    }


def compress_to_summary(session: Dict) -> str:
    """压缩会话为结构化摘要（v1.0 兼容版）"""
    return compress_hot(session)  # 默认使用热数据压缩


def save_to_daily(summary: str, date: str = None, tier: str = "hot") -> Path:
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


def process_old_notes(tier_threshold_days: Dict = None):
    """
    处理旧笔记 - 分层压缩
    
    Args:
        tier_threshold_days: 层级阈值，默认 {hot: 7, warm: 30, cold: >30}
    """
    if tier_threshold_days is None:
        tier_threshold_days = {
            'hot': 7,
            'warm': 30
        }
    
    print("\n" + "=" * 60)
    print("Processing Old Notes - Tiered Compression")
    print("=" * 60)
    
    if not MEMORY_DIR.exists():
        print("[SKIP] Memory directory not found")
        return
    
    # 获取所有日常笔记
    daily_notes = sorted([f for f in MEMORY_DIR.glob("*.md") if f.stem != "MEMORY"])
    
    stats = {'hot': 0, 'warm': 0, 'cold': 0, 'processed': 0}
    
    for note_file in daily_notes:
        try:
            # 解析日期
            note_date = datetime.strptime(note_file.stem, '%Y-%m-%d')
            days_old = (datetime.now() - note_date).days
            
            # 确定层级
            tier = get_tier(days_old)
            stats[tier] += 1
            
            # 跳过今天和昨天的笔记
            if days_old < 2:
                continue
            
            # 读取笔记
            content = note_file.read_text(encoding='utf-8')
            
            # 简单压缩：移除多余空行
            compressed = re.sub(r'\n{3,}', '\n\n', content)
            compressed = '\n'.join(line.rstrip() for line in compressed.split('\n'))
            
            # 保存压缩后的内容
            original_size = len(content)
            compressed_size = len(compressed)
            savings = original_size - compressed_size
            
            if savings > 0:
                note_file.write_text(compressed, encoding='utf-8')
                savings_pct = (savings / original_size * 100) if original_size > 0 else 0
                print(f"  [{tier.upper()}] {note_file.stem}: {original_size} → {compressed_size} bytes (-{savings_pct:.1f}%)")
                stats['processed'] += 1
            
        except Exception as e:
            print(f"  [ERROR] {note_file.name}: {e}")
    
    print(f"\n[Summary] Hot: {stats['hot']}, Warm: {stats['warm']}, Cold: {stats['cold']}, Processed: {stats['processed']}")


def update_memory_index():
    """更新记忆索引"""
    index_generator = SCRIPTS_DIR / 'memory_index_generator.py'
    
    if not index_generator.exists():
        print(f"[MEMORY] Index generator not found, skipping")
        return
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, str(index_generator)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        for line in result.stdout.split('\n'):
            if line.strip() and ('Found' in line or 'Tags' in line or 'DONE' in line):
                print(f"[MEMORY] {line.strip()}")
    except Exception as e:
        print(f"[MEMORY] Error updating index: {e}")


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
    
    parser = argparse.ArgumentParser(description='Post-Session Compressor v2.0')
    parser.add_argument('--auto', action='store_true', help='自动模式 (无交互)')
    parser.add_argument('--verify', action='store_true', help='只验证上下文大小')
    parser.add_argument('--tiered', action='store_true', help='启用分层压缩')
    parser.add_argument('--process-old', action='store_true', help='处理旧笔记')
    parser.add_argument('--importance', action='store_true', help='显示重要性评分')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Post-Session Compressor v2.0 - 分层压缩 + 重要性评估")
    print("=" * 60)
    
    # 验证上下文大小
    context_stats = verify_context_size()
    print(f"\n[Context Size]")
    print(f"  Total: {context_stats['total_kb']}KB ({context_stats['total_mb']}MB)")
    print(f"  Under 100KB limit: {'Yes' if context_stats['under_limit'] else 'No'}")
    
    if args.verify:
        return 0
    
    # 处理旧笔记
    if args.process_old:
        process_old_notes()
        return 0
    
    # 提取会话摘要
    session = extract_session_summary()
    
    if not session['topics'] and not session['decisions']:
        print("\n[WARN] No session data found. Create session_temp.json first.")
        print("\nUsage:")
        print("  1. Create 30-scripts-tools/session_temp.json with session data")
        print("  2. Run: py post_session_compress.py --auto")
        return 0
    
    # 计算重要性
    importance = calculate_importance(session)
    print(f"\n[Importance Score] {importance:.2f} / 1.00")
    print(f"[Compression Strategy] {get_compression_strategy(importance)}")
    
    # 分层压缩
    if args.tiered:
        # 根据会话时间确定层级
        try:
            session_time = datetime.fromisoformat(session['timestamp'])
            days_old = (datetime.now() - session_time).days
            tier = get_tier(days_old)
            print(f"[Data Tier] {tier.upper()} ({days_old} days old)")
        except:
            tier = "hot"
        
        summary = compress_tiered(session, tier, importance)
    else:
        # 默认使用热数据压缩（v1.0 兼容）
        summary = compress_to_summary(session)
    
    print(f"\n[Compressed Summary]")
    print(summary[:500] + "..." if len(summary) > 500 else summary)
    
    # 保存
    daily_path = save_to_daily(summary)
    print(f"\n[OK] Saved to: {daily_path}")
    
    # 更新记忆索引
    update_memory_index()
    
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
