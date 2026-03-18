#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
import codecs

# Windows UTF-8
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# 读取注册表
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

# 添加新工具
registry['tools']['p1-issue-fixer'] = {
    "tool_id": "p1-issue-fixer",
    "name": "P1 Issue Auto-Fixer",
    "description": "自动修复 P1 优先级问题（os.system/eval/exec 替换）",
    "version": "1.0",
    "command": "py 30-scripts-tools\\p1_issue_fixer.py --{action}",
    "parameters": {
        "action": {
            "type": "string",
            "required": True,
            "description": "操作类型",
            "enum": ["scan", "fix", "verify"],
            "default": "fix"
        }
    },
    "validation": {
        "os_system_remaining": 0,
        "eval_exec_remaining": 0
    },
    "category": "code-quality",
    "priority": "P1",
    "auto_run": True
}

# 更新版本
registry['version'] = '1.2.0'
registry['last_updated'] = '2026-03-18'
registry['changes'].append('Added p1-issue-fixer for automated os.system/eval/exec replacement')

# 保存
with open('30-scripts-tools/tools_registry.json', 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print("OK: Tool registered: p1-issue-fixer")
print(f"Total tools: {len(registry['tools'])}")
