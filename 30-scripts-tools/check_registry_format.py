import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

# 检查 workflow-enforcer
tool = registry["tools"].get("workflow-enforcer", {})
print("workflow-enforcer 定义:")
print(json.dumps(tool, ensure_ascii=False, indent=2))

# 检查几个其他工具
print("\n\n其他工具示例:")
for tool_id in ["copaw-entry", "tool-executor", "embedded-critic"]:
    tool = registry["tools"].get(tool_id, {})
    print(f"\n{tool_id}:")
    print(f"  command: {tool.get('command', 'N/A')}")
    print(f"  path: {tool.get('path', 'N/A')}")
