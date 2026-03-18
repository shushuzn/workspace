#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heartbeat Lite - 精简版心跳系统
替代原有的 3 个 heartbeat 工具 (964 行 → 150 行)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# 工作区根目录
WORKSPACE_ROOT = Path(__file__).parent.parent
STATE_FILE = WORKSPACE_ROOT / "13-memory" / "heartbeat-state.json"
HEARTBEAT_FILE = WORKSPACE_ROOT / "HEARTBEAT.md"

def load_state():
    """加载心跳状态"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "last_check": None,
        "current_article": None,
        "status": "idle",
        "checks": {}
    }

def save_state(state):
    """保存心跳状态"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def check_status():
    """检查心跳状态"""
    state = load_state()
    print("=" * 60)
    print("Heartbeat Status")
    print("=" * 60)
    print(f"Last Check: {state.get('last_check', 'Never')}")
    print(f"Current Article: {state.get('current_article', 'None')}")
    print(f"Status: {state.get('status', 'idle')}")
    
    checks = state.get('checks', {})
    if checks:
        print("\nChecks:")
        for key, value in checks.items():
            print(f"  - {key}: {value}")
    
    print("=" * 60)
    return state

def reset():
    """重置心跳状态"""
    state = {
        "last_check": None,
        "current_article": None,
        "status": "idle",
        "checks": {}
    }
    save_state(state)
    print("✅ Heartbeat state reset")

def trigger():
    """触发心跳"""
    state = load_state()
    state["last_check"] = datetime.now().isoformat()
    state["status"] = "running"
    save_state(state)
    
    # 读取 HEARTBEAT.md
    if HEARTBEAT_FILE.exists():
        with open(HEARTBEAT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取核心规则
            if "⚠️ 核心规则" in content:
                rules = content.split("⚠️ 核心规则")[1].split("---")[0]
                print(rules)
    
    print(f"\n✅ Heartbeat triggered at {state['last_check']}")
    return state

def check_daily_tasks():
    """检查每日任务状态"""
    tasks = [
        ("LIG 风险预警", "40-arxiv/lig-risk-monitor.py"),
        ("记忆蒸馏", "30-scripts-tools/memory_distiller_v2.py"),
        ("意识状态", "30-scripts-tools/memory_consciousness_emergence.py"),
    ]
    
    print("\nDaily Tasks Status:")
    for name, script in tasks:
        script_path = WORKSPACE_ROOT / script
        exists = "✅" if script_path.exists() else "❌"
        print(f"  {exists} {name}: {script}")

def check_weekly_tasks():
    """检查每周任务状态"""
    tasks = [
        ("批量蒸馏", "30-scripts-tools/memory_distiller_v2.py --batch"),
        ("遗忘评估", "30-scripts-tools/memory_forgetting_execute.py"),
        ("冲突解决", "30-scripts-tools/memory_conflict_resolver.py"),
    ]
    
    print("\nWeekly Tasks Status:")
    for name, script in tasks:
        print(f"  ⏳ {name}: {script}")

def main():
    if len(sys.argv) < 2:
        print("Usage: py heartbeat_lite.py <command>")
        print("\nCommands:")
        print("  status      - Check heartbeat status")
        print("  trigger     - Trigger heartbeat")
        print("  reset       - Reset heartbeat state")
        print("  daily       - Check daily tasks")
        print("  weekly      - Check weekly tasks")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        check_status()
    elif command == "trigger":
        trigger()
    elif command == "reset":
        reset()
    elif command == "daily":
        check_daily_tasks()
    elif command == "weekly":
        check_weekly_tasks()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
