import json
from datetime import datetime

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

new_tool = {
    "tool_id": "improvement-executor",
    "name": "Improvement Executor",
    "description": "改进计划执行器 - 自动执行合规率改进",
    "version": "1.0.0",
    "file_path": "30-scripts-tools/improvement_executor.py",
    "category": "protection",
    "status": "active",
    "usage_count": 0,
    "created_at": datetime.now().isoformat()
}

if new_tool["tool_id"] not in registry["tools"]:
    registry["tools"][new_tool["tool_id"]] = new_tool
    print(f"[ADD] {new_tool['tool_id']}")

registry["version"] = "1.11.52-improvement-v9"
registry["last_updated"] = datetime.now().isoformat()

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"新版本：{registry['version']}")
print(f"工具总数：{len(registry['tools'])}")
