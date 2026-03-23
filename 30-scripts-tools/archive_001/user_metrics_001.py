#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
USER-METRICS-001 用户表现指标追踪系统

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
# Purpose:
#     - 追踪用户工作流执行表现
#     - 分析认知负荷和注意力指标
#     - 检测训练迁移效应 (基于论文 2603.09753)
# Data Flow:
#     session_data -> track() -> metrics.json -> analyze() -> report
# Files:
#     - user_metrics_001.py (主工具)
#     - .user_metrics.json (指标存储)
# Edge Cases:
#     - 无历史数据 -> 返回基线
#     - 数据损坏 -> 重置指标
#     - 新用户 -> 创建新档案
# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================
"""
import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

METRICS_FILE = Path(".user_metrics.json")

METRIC_TEMPLATES = {
    "attention": {
        "avg_response_time": 0.0,
        "focus_score": 0.0,
        "attention_shifts": 0,
    },
    "memory": {
        "info_retention_rate": 0.0,
        "working_memory_load": 0.0,
    },
    "executive": {
        "task_completion_rate": 0.0,
        "error_recovery_time": 0.0,
    },
    "transfer": {
        "cross_task_improvement": 0.0,
        "skill_retention": 0.0,
        "generalization_score": 0.0,
        "learning_velocity": 0.0,
    },
}


def load_metrics():
    """加载或初始化指标"""
    if METRICS_FILE.exists():
        try:
            return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    return {
        "user_id": "default",
        "created_at": datetime.now().isoformat(),
        "total_sessions": 0,
        "metrics": METRIC_TEMPLATES.copy(),
        "session_history": [],
    }


def save_metrics(data):
    """保存指标"""
    METRICS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def track_session(session_data):
    """追踪单个会话的表现数据"""
    metrics = load_metrics()

    session_record = {
        "session_id": session_data.get("session_id", "unknown"),
        "timestamp": datetime.now().isoformat(),
        "workflow_id": session_data.get("workflow_id", ""),
        "duration": session_data.get("duration", 0),
        "steps_completed": session_data.get("steps_completed", 0),
        "errors": session_data.get("errors", 0),
        "tool_count": session_data.get("tool_count", 0),
    }

    metrics["session_history"].append(session_record)
    metrics["total_sessions"] += 1

    recent = metrics["session_history"][-10:]

    # 注意力指标
    if recent:
        times = [s.get("duration", 0) / max(1, s.get("steps_completed", 1)) for s in recent]
        metrics["metrics"]["attention"]["avg_response_time"] = sum(times) / len(times)
        metrics["metrics"]["attention"]["attention_shifts"] = len(recent)
        variance = sum((t - metrics["metrics"]["attention"]["avg_response_time"])**2 for t in times) / len(times)
        metrics["metrics"]["attention"]["focus_score"] = max(0, 100 - variance * 10)

    # 记忆指标
    if recent:
        rates = [s.get("steps_completed", 0) / max(1, s.get("duration", 1)) for s in recent]
        metrics["metrics"]["memory"]["info_retention_rate"] = sum(rates) / len(rates) * 100
        metrics["metrics"]["memory"]["working_memory_load"] = min(100,
            len(set(s.get("workflow_id", "") for s in recent)) * 10)

    # 执行功能
    if recent:
        errors = sum(s.get("errors", 0) for s in recent)
        steps = sum(s.get("steps_completed", 0) for s in recent)
        metrics["metrics"]["executive"]["task_completion_rate"] = (steps - errors) / max(1, steps) * 100

    # 训练迁移 (论文核心发现)
    if len(recent) >= 3:
        first = recent[:len(recent) //3]
        last = recent[-len(recent) //3:]
        first_avg = sum(s.get("steps_completed", 0) / max(1, s.get("duration", 1)) for s in first) / len(first)
        last_avg = sum(s.get("steps_completed", 0) / max(1, s.get("duration", 1)) for s in last) / len(last)
        improvement = (last_avg - first_avg) / max(0.001, first_avg) * 100
        metrics["metrics"]["transfer"]["cross_task_improvement"] = improvement
        metrics["metrics"]["transfer"]["skill_retention"] = max(0, min(100, 80 + improvement * 0.5))
        metrics["metrics"]["transfer"]["generalization_score"] = min(100, improvement * 2)
        metrics["metrics"]["transfer"]["learning_velocity"] = improvement / len(recent)

    save_metrics(metrics)
    return metrics["metrics"]


def analyze_performance():
    """分析用户整体表现"""
    metrics = load_metrics()

    print("=" * 60)
    print("USER PERFORMANCE REPORT")
    print("=" * 60)
    print(f"Total Sessions: {metrics['total_sessions']}")
    print("-" * 60)

    att = metrics["metrics"]["attention"]
    print("\n[ATTENTION]")
    print(f"  Avg Response: {att['avg_response_time']:.2f}s")
    print(f"  Focus Score: {att['focus_score']:.1f}/100")

    mem = metrics["metrics"]["memory"]
    print("\n[MEMORY]")
    print(f"  Retention: {mem['info_retention_rate']:.1f}%")
    print(f"  WM Load: {mem['working_memory_load']:.1f}%")

    exe = metrics["metrics"]["executive"]
    print("\n[EXECUTIVE]")
    print(f"  Completion Rate: {exe['task_completion_rate']:.1f}%")

    tra = metrics["metrics"]["transfer"]
    print("\n[TRANSFER LEARNING]")
    print(f"  Cross-Task Improvement: {tra['cross_task_improvement']:.1f}%")
    print(f"  Generalization: {tra['generalization_score']:.1f}/100")
    print(f"  Learning Velocity: {tra['learning_velocity']:.2f}")
    print("=" * 60)


def main():
    import sys

    if len(sys.argv) < 2:
        print("USER-METRICS-001 Usage:")
        print("  py user_metrics_001.py --analyze")
        print("  py user_metrics_001.py --track <workflow_id> <duration> <steps>")
        return

    if sys.argv[1] == "--analyze":
        analyze_performance()
    elif sys.argv[1] == "--track" and len(sys.argv) >= 5:
        track_session({
            "workflow_id": sys.argv[2],
            "duration": int(sys.argv[3]),
            "steps_completed": int(sys.argv[4]),
            "errors": int(sys.argv[5]) if len(sys.argv) > 5 else 0,
        })
        print("[OK] Session tracked")


# ==============================================================================
# STAGE 3: ASK 询问确认
# py user_metrics_001.py --analyze  # Run verification
# ==============================================================================

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases
    1. First run -> Create baseline
    2. Track session -> Update metrics
    3. Analyze -> Show report
"""


if __name__ == "__main__":
    main()
