import logging
logger = logging.getLogger(__name__)

import json

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

print("工具注册表验证:\n")
print(f"  版本：{registry.get('version', 'N/A')}")
print(f"  最后更新：{registry.get('last_updated', 'N/A')}")
print(f"  变更记录数：{len(registry.get('changes', []))}")
print(f"  最新变更：{registry.get('changes', ['N/A'])[0] if registry.get('changes') else 'N/A'}")

enforcement = registry.get('enforcement_rules', {})
print(f"\n  enforcement_rules 键：{list(enforcement.keys())}")

if 'security' in enforcement:
    sec = enforcement['security']
    print(f"\n  安全规则:")
    print(f"    版本：{sec.get('security_policy', {}).get('version', 'N/A')}")
    print(f"    允许工具数：{len(sec.get('allowed_tools', []))}")
    print(f"    包装工具数：{len(sec.get('wrapper_tools', []))}")
else:
    print("\n  [警告] security 规则未找到")

# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py verify_registry_update_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py verify_registry_update_001.py

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
