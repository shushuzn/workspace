import json
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("原则:")
for p in d.get('principles', []):
    print(f"  - {p}")

print("\n强制规则:")
for k, v in d.get('enforcement_rules', {}).items():
    print(f"  {k}: {v.get('rule')}")

print(f"\n总工具数：{len(d.get('tools', {}))}")
