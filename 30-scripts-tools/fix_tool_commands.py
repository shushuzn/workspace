#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复工具注册表中的命令配置
规则：移除 ${args} 占位符，使用实际参数或无参数
"""

import json
import sys
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
REGISTRY_FILE = WORKSPACE / "30-scripts-tools" / "tools_registry.json"

# 需要修复的工具命令
FIXES = {
    # 无参数工具
    'context_search': 'py 30-scripts-tools/context_search.py --demo',
    'quality_gate_check': 'py 30-scripts-tools/quality_gate_check.py --all',
    'session_end': 'py 30-scripts-tools/session_end.py auto',
    'auto_critic_v7': 'py 30-scripts-tools/auto-critic_v7.py -t workflow_execution -p final',
}

def main():
    print("="*60)
    print("修复工具命令配置")
    print("="*60)
    
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    fixed = 0
    for tool_id, new_command in FIXES.items():
        if tool_id in registry.get('tools', {}):
            old_command = registry['tools'][tool_id].get('command', '')
            registry['tools'][tool_id]['command'] = new_command
            print(f"  {tool_id:30s}: {old_command[:50]:50s} → {new_command}")
            fixed += 1
    
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] 修复完成：{fixed} 个工具命令")

if __name__ == '__main__':
    main()
