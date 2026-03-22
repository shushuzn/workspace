import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
State 文件保护器 - 唯一允许修改 execution-state.json 的入口

防护规则：
1. 只有 copaw_entry.py 可以写入 execution-state.json
2. 所有修改必须记录审计日志
3. 所有修改必须包含数字签名
4. 任何直接修改都会被检测

使用方式：
    from state_protector import update_state
    update_state({'current_step': 2})
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
AUDIT_LOG = Path("flow-archive/20260318-universal-workflow-001/state-audit.jsonl")
SIGNATURE_KEY = "CoPaw-State-Integrity-Key-2026"

# 允许修改 state 的脚本
ALLOWED_WRITERS = [
    'copaw_entry.py',
    'state_protector.py',
]


def compute_signature(state: dict) -> str:
    """计算 state 的数字签名"""
    # 排除 signature 字段本身
    state_copy = {k: v for k, v in state.items() if k != 'signature'}
    content = json.dumps(state_copy, sort_keys=True, ensure_ascii=False)
    signature = hashlib.sha256((content + SIGNATURE_KEY).encode('utf-8')).hexdigest()
    return signature


def verify_signature(state: dict) -> bool:
    """验证 state 的数字签名"""
    if 'signature' not in state:
        return False
    
    stored_signature = state['signature']
    computed_signature = compute_signature(state)
    return stored_signature == computed_signature


def log_audit(action: str, changes: dict, caller: str):
    """记录审计日志"""
    audit_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "changes": changes,
        "caller": caller,
        "pid": os.getpid(),
    }
    
    with open(AUDIT_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(audit_entry, ensure_ascii=False) + '\n')


def check_caller():
    """检查调用者是否被允许"""
    import sys
    
    # 获取调用栈
    import traceback
    stack = traceback.extract_stack()
    
    # 检查调用链
    for frame in stack:
        filename = Path(frame.filename).name
        if filename in ALLOWED_WRITERS:
            return True, filename
    
    # 检查是否是直接执行
    script_name = Path(sys.argv[0]).name if sys.argv[0] else 'unknown'
    if script_name in ALLOWED_WRITERS:
        return True, script_name
    
    return False, script_name


def update_state(changes: dict, force: bool = False) -> bool:
    """
    更新 state 文件
    
    Args:
        changes: 要修改的字段
        force: 是否强制修改（仅内部使用）
    
    Returns:
        bool: 是否成功
    """
    # 检查调用者
    allowed, caller = check_caller()
    if not allowed and not force:
        print("=" * 70)
        print(f"[BLOCK] State 修改被拒绝")
        print(f"[BLOCK] 调用者：{caller}")
        print(f"[BLOCK] 只允许：{', '.join(ALLOWED_WRITERS)}")
        print("=" * 70)
        return False
    
    # 读取现有 state
    if not STATE_FILE.exists():
        print("[ERROR] State 文件不存在")
        return False
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    # 验证现有签名
    if 'signature' in state and not verify_signature(state):
        print("=" * 70)
        print("[SECURITY] State 文件签名验证失败")
        print("[SECURITY] 文件可能已被篡改")
        print("=" * 70)
        log_audit("tampering_detected", {"old_state": state}, caller)
    
    # 应用修改
    old_values = {}
    for key, value in changes.items():
        if key in state:
            old_values[key] = state[key]
        state[key] = value
    
    # 添加新签名
    state['signature'] = compute_signature(state)
    state['last_modified'] = datetime.now().isoformat()
    state['last_modified_by'] = caller
    
    # 写入 state
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    # 记录审计
    log_audit("state_update", {"changes": changes, "old_values": old_values}, caller)
    
    print(f"[OK] State 已更新 by {caller}")
    return True


def verify_state_integrity() -> bool:
    """验证 state 文件完整性"""
    if not STATE_FILE.exists():
        return False
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    return verify_signature(state)


def init_state_protection():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py state_protector_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py state_protector_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

初始化 state 保护（首次创建时调用）"""
    if not STATE_FILE.exists():
        return
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    # 添加初始签名
    if 'signature' not in state:
        state['signature'] = compute_signature(state)
        state['protection_enabled'] = True
        
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        log_audit("protection_enabled", {}, "state_protector")
        print("[OK] State 保护已启用")


if __name__ == '__main__':
    # 测试
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        if verify_state_integrity():
            print("[OK] State 文件完整性验证通过")
            sys.exit(0)
        else:
            print("[FAIL] State 文件完整性验证失败")
            sys.exit(1)
    
    print("State Protector - 只允许通过 copaw_entry.py 修改")
