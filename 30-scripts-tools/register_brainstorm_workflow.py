#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Register Brainstorm Workflow - 注册头脑风暴双环工作流到 workflow 类别
"""

import json
from datetime import datetime
from pathlib import Path

def register_brainstorm_workflow():
    """注册头脑风暴工作流"""
    
    registry_file = Path("30-scripts-tools/tools_registry.json")
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # 新工作流定义
    new_workflow = {
        "brainstorm-workflow-v2": {
            "description": "头脑风暴双环工作流 v2.0 - 发散环 (D1-D5) + 收敛环 (C1-C5), 最大 3 轮迭代",
            "category": "workflow",
            "automation_enabled": False,
            "usage_count": 0,
            "file": "brainstorm_facilitator.py",
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "triggers": ["manual", "creative_task"],
            "review_required": False,
            "blocking": False,
            "timeout_seconds": 5400,
            "workflow_config": {
                "flow_id": "brainstorm-workflow-v2",
                "total_steps": 10,
                "rings": ["divergent", "convergent"],
                "max_iterations": 3,
                "time_limit_minutes": 90,
                "critic_threshold": 60
            }
        }
    }
    
    # 添加到 registry
    registry["tools"].update(new_workflow)
    
    # 更新版本
    version_parts = registry["version"].split(".")
    registry["version"] = f"{version_parts[0]}.{version_parts[1]}.{int(version_parts[2]) + 1}"
    registry["last_updated"] = datetime.now().isoformat()
    registry["changes"].insert(0, f"v{registry['version']}: Added brainstorm-workflow-v2 to workflow category")
    
    # 保存
    with open(registry_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"注册完成:")
    print(f"  新工作流：brainstorm-workflow-v2")
    print(f"  版本：{registry['version']}")
    print(f"  总工具数：{len(registry['tools'])}")
    
    return registry

if __name__ == "__main__":
    register_brainstorm_workflow()
