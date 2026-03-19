#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Brainstorm Workflow to flow_registry.json
注册头脑风暴工作流到 flow_registry.json
"""

import json
from datetime import datetime
from pathlib import Path

def register_workflow():
    """注册工作流"""
    
    registry_file = Path("flow-archive/flow_registry.json")
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # 新工作流定义
    new_flow = {
        "20260320-brainstorm-v2": {
            "business_name": "brainstorm-v2",
            "description": "头脑风暴双环工作流 v2.0 - 发散环 (D1-D5) + 收敛环 (C1-C5), 最大 3 轮迭代",
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "directory": "D:\\OpenClaw\\workspace\\flow-archive\\20260320-brainstorm-v2",
            "last_updated": datetime.now().isoformat(),
            "workflow_file": "workflow.json",
            "total_steps": 10,
            "rings": ["divergent", "convergent"],
            "max_iterations": 3,
            "time_limit_minutes": 90,
            "critic_threshold": 60,
            "tools": [
                "brainstorm-divergent",
                "brainstorm-convergent",
                "brainstorm-facilitator",
                "critic-brainstorm-lite"
            ],
            "workflow_type": "subworkflow",
            "parent_workflow": "20260318-universal-workflow-001"
        }
    }
    
    # 添加到 registry
    registry["flows"].update(new_flow)
    registry["last_updated"] = datetime.now().isoformat()
    
    # 保存
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"注册完成:")
    print(f"  工作流：20260320-brainstorm-v2")
    print(f"  目录：flow-archive/20260320-brainstorm-v2/")
    print(f"  总工作流数：{len(registry['flows'])}")
    
    return registry

if __name__ == "__main__":
    register_workflow()
