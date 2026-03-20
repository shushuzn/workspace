#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python 执行包装器 - 强制所有 py 命令通过防护层
使用方法：py protected_py.py <script.py> [args...]
"""
import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path("30-scripts-tools")
STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
STOP_FLAG = SCRIPTS_DIR / ".STOP_FLAG"

def force_protection_check():
    """强制防护检查 - 失败则退出"""
    
    # 检查 session
    if not STATE_FILE.exists():
        print("=" * 70)
        print("[FATAL] execution-state.json 不存在")
        print("[FATAL] 必须通过 copaw_entry.py 启动会话")
        print("[FATAL] 直接运行脚本是被禁止的")
        print("=" * 70)
        sys.exit(1)
    
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    if not state.get("session_id"):
        print("[FATAL] session_id 缺失")
        sys.exit(1)
    
    if not state.get("mandatory_execution"):
        print("[FATAL] mandatory_execution 未启用")
        sys.exit(1)
    
    # 检查停止标志
    if STOP_FLAG.exists():
        print("=" * 70)
        print("[BLOCK] 系统处于停止状态")
        with open(STOP_FLAG, "r", encoding="utf-8") as f:
            stop_data = json.load(f)
        print(f"[BLOCK] 原因：{stop_data.get('reason', '未知')}")
        print("=" * 70)
        sys.exit(1)
    
    print(f"[OK] 防护检查通过：{state['session_id']}")

def main():
    if len(sys.argv) < 2:
        print("用法：py protected_py.py <script.py> [args...]")
        print("所有 Python 脚本执行都会自动通过防护检查")
        sys.exit(1)
    
    # 强制防护检查
    force_protection_check()
    
    # 执行实际脚本
    script_path = sys.argv[1]
    script_args = sys.argv[2:]
    
    command = f"py {script_path} {' '.join(script_args)}"
    
    print(f"[EXEC] {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=300
        )
        
        # 输出结果
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        sys.exit(result.returncode)
    
    except subprocess.TimeoutExpired:
        print("[ERROR] 执行超时 (>300s)")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
