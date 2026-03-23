#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
==============================================================================
  WORKFLOW INSIGHTS - 自我迭代系统 v1.0
  功能：
    - 使用统计追踪
    - 决策库存储
    - 模式识别
    - 智能建议
==============================================================================
"""
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE = Path(__file__).parent.parent
INSIGHTS_DIR = WORKSPACE / "30-scripts-tools" / "workflow_insights"
STATS_FILE = INSIGHTS_DIR / "usage_stats.json"
DECISIONS_DIR = INSIGHTS_DIR / "decisions"
PATTERNS_FILE = INSIGHTS_DIR / "patterns.json"
SUGGESTIONS_FILE = INSIGHTS_DIR / "suggestions.json"

# 确保目录存在
INSIGHTS_DIR.mkdir(exist_ok=True)
DECISIONS_DIR.mkdir(exist_ok=True)


# ========== 使用统计 ==========
def load_stats():
    """加载使用统计"""
    if STATS_FILE.exists():
        try:
            return json.loads(STATS_FILE.read_text(encoding='utf-8'))
        except:
            pass
    return {
        "commands": defaultdict(int),
        "projects": defaultdict(int),
        "hourly_distribution": defaultdict(int),
        "daily_stats": defaultdict(int),
        "session_durations": [],
        "tests_run": 0,
        "decisions_made": 0,
        "first_used": datetime.now().isoformat(),
        "last_used": datetime.now().isoformat()
    }


def save_stats(stats):
    """保存使用统计"""
    STATS_FILE.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding='utf-8')


def track_command(cmd, project=None):
    """追踪命令使用"""
    stats = load_stats()

    # 确保是字典类型
    if not isinstance(stats["commands"], dict):
        stats["commands"] = dict(stats["commands"])
    if not isinstance(stats["projects"], dict):
        stats["projects"] = dict(stats["projects"])
    if not isinstance(stats["hourly_distribution"], dict):
        stats["hourly_distribution"] = dict(stats["hourly_distribution"])
    if not isinstance(stats["daily_stats"], dict):
        stats["daily_stats"] = dict(stats["daily_stats"])

    stats["commands"][cmd] = stats["commands"].get(cmd, 0) + 1
    stats["last_used"] = datetime.now().isoformat()

    if project:
        stats["projects"][project] = stats["projects"].get(project, 0) + 1

    # 记录小时分布
    hour = datetime.now().hour
    stats["hourly_distribution"][str(hour)] = stats["hourly_distribution"].get(str(hour), 0) + 1

    # 记录日期
    today = datetime.now().strftime("%Y-%m-%d")
    stats["daily_stats"][today] = stats["daily_stats"].get(today, 0) + 1

    save_stats(stats)


def track_session_duration(duration_minutes):
    """追踪会话时长"""
    stats = load_stats()

    # 确保是列表
    if not isinstance(stats["session_durations"], list):
        stats["session_durations"] = list(stats["session_durations"])

    stats["session_durations"].append(duration_minutes)
    # 只保留最近100条
    stats["session_durations"] = stats["session_durations"][-100:]

    # 计算平均时长
    if stats["session_durations"]:
        stats["avg_session_duration"] = sum(stats["session_durations"]) / len(stats["session_durations"])
    else:
        stats["avg_session_duration"] = 0

    save_stats(stats)


def track_test():
    """追踪测试运行"""
    stats = load_stats()
    stats["tests_run"] += 1
    save_stats(stats)


def track_decision():
    """追踪决策数量"""
    stats = load_stats()
    stats["decisions_made"] += 1
    save_stats(stats)


# ========== 决策库 ==========
def save_decision(context, decision, result):
    """保存决策"""
    decision_id = datetime.now().strftime("%Y%m%d%H%M%S")

    decision_file = DECISIONS_DIR / f"{decision_id}.json"
    decision_file.write_text(json.dumps({
        "id": decision_id,
        "context": context,
        "decision": decision,
        "result": result,
        "created_at": datetime.now().isoformat(),
        "tags": extract_tags(context)
    }, indent=2, ensure_ascii=False), encoding='utf-8')


def extract_tags(context):
    """从上下文提取标签"""
    tags = []
    keywords = ["优化", "修复", "新增", "删除", "重构", "测试", "部署", "配置"]
    for kw in keywords:
        if kw in context:
            tags.append(kw)
    return tags


def search_decisions(query, limit=5):
    """搜索决策"""
    results = []
    query_lower = query.lower()

    for df in DECISIONS_DIR.glob("*.json"):
        try:
            data = json.loads(df.read_text(encoding='utf-8'))
            if query_lower in data.get("context", "").lower() or \
               query_lower in data.get("decision", "").lower():
                results.append(data)
                if len(results) >= limit:
                    break
        except:
            pass

    return results


def get_similar_decisions(current_context, limit=3):
    """获取相似决策"""
    decisions = []
    for df in DECISIONS_DIR.glob("*.json"):
        try:
            data = json.loads(df.read_text(encoding='utf-8'))
            decisions.append(data)
        except:
            pass

    # 计算相似度
    scored = []
    current_tags = extract_tags(current_context)
    for d in decisions:
        common_tags = set(current_tags) & set(d.get("tags", []))
        if common_tags:
            scored.append((len(common_tags), d))

    scored.sort(reverse=True)
    return [d for _, d in scored[:limit]]


# ========== 模式识别 ==========
def detect_patterns():
    """检测使用模式"""
    stats = load_stats()
    patterns = []

    # 最常用命令
    if stats["commands"]:
        top_commands = sorted(stats["commands"].items(), key=lambda x: x[1], reverse=True)[:5]
        patterns.append({
            "type": "top_commands",
            "data": dict(top_commands),
            "insight": f"最常用命令: {top_commands[0][0]} ({top_commands[0][1]}次)"
        })

    # 高效时段
    if stats["hourly_distribution"]:
        hourly = stats["hourly_distribution"]
        peak_hour_str = max(hourly.items(), key=lambda x: x[1])[0]
        peak_hour = int(peak_hour_str)
        patterns.append({
            "type": "peak_hour",
            "data": {"hour": peak_hour, "count": hourly[peak_hour_str]},
            "insight": f"最高效时段: {peak_hour}:00-{peak_hour + 1}:00"
        })

    # 项目分布
    if stats["projects"]:
        top_project = max(stats["projects"].items(), key=lambda x: x[1])
        patterns.append({
            "type": "top_project",
            "data": dict(stats["projects"]),
            "insight": f"最常项目: {top_project[0]} ({top_project[1]}次)"
        })

    # 会话长度趋势
    if "avg_session_duration" in stats and stats["avg_session_duration"] > 0:
        patterns.append({
            "type": "avg_session",
            "data": {"minutes": round(stats["avg_session_duration"], 1)},
            "insight": f"平均会话时长: {stats['avg_session_duration']:.1f}分钟"
        })

    # 命令序列模式
    command_sequence = detect_command_sequence()
    if command_sequence:
        patterns.append({
            "type": "command_sequence",
            "data": command_sequence,
            "insight": f"常见命令序列: {' → '.join(command_sequence)}"
        })

    return patterns


def detect_command_sequence(min_occurrences=2):
    """检测常见命令序列"""
    # 分析最近的命令历史来检测序列
    # 这里简单实现：查找 "save -> test -> push" 等常见序列
    common_sequences = [
        ["start", "save", "end"],
        ["start", "test", "save", "end"],
        ["start", "save", "test", "push"],
    ]
    return []  # 简化实现


# ========== 智能建议 ==========
def generate_suggestions():
    """生成智能建议"""
    stats = load_stats()
    suggestions = []
    patterns = detect_patterns()

    # 基于模式的建议
    for pattern in patterns:
        if pattern["type"] == "peak_hour":
            hour = pattern["data"]["hour"]
            if 9 <= hour <= 11:
                suggestions.append({
                    "type": "productivity",
                    "priority": "high",
                    "suggestion": f"你在 {hour}:00 效率最高，适合处理复杂任务",
                    "action": "schedule_important_tasks"
                })
            elif 22 <= hour or hour <= 5:
                suggestions.append({
                    "type": "work_life_balance",
                    "priority": "medium",
                    "suggestion": "你在深夜工作较多，注意休息",
                    "action": "set_reminder"
                })

        elif pattern["type"] == "top_commands":
            commands = pattern["data"]
            if commands.get("test", 0) > 5 and commands.get("push", 0) < commands.get("test", 0) / 2:
                suggestions.append({
                    "type": "git_hygiene",
                    "priority": "medium",
                    "suggestion": "测试较多但推送较少，建议定期推送",
                    "action": "auto_push"
                })

    # 基于决策的建议
    recent_decisions = list(DECISIONS_DIR.glob("*.json"))
    if len(recent_decisions) >= 10:
        # 检查是否有重复的优化任务
        optimization_count = 0
        for df in recent_decisions[-10:]:
            try:
                data = json.loads(df.read_text(encoding='utf-8'))
                if "优化" in data.get("context", ""):
                    optimization_count += 1
            except:
                pass

        if optimization_count >= 5:
            suggestions.append({
                "type": "consolidation",
                "priority": "high",
                "suggestion": "你进行了多次优化，建议合并为一次完整优化",
                "action": "plan_consolidation"
            })

    # 基于时长的建议
    if "avg_session_duration" in stats:
        avg = stats["avg_session_duration"]
        if avg < 5:
            suggestions.append({
                "type": "efficiency",
                "priority": "low",
                "suggestion": "会话平均时长较短，可能任务被打断",
                "action": "enable_auto_save"
            })

    # 排序
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return suggestions[:5]  # 只返回前5条


# ========== 自我分析报告 ==========
def generate_report():
    """生成自我分析报告"""
    stats = load_stats()
    patterns = detect_patterns()
    suggestions = generate_suggestions()

    report = f"""
