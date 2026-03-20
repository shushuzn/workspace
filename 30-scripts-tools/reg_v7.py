import json
from datetime import datetime

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

new_tools = [
    {
        "tool_id": "blockchain-logger",
        "name": "Blockchain Logger",
        "description": "区块链式日志 - 不可篡改",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/blockchain_logger.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "external-verifier",
        "name": "External Verifier",
        "description": "外部验证器 - 第三方审计",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/external_verifier.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "auto-recovery",
        "name": "Auto Recovery System",
        "description": "自动恢复系统 - 被破坏后自愈",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/auto_recovery.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    }
]

added = 0
for tool in new_tools:
    tool_id = tool["tool_id"]
    if tool_id not in registry["tools"]:
        registry["tools"][tool_id] = tool
        added += 1
        print(f"[ADD] {tool_id}")

registry["version"] = "1.11.50-recovery-v7"
registry["last_updated"] = datetime.now().isoformat()

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"新版本：{registry['version']}")
print(f"新增工具：{added} 个")
