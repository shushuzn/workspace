import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["confirmation-gate"] = {
    "tool_id": "confirmation-gate",
    "name": "Confirmation Gate",
    "description": "用户确认门 - 高风险操作前必须用户确认",
    "version": "1.0.0",
    "file_path": "30-scripts-tools/confirmation_gate.py",
    "category": "protection",
    "status": "active",
    "usage_count": 0,
    "created_at": "2026-03-20T08:26:00+08:00"
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("confirmation-gate 已注册")