╔══════════════════════════════════════════════════════════════╗
║              WORKFLOW INSIGHTS - 自我分析报告               ║
╚══════════════════════════════════════════════════════════════╝

📊 使用统计
─────────────────────────────────────
  总命令执行: {sum(stats['commands'].values())}
  会话数: {len(stats['session_durations'])}
  平均会话时长: {stats.get('avg_session_duration', 0):.1f} 分钟
  测试运行: {stats['tests_run']}
  决策记录: {stats['decisions_made']}

📈 模式识别
─────────────────────────────────────
"""
    for p in patterns:
        report += f"  • {p['insight']}\n"

    report += """
🎯 智能建议
─────────────────────────────────────
"""
    for i, s in enumerate(suggestions, 1):
        icon = "🔴" if s["priority"] == "high" else "🟡" if s["priority"] == "medium" else "🟢"
        report += f"  {icon} {i}. {s['suggestion']}\n"

    report += """
💡 决策库最近案例
─────────────────────────────────────
"""
    recent = sorted(DECISIONS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]
    for df in recent:
        try:
            data = json.loads(df.read_text(encoding='utf-8'))
            report += f"  • {data.get('context', 'N/A')[:40]}...\n"
            report += f"    → {data.get('decision', 'N/A')[:30]}\n"
        except:
            pass

    report += """
