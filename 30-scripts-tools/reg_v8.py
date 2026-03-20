import json
from datetime import datetime

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

new_tools = [
    {
        "tool_id": "compliance-booster",
        "name": "Compliance Booster",
        "description": "合规率提升引擎 - 根因分析 + 改进方案",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/compliance_booster.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "behavior-analyzer",
        "name": "Behavior Analyzer",
        "description": "AI 行为分析器 - 异常检测 + 风险预测",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/behavior_analyzer.py",
        "category": "protection",
        "status": "active",
        "usage_count": 0,
        "created_at": datetime.now().isoformat()
    },
    {
        "tool_id": "auto-training-engine",
        "name": "Auto Training Engine",
        "description": "自动训练引擎 - 行为优化 + 习惯养成",
        "version": "1.0.0",
        "file_path": "30-scripts-tools/auto_training_engine.py",
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

registry["version"] = "1.11.51-compliance-v8"
registry["last_updated"] = datetime.now().isoformat()

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(f"新版本：{registry['version']}")
print(f"新增工具：{added} 个")
