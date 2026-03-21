import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

registry["tools"]["fix-execution-state-v3"] = {
    "tool_id": "fix-execution-state-v3",
    "name": "Fix Execution State v3",
    "description": "修复 execution-state.json 以匹配 workflow.json 的所有步骤 ID",
    "version": "3.0.0",
    "command": "py 30-scripts-tools\\fix_execution_state_v3.py",
    "path": "30-scripts-tools\\fix_execution_state_v3.py",
    "category": "workflow",
    "parameters": {}
}

with open("30-scripts-tools/tools_registry.json", "w", encoding="utf-8") as f:
    json.dump(registry, f, ensure_ascii=False, indent=2)

print("fix-execution-state-v3 已注册")
