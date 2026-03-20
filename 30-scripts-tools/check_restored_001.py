import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

print(f"Registry 版本：{registry.get('version', 'N/A')}")
print(f"工具总数：{len(registry.get('tools', {}))}")
print(f"最后更新：{registry.get('last_updated', 'N/A')}")
