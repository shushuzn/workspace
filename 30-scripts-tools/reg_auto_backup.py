import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["auto-backup"] = {
    "tool_id": "auto-backup",
    "name": "Auto Backup",
    "description": "自动备份工具 - 修改文件前自动备份",
    "version": "1.0.0",
    "file_path": "30-scripts-tools/auto_backup.py",
    "category": "protection",
    "status": "active",
    "usage_count": 0,
    "created_at": "2026-03-20T08:27:00+08:00"
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("auto-backup 已注册")
