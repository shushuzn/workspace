#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Python Site Customize - 系统级防护层

此文件会在所有 Python 脚本执行前自动运行（通过 PYTHONPATH 或 site 模块）

防护功能：
1. 检查是否在允许的工具脚本目录中
2. 检查是否有 session（对工具脚本强制）
3. 记录所有 Python 脚本执行
"""

import sys
import os
from pathlib import Path
import json

# 只在工作空间目录激活
WORKSPACE_ROOT = Path("D:/OpenClaw/workspace")
if Path.cwd() != WORKSPACE_ROOT and not str(Path.cwd()).startswith(str(WORKSPACE_ROOT)):
    # 不在工作空间，不激活防护
    sys.exit(0)

# 检查是否是允许的系统脚本（不需要 session）
ALLOWED_WITHOUT_SESSION = [
    'copaw_entry.py',      # 会话入口
    'sitecustomize.py',    # 本脚本
    'check_session.py',    # session 检查工具
]

# 获取当前执行的脚本
script_path = Path(sys.argv[0]).resolve() if sys.argv[0] else Path.cwd()
script_name = script_path.name

# 检查是否在工具目录
is_tool_script = '30-scripts-tools' in str(script_path)

if is_tool_script and script_name not in ALLOWED_WITHOUT_SESSION:
    # 工具脚本必须检查 session
    state_file = WORKSPACE_ROOT / "flow-archive/20260318-universal-workflow-001/execution-state.json"
    
    if not state_file.exists():
        print("=" * 70, file=sys.stderr)
        print("[BLOCK] Python 脚本执行被拒绝", file=sys.stderr)
        print(f"[BLOCK] 脚本：{script_name}", file=sys.stderr)
        print("[BLOCK] 原因：execution-state.json 不存在", file=sys.stderr)
        print("[BLOCK] 请先运行：py 30-scripts-tools/copaw_entry.py <task>", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)
    
    # 验证 session 有效性
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        if not state.get('session_id'):
            raise ValueError("session_id missing")
        if not state.get('mandatory_execution'):
            raise ValueError("mandatory_execution not enabled")
    except Exception as e:
        print("=" * 70, file=sys.stderr)
        print("[BLOCK] Python 脚本执行被拒绝", file=sys.stderr)
        print(f"[BLOCK] 脚本：{script_name}", file=sys.stderr)
        print(f"[BLOCK] 原因：session 无效 - {e}", file=sys.stderr)
        print("[BLOCK] 请先运行：py 30-scripts-tools/copaw_entry.py <task>", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        sys.exit(1)

# 记录脚本执行（用于审计）
log_file = WORKSPACE_ROOT / "30-scripts-tools/python_execution_log.jsonl"
try:
    log_entry = {
        "timestamp": json.dumps(__import__('datetime').datetime.now().isoformat()),
        "script": str(script_path),
        "args": sys.argv[1:],
        "pid": os.getpid(),
    }
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(str(log_entry) + '\n')
except:
    pass  # 日志失败不影响执行
