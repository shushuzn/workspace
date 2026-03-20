import json
from datetime import datetime

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

new_tools = [
    {
        "tool_id": "sa-019-chart-generator",
        "name": "SA-019 Stock Chart Generator",
        "description": "股票图表生成器 - K线图、指标图、形态标注",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/sa_019_chart_generator.py",
        "category": "stock_analysis",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "sa-020-report-generator",
        "name": "SA-020 Report Generator",
        "description": "报告自动生成器 - 每日/周报/月报，Markdown格式",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/sa_020_report_generator.py",
        "category": "stock_analysis",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "sa-021-dashboard",
        "name": "SA-021 Stock Dashboard",
        "description": "股票监控仪表板 - 实时行情、持仓、告警",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/sa_021_dashboard.py",
        "category": "stock_analysis",
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

registry["version"] = "1.11.55-phase4-v1"
registry["last_updated"] = datetime.now().isoformat()

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"Version: {registry['version']}")
print(f"Total tools: {len(registry['tools'])}")
print(f"Added: {added}")