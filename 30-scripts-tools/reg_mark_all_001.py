import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["mark-all-completed"] = {
    "tool_id": "mark-all-completed",
    "name": "Mark All Completed",
    "description": "批量标记所有步骤为完成",
    "version": "1.0.0",
    "command": "py 30-scripts-tools\\mark_all_completed.py",
    "path": "30-scripts-tools\\mark_all_completed.py",
    "category": "workflow",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("mark-all-completed 已注册")
