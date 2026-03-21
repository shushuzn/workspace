import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["workflow_scheduler"] = {
    "tool_id": "workflow_scheduler",
    "name": "Workflow Scheduler",
    "description": "子工作流调度工具",
    "version": "1.0.0",
    "path": "30-scripts-tools\\workflow_scheduler.py",
    "category": "workflow",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print(json.dumps({
    "status": "success",
    "message": "workflow_scheduler 已注册",
    "server_time": "2026-03-20T02:41:30+08:00"
}, ensure_ascii=False, indent=2))
