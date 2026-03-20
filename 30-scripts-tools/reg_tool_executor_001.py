import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["tool_executor"] = {
    "tool_id": "tool_executor",
    "name": "Tool Executor",
    "description": "工具执行器 - 统一工具调用入口",
    "version": "1.0.0",
    "command": "py 30-scripts-tools\\tool_executor.py",
    "path": "30-scripts-tools\\tool_executor.py",
    "category": "core",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("tool_executor 已注册")
