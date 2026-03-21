import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["risk-assessor"] = {
    "tool_id": "risk-assessor",
    "name": "Risk Assessor",
    "description": "风险评级工具 - 评估操作风险等级",
    "version": "1.0.0",
    "file_path": "30-scripts-tools/risk_assessor.py",
    "category": "protection",
    "status": "active",
    "usage_count": 0,
    "created_at": "2026-03-20T08:25:00+08:00"
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("risk-assessor 已注册")
