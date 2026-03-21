import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新 execution-state.json 中的步骤状态
"""
import json
from pathlib import Path
from datetime import datetime

def update_step(step_id: int, status: str, result: str = None):
    state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
    
    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)
    
    # 更新步骤状态
    step_status = state.get("step_status", {})
    step_name = f"Step {step_id}"
    
    step_status[str(step_id)] = {
        "name": step_name,
        "status": status,
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat() if status == "completed" else None,
        "result": result
    }
    
    state["step_status"] = step_status
    
    # 更新完成步骤列表
    if status == "completed":
        completed = state.get("completed_steps", [])
        if step_id not in completed:
            completed.append(step_id)
        state["completed_steps"] = completed
    
    # 计算完成率
    total = state.get("total_steps", 12)
    state["completion_percentage"] = round(len(state["completed_steps"]) / total * 100, 1)
    
    # 更新当前步骤
    if status == "completed":
        state["current_step"] = step_id + 1
    
    # 保存
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    return {
        "status": "success",
        "step_id": step_id,
        "step_status": status,
        "completion_percentage": state["completion_percentage"],
        "server_time": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import sys
    step_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    status = sys.argv[2] if len(sys.argv) > 2 else "completed"
    result = sys.argv[3] if len(sys.argv) > 3 else None
    
    res = update_step(step_id, status, result)
    print(json.dumps(res, ensure_ascii=False, indent=2))
