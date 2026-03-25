import json
from datetime import datetime

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

new_tools = [
    {
        "tool_id": "forced-protection-executor",
        "name": "Forced Protection Executor",
        "description": "强制防护执行器 - 无法绕过的防护执行",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/forced_protection_executor.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "protected-py",
        "name": "Protected PY",
        "description": "Python 执行包装器 - 强制所有 py 命令通过防护层",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/protected_py.py",
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

registry["version"] = "1.11.45-forced-protection-v2"
registry["last_updated"] = datetime.now().isoformat()

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"\n注册完成：{added} 个工具")
print(f"新版本：{registry['version']}")
