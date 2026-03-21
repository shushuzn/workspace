import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["task_analyzer"] = {
    "tool_id": "task_analyzer",
    "name": "Task Analyzer",
    "description": "任务分析工具",
    "version": "1.0.0",
    "command": "py 30-scripts-tools\\task_analyzer.py",
    "path": "30-scripts-tools\\task_analyzer.py",
    "category": "analysis",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("task_analyzer 已注册")
