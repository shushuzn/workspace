import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["core_rules_verifier"] = {
    "tool_id": "core_rules_verifier",
    "name": "Core Rules Verifier",
    "description": "核心执行规则验证工具",
    "version": "1.0.0",
    "path": "30-scripts-tools\\core_rules_verifier.py",
    "category": "verification",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(json.dumps({
    "status": "success",
    "message": "core_rules_verifier 已注册",
    "server_time": "2026-03-20T02:40:30+08:00"
}, ensure_ascii=False, indent=2))
