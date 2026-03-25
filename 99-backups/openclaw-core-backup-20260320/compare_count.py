import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

print(f"当前 Registry 工具数：{len(registry.get('tools', {}))}")
print(f"实际文件数：107")
print(f"缺失：{107 - len(registry.get('tools', {}))}")
