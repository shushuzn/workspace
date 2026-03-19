#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verify Brainstorm Workflow Registration - 验证头脑风暴工作流注册
"""

import json
from pathlib import Path

def verify():
    """验证注册"""
    
    flow_registry = Path("flow-archive/flow_registry.json")
    tools_registry = Path("30-scripts-tools/tools_registry.json")
    
    print("="*60)
    print("验证头脑风暴工作流注册")
    print("="*60)
    
    # 检查 flow_registry.json
    print("\n[1] flow-archive/flow_registry.json:")
    with open(flow_registry, 'r', encoding='utf-8') as f:
        flow_reg = json.load(f)
    
    if "20260320-brainstorm-v2" in flow_reg['flows']:
        flow_info = flow_reg['flows']["20260320-brainstorm-v2"]
        print(f"  [OK] 20260320-brainstorm-v2 已注册")
        print(f"       目录：{flow_info.get('directory', 'N/A')}")
        print(f"       类型：{flow_info.get('workflow_type', 'N/A')}")
        print(f"       步骤：{flow_info.get('total_steps', 'N/A')}")
        print(f"       父工作流：{flow_info.get('parent_workflow', 'N/A')}")
    else:
        print(f"  [FAIL] 20260320-brainstorm-v2 未注册")
    
    # 检查 tools_registry.json
    print("\n[2] 30-scripts-tools/tools_registry.json:")
    with open(tools_registry, 'r', encoding='utf-8') as f:
        tools_reg = json.load(f)
    
    if "20260320-brainstorm-v2" in tools_reg['tools']:
        tool_info = tools_reg['tools']["20260320-brainstorm-v2"]
        print(f"  [OK] 20260320-brainstorm-v2 已注册")
        print(f"       类别：{tool_info.get('category', 'N/A')}")
        print(f"       描述：{tool_info.get('description', 'N/A')[:50]}...")
    else:
        print(f"  [INFO] 20260320-brainstorm-v2 未在 tools_registry 中注册 (正常)")
    
    # 检查 workflow.json
    print("\n[3] flow-archive/20260320-brainstorm-v2/workflow.json:")
    workflow_file = Path("flow-archive/20260320-brainstorm-v2/workflow.json")
    if workflow_file.exists():
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        print(f"  [OK] workflow.json 存在")
        print(f"       flow_id: {workflow.get('flow_id', 'N/A')}")
        print(f"       名称：{workflow.get('name', 'N/A')}")
        print(f"       版本：{workflow.get('version', 'N/A')}")
    else:
        print(f"  [FAIL] workflow.json 不存在")
    
    print("\n" + "="*60)
    print("验证完成!")
    print("="*60)

if __name__ == "__main__":
    verify()
