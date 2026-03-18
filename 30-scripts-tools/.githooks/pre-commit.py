#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Git Pre-Commit Hook - 工作流合规性检查"""

import sys, io, json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
FLOW_ARCHIVE = WORKSPACE / "flow-archive"

def check_workflow_completion(flow_id="20260318-universal-workflow-001"):
    checkpoint_file = FLOW_ARCHIVE / flow_id / "checkpoint.json"
    if not checkpoint_file.exists():
        return True
    
    with open(checkpoint_file, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    total = state.get('total_steps', 0)
    completed = len(state.get('completed_steps', []))
    status = state.get('status', 'unknown')
    
    print(f"[Git Hook] 工作流检查：{completed}/{total} 步骤，状态：{status}")
    
    if status != 'completed':
        print(f"[BLOCKER] 工作流未完成！提交被阻断")
        return False
    
    return True

if __name__ == '__main__':
    if not check_workflow_completion():
        sys.exit(1)
    sys.exit(0)
