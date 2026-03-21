import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速验证 execution-state.json 类型正确性
用法：py verify_state_types.py
"""

import json

logging.basicConfig(level=logging.INFO)
def main():
    # 加载文件
    with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
        workflow = json.load(f)
    
    with open('flow-archive/20260318-universal-workflow-001/execution-state.json', 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    # 提取 step_id
    required = [s.get('step_id') for s in workflow.get('steps', []) if s.get('required', True)]
    completed = state.get('completed_steps', [])
    
    print("=" * 60)
    print("Step ID 类型验证")
    print("=" * 60)
    
    # 逐项对比
    all_match = True
    for i, (req, comp) in enumerate(zip(required, completed)):
        type_match = type(req) == type(comp)
        value_match = req == comp
        
        status = "[OK]" if (type_match and value_match) else "[FAIL]"
        print(f"{status} Step {i+1}: workflow={req} ({type(req).__name__}), state={comp} ({type(comp).__name__})")
        
        if not (type_match and value_match):
            all_match = False
    
    print("=" * 60)
    if all_match:
        print("[OK] 所有 Step ID 类型和值完全匹配")
        return 0
    else:
        print("[FAIL] 发现类型或值不匹配")
        return 1

if __name__ == "__main__":
    exit(main())
