import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["guardian-auto-fix"] = {
    "tool_id": "guardian-auto-fix",
    "name": "Guardian Auto Fix",
    "description": "自动修复 execution-state.json",
    "version": "1.0.0",
    "command": "py 30-scripts-tools\\guardian_auto_fix.py",
    "path": "30-scripts-tools\\guardian_auto_fix.py",
    "category": "workflow",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("guardian-auto-fix 已注册")
