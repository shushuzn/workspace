import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

# 检查第一个工具的结构
first_tool_id = list(registry["tools"].keys())[0]
first_tool = registry["tools"][first_tool_id]

print(f"第一个工具 ID: {first_tool_id}")
print(f"工具结构:")
print(json.dumps(first_tool, ensure_ascii=False, indent=2))

# 检查是否有 path 字段
print(f"\n是否有 path 字段：{'path' in first_tool}")
