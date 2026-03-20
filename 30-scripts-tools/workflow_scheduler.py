#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Step 5: 子工作流调度工具
判断是否需要子工作流，并调度相应子工作流
"""
import json
from pathlib import Path
from datetime import datetime

def schedule_workflow(task_analysis_file: str):
    analysis_path = Path(task_analysis_file)
    if not analysis_path.exists():
        return {
            "status": "error",
            "message": "任务分析文件不存在",
            "server_time": datetime.now().isoformat()
        }
    
    with open(analysis_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)
    
    complexity = analysis.get("complexity", "medium")
    estimated_time = analysis.get("estimated_time_minutes", 30)
    
    # 判断是否需要子工作流
    needs_subworkflow = complexity == "高" or estimated_time > 60
    
    if needs_subworkflow:
        # 选择合适的子工作流
        task_type = analysis.get("task_type", "")
        if "设计" in task_type or "系统" in task_type:
            subworkflow = "design-workflow"
        elif "实现" in task_type:
            subworkflow = "implementation-workflow"
        else:
            subworkflow = "general-workflow"
        
        return {
            "status": "subworkflow_required",
            "subworkflow": subworkflow,
            "reason": f"复杂度={complexity}, 预计时间={estimated_time}分钟",
            "server_time": datetime.now().isoformat()
        }
    else:
        return {
            "status": "no_subworkflow",
            "reason": f"复杂度={complexity}, 预计时间={estimated_time}分钟",
            "server_time": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import sys
    task_file = sys.argv[1] if len(sys.argv) > 1 else "flow-archive/20260318-universal-workflow-001/task-analysis.json"
    result = schedule_workflow(task_file)
    print(json.dumps(result, ensure_ascii=False, indent=2))