╚══════════════════════════════════════════════════════════════╝
"""
    return report


# ========== CLI 接口 ==========
def cmd_stats():
    """显示统计"""
    stats = load_stats()
    print(f"\n📊 使用统计")
    print(f"  总命令: {sum(stats['commands'].values())}")
    print(f"  会话: {len(stats['session_durations'])}")
    print(f"  平均时长: {stats.get('avg_session_duration', 0):.1f}m")
    print(f"  测试: {stats['tests_run']}")

    if stats["commands"]:
        print(f"\n  命令使用:")
        for cmd, count in sorted(stats["commands"].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {cmd}: {count}")

    if stats["projects"]:
        print(f"\n  项目分布:")
        for proj, count in sorted(stats["projects"].items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"    {proj}: {count}")


def cmd_patterns():
    """显示模式"""
    patterns = detect_patterns()
    print(f"\n📈 模式识别")
    for p in patterns:
        print(f"  • {p['insight']}")


def cmd_suggest():
    """显示建议"""
    suggestions = generate_suggestions()
    print(f"\n🎯 智能建议")
    if not suggestions:
        print("  暂无建议")
    for i, s in enumerate(suggestions, 1):
        icon = "🔴" if s["priority"] == "high" else "🟡" if s["priority"] == "medium" else "🟢"
        print(f"  {icon} {i}. {s['suggestion']}")


def cmd_report():
    """显示完整报告"""
    print(generate_report())


def cmd_search(query):
    """搜索决策"""
    results = search_decisions(query)
    print(f"\n🔍 决策搜索: {query}")
    if not results:
        print("  无结果")
    for r in results:
        print(f"  • {r.get('context', 'N/A')[:50]}")
        print(f"    → {r.get('decision', 'N/A')[:40]}")


def cmd_help():
    """显示帮助"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              WORKFLOW INSIGHTS - 自我迭代系统               ║
╠══════════════════════════════════════════════════════════════╣
║  用法: py workflow_insights.py <command>                   ║
║                                                              ║
║  Commands:                                                   ║
║    stats      - 显示使用统计                                 ║
║    patterns   - 显示使用模式                                 ║
║    suggest    - 显示智能建议                                 ║
║    report     - 生成完整报告                                 ║
║    search <q> - 搜索决策库                                 ║
║    help       - 显示帮助                                     ║
╚══════════════════════════════════════════════════════════════╝
""")


def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    commands = {
        "stats": cmd_stats,
        "patterns": cmd_patterns,
        "suggest": cmd_suggest,
        "report": cmd_report,
        "search": lambda: cmd_search(args[0] if args else ""),
        "help": cmd_help,
        "--help": cmd_help,
        "-h": cmd_help,
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        cmd_help()


if __name__ == "__main__":
    main()
