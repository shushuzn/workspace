import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

print(f"Registry 版本：{registry.get('version', 'N/A')}")
print(f"工具总数：{len(registry.get('tools', {}))}\n")

print("可用工具列表 (前 30 个):")
for i, (tool_id, info) in enumerate(list(registry["tools"].items())[:30], 1):
    cmd = info.get("command", "N/A")
    print(f"  {i}. {tool_id}")
    print(f"     {cmd}")
