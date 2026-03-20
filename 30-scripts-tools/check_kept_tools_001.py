import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

print(f"保留的工具 ({len(registry['tools'])}):")
for tool_id, info in registry["tools"].items():
    print(f"  - {tool_id}: {info.get('command', info.get('path', 'N/A'))}")
