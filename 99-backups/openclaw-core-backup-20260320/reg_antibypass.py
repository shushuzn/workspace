import json
from datetime import datetime

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

new_tools = [
    {
        "tool_id": "integrity-checker",
        "name": "Integrity Checker",
        "description": "完整性检查器 - 防篡改检测",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/integrity_checker.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "anti-bypass-engine",
        "name": "Anti Bypass Engine",
        "description": "反绕过引擎 - 主动检测并阻止绕过行为",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/anti_bypass_engine.py",
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

registry["version"] = "1.11.49-antibypass-v6"
registry["last_updated"] = datetime.now().isoformat()

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"新版本：{registry['version']}")
print(f"新增工具：{added} 个")
