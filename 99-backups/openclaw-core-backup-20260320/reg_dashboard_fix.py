import json
from datetime import datetime

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

new_tools = [
    {
        "tool_id": "compliance-dashboard",
        "name": "Compliance Dashboard",
        "description": "合规仪表板 - 实时监控 + 趋势分析 + 自动建议",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/compliance_dashboard.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "auto-fix-engine",
        "name": "Auto Fix Engine",
        "description": "自动修复引擎 - 智能修复 + 验证",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/auto_fix_engine.py",
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

registry["version"] = "1.11.48-dashboard-fix-v5"
registry["last_updated"] = datetime.now().isoformat()

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"新版本：{registry['version']}")
print(f"新增工具：{added} 个")
