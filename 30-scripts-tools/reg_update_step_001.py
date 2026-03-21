import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["update-step-state"] = {
    "tool_id": "update-step-state",
    "name": "Update Step State",
    "description": "更新 execution-state.json 中的步骤状态",
    "version": "1.0.0",
    "command": "py 30-scripts-tools\\update_step_state.py",
    "path": "30-scripts-tools\\update_step_state.py",
    "category": "workflow",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("update-step-state 已注册")
