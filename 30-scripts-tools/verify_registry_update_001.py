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
