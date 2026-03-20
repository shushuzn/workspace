import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["tool_selector"] = {
    "tool_id": "tool_selector",
    "name": "Tool Selector",
    "description": "工具选择工具",
    "version": "1.0.0",
    "path": "30-scripts-tools\\tool_selector.py",
    "category": "selection",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(json.dumps({
    "status": "success",
    "message": "tool_selector 已注册",
    "server_time": "2026-03-20T02:41:00+08:00"
}, ensure_ascii=False, indent=2))
