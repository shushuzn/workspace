#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check Missing File Tools - 检查缺失文件工具的使用情况
"""

import json
from pathlib import Path

TOOLS_REGISTRY = "30-scripts-tools/tools_registry.json"

MISSING_FILES = [
    "git_commit_push.py",
    "execution_logger.py",
    "tool_suggester.py",
    "task_analyzer.py",
    "checkpoint_saver.py",
    "timeout_optimizer.py"
]

def check_missing_tools():
    """检查缺失文件的工具"""
    
    print("=" * 70)
    print("🔍 检查缺失文件工具的使用情况")
    print("=" * 70)
    
    # 加载工具库
    with open(TOOLS_REGISTRY, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    tools = registry.get("tools", {})
    
    # 找到缺失文件的工具
    missing_tools = []
    for tool_id, tool in tools.items():
        file_name = tool.get("file", "")
        if file_name in MISSING_FILES:
            missing_tools.append({
                "tool_id": tool_id,
                "name": tool.get("name", "Unknown"),
                "description": tool.get("description", "No description"),
                "file": file_name,
                "category": tool.get("category", "uncategorized"),
                "triggers": tool.get("triggers", []),
                "blocking": tool.get("blocking", False)
            })
    
    print(f"\n📊 缺失文件工具：{len(missing_tools)} 个\n")
    
    for i, tool in enumerate(missing_tools, 1):
        print(f"{i}. [{tool['tool_id']}]")
        print(f"   名称：{tool['name']}")
        print(f"   描述：{tool['description']}")
        print(f"   文件：{tool['file']} ❌ (缺失)")
        print(f"   类别：{tool['category']}")
        print(f"   触发器：{tool['triggers']}")
        print(f"   阻断性：{tool['blocking']}")
        print()
    
    # 检查是否被 workflow.json 引用
    print("=" * 70)
    print("🔍 检查工作流配置引用...")
    print("=" * 70)
    
    workflow_file = Path("flow-archive/20260318-universal-workflow-001/workflow.json")
    if workflow_file.exists():
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = json.load(f)
        
        steps = workflow.get("steps", [])
        referenced_tools = []
        
        for step in steps:
            step_tools = step.get("tools", [])
            for tool in step_tools:
                tool_id = tool.get("tool_id", "") if isinstance(tool, dict) else tool
                if any(mf.replace(".py", "") in tool_id for mf in MISSING_FILES):
                    referenced_tools.append({
                        "step": step.get("step_id", "Unknown"),
                        "tool_id": tool_id
                    })
        
        if referenced_tools:
            print(f"\n⚠️  发现 {len(referenced_tools)} 个缺失工具被工作流引用:\n")
            for ref in referenced_tools:
                print(f"  - 步骤 {ref['step']}: {ref['tool_id']}")
        else:
            print("\n✅ 工作流配置中未引用缺失文件的工具")
    else:
        print(f"\n⚠️  工作流配置文件不存在：{workflow_file}")
    
    # 检查是否被其他工具调用
    print("\n" + "=" * 70)
    print("🔍 检查其他工具调用...")
    print("=" * 70)
    
    scripts_dir = Path("30-scripts-tools")
    referenced_by_scripts = {mf: [] for mf in MISSING_FILES}
    
    for script in scripts_dir.glob("*.py"):
        if script.name in MISSING_FILES:
            continue
        
        try:
            with open(script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for mf in MISSING_FILES:
                tool_name = mf.replace(".py", "")
                if tool_name in content:
                    referenced_by_scripts[mf].append(script.name)
        except:
            pass
    
    has_references = False
    for mf, scripts in referenced_by_scripts.items():
        if scripts:
            has_references = True
            print(f"\n⚠️  {mf} 被以下脚本引用:")
            for script in scripts[:5]:  # 显示前 5 个
                print(f"    - {script}")
            if len(scripts) > 5:
                print(f"    ... 还有 {len(scripts) - 5} 个")
    
    if not has_references:
        print("\n✅ 没有其他脚本引用缺失文件的工具")
    
    # 生成建议
    print("\n" + "=" * 70)
    print("💡 处理建议")
    print("=" * 70)
    
    for tool in missing_tools:
        file_name = tool["file"]
        tool_name = file_name.replace(".py", "")
        
        is_referenced = len(referenced_by_scripts.get(file_name, [])) > 0
        
        print(f"\n[{tool['tool_id']}]")
        
        if is_referenced:
            print(f"  ⚠️  状态：被其他工具引用")
            print(f"  ✅ 建议：补全文件 (创建 {file_name})")
            print(f"  📝 方案：")
            print(f"    1. 创建 {file_name} 实现基本功能")
            print(f"    2. 或迁移到现有工具 (如 tool_executor.py)")
            print(f"    3. 更新引用该工具的脚本")
        else:
            print(f"  ✅ 状态：未被引用")
            print(f"  ✅ 建议：从 tools_registry.json 删除定义")
            print(f"  📝 方案：")
            print(f"    1. 从 tools_registry.json 移除该工具")
            print(f"    2. 更新版本号")
    
    return missing_tools, referenced_by_scripts

if __name__ == '__main__':
    check_missing_tools()
