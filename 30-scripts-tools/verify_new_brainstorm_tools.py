#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify New Brainstorm Tools - 验证新版头脑风暴工具
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("验证新版头脑风暴工具")
print("="*60)

tools_to_verify = [
    "brainstorm_divergent",
    "brainstorm_convergent",
    "brainstorm_facilitator",
    "critic_brainstorm_lite"
]

results = []

for tool in tools_to_verify:
    try:
        module = __import__(tool)
        print(f"  [OK] {tool}.py - 导入成功")
        results.append({"tool": tool, "status": "pass", "error": None})
    except Exception as e:
        print(f"  [FAIL] {tool}.py - {e}")
        results.append({"tool": tool, "status": "fail", "error": str(e)})

print()
print("="*60)
print(f"验证结果：{sum(1 for r in results if r['status']=='pass')}/{len(results)} 通过")
print("="*60)

if all(r['status'] == 'pass' for r in results):
    print("✅ 所有新版工具验证通过!")
else:
    print("❌ 部分工具验证失败")
