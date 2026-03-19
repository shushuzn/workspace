#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integrate Tools - 集成工具到 tool_executor.py
"""

from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:\\OpenClaw\\workspace")
TOOL_EXECUTOR = WORKSPACE / "30-scripts-tools" / "tool_executor.py"

# 需要集成的工具
TOOLS_TO_INTEGRATE = [
    {
        "tool_id": "long-term-memory",
        "module": "long_term_memory",
        "function": "main"
    },
    {
        "tool_id": "task-decomposer",
        "module": "task_decomposer",
        "function": "main"
    },
    {
        "tool_id": "proactive-agent",
        "module": "proactive_agent",
        "function": "main"
    },
    {
        "tool_id": "multimodal-agent",
        "module": "multimodal_agent",
        "function": "main"
    },
    {
        "tool_id": "workflow-recovery",
        "module": "workflow_recovery",
        "function": "main"
    },
    {
        "tool_id": "integration-validator",
        "module": "integration_validator",
        "function": "main"
    }
]

def integrate_tools():
    """集成工具到 tool_executor.py"""
    
    if not TOOL_EXECUTOR.exists():
        print("❌ tool_executor.py 不存在")
        return False
    
    with open(TOOL_EXECUTOR, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已导入
    integrated_count = 0
    
    for tool in TOOLS_TO_INTEGRATE:
        module = tool["module"]
        tool_id = tool["tool_id"]
        
        # 检查是否已导入
        if f"import {module}" in content or f"from {module}" in content:
            print(f"⚠️  已导入：{module}")
            continue
        
        # 添加到导入部分 (在文件开头附近找导入区域)
        import_marker = "import json"
        if import_marker in content:
            new_import = f"import {module}"
            content = content.replace(import_marker, f"{import_marker}\n{new_import}")
            print(f"✅ 已添加导入：{module}")
            integrated_count += 1
        else:
            print(f"❌ 找不到导入位置：{module}")
    
    # 添加到工具映射字典
    # 找 tool_mapping 或类似结构
    if "tool_mapping" in content or "TOOLS" in content:
        print("✅ 工具映射已存在，无需添加")
    else:
        # 添加简单的工具映射
        mapping_code = "\n\n# Tool Mapping\ntool_mapping = {\n"
        for tool in TOOLS_TO_INTEGRATE:
            mapping_code += f"    '{tool['tool_id']}': {tool['module']}.{tool['function']},\n"
        mapping_code += "}\n"
        
        # 添加到文件末尾
        content += mapping_code
        print("✅ 已添加工具映射")
    
    # 保存
    with open(TOOL_EXECUTOR, 'w', encoding='utf-8') as f:
        content = content.replace('\r\n', '\n')  # 统一换行符
        f.write(content)
    
    print(f"\n✅ 集成完成：{integrated_count} 个工具")
    
    return True

if __name__ == '__main__':
    integrate_tools()
