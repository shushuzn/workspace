#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复 state 文件签名
"""

import json
import hashlib
from pathlib import Path

STATE_FILE = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
SIGNATURE_KEY = "CoPaw-State-Integrity-Key-2026"

def compute_signature(state: dict) -> str:
    state_copy = {k: v for k, v in state.items() if k != 'signature'}
    content = json.dumps(state_copy, sort_keys=True, ensure_ascii=False)
    signature = hashlib.sha256((content + SIGNATURE_KEY).encode('utf-8')).hexdigest()
    return signature

# 读取 state
with open(STATE_FILE, 'r', encoding='utf-8') as f:
    state = json.load(f)

# 重新计算签名
state['signature'] = compute_signature(state)

# 保存
with open(STATE_FILE, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("State 签名已修复")
print(f"  签名：{state['signature'][:16]}...")
