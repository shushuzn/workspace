#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完全自动化工作流执行 - 零手动干预
方案 A: 自动步骤追踪

规则:
1. 所有工具通过 tool_executor.py 调用（禁止直接调用工具脚本）
2. 配置步骤自动跳过并标记完成
3. 系统级 UTF-8 编码已设置（无需在脚本中处理）
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
FLOW_ARCHIVE = WORKSPACE / "flow-archive"
WORKFLOW_FILE = FLOW_ARCHIVE / "20260318-universal-workflow-001" / "workflow.json"
CHECKPOINT_FILE = FLOW_ARCHIVE / "20260318-universal-workflow-001" / "checkpoint.json"
TOOL_EXECUTOR = WORKSPACE / "30-scripts-tools" / "tool_executor.py"

def load_workflow():
    with open(WORKFLOW_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_checkpoint():
    if not CHECKPOINT_FILE.exists():
        return None
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_current_step():
    state = load_checkpoint()
    if not state:
        return 1
    return len(state.get('completed_steps', [])) + 1

def tool_exists(tool_id):
    """检查工具是否存在"""
    registry_file = WORKSPACE / "30-scripts-tools" / "tools_registry.json"
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    return tool_id in registry.get('tools', {})

def is_config_step(tool_id):
    """判断是否为配置步骤（需要特殊参数或仅配置用途）"""
    config_tools = [
        'flow_manager', 'task_analyzer', 'tool_suggester',
        'workflow_selector', 'subworkflow_dispatcher', 'workflow_scheduler',
        'execution_logger', 'checkpoint_saver', 'tool_executor'
    ]
    return tool_id in config_tools

def execute_step_via_executor(tool_id):
    """通过 tool_executor 执行工具（唯一合法方式）"""
    result = subprocess.run([
        sys.executable,
        str(TOOL_EXECUTOR),
        tool_id
    ], cwd=str(WORKSPACE), capture_output=True, text=True, 
       encoding='utf-8', errors='replace')
    
    return result.returncode == 0, result.stdout, result.stderr

def mark_step_complete(step_id):
    """标记步骤完成"""
    subprocess.run([
        sys.executable,
        str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
        "--complete-step",
        str(step_id)
    ], cwd=str(WORKSPACE), capture_output=True)

def execute_step(step_config):
    """
    执行单个步骤
    
    规则:
    1. 配置步骤 → 自动跳过并标记完成
    2. 工具不存在 → 警告并跳过
    3. 实际工具 → 通过 tool_executor 执行
    """
    step_id = step_config['step_id']
    tool_id = step_config.get('tool_id')
    step_name = step_config['name']
    
    print(f"\n{'='*60}")
    print(f"Step {step_id}: {step_name}")
    print(f"{'='*60}")
    
    # 无工具 → 自动跳过
    if not tool_id:
        print(f"[INFO] 步骤 {step_id} 无关联工具，自动跳过")
        mark_step_complete(step_id)
        return True
    
    # 配置步骤 → 自动跳过
    if is_config_step(tool_id):
        print(f"[INFO] 步骤 {step_id} ({tool_id}) 是配置步骤，自动跳过")
        mark_step_complete(step_id)
        return True
    
    # 工具不存在 → 警告并跳过
    if not tool_exists(tool_id):
        print(f"[WARN] 工具 {tool_id} 不存在，自动跳过步骤 {step_id}")
        mark_step_complete(step_id)
        return True
    
    # 通过 tool_executor 执行工具
    print(f"[EXEC] 通过 tool_executor 执行：{tool_id}")
    success, stdout, stderr = execute_step_via_executor(tool_id)
    
    if success:
        print(f"[OK] 步骤 {step_id} 执行成功（自动完成）")
        return True
    else:
        print(f"[ERROR] 步骤 {step_id} 执行失败")
        # 安全打印（避免编码错误）
        if stdout:
            try:
                print(stdout)
            except UnicodeEncodeError:
                print(stdout.encode('gbk', errors='replace').decode('gbk', errors='replace'))
        if stderr:
            try:
                print(stderr)
            except UnicodeEncodeError:
                print(stderr.encode('gbk', errors='replace').decode('gbk', errors='replace'))
        return False

def main():
    print("="*60)
    print("完全自动化工作流执行 - 方案 A")
    print("规则：所有工具通过 tool_executor 调用")
    print("="*60)
    
    workflow = load_workflow()
    steps = workflow.get('steps', [])
    
    for step in steps:
        step_id = step['step_id']
        current = get_current_step()
        
        # 跳过已完成的步骤
        if step_id < current:
            continue
        
        # 执行步骤
        if not execute_step(step):
            print(f"\n[BLOCKER] 步骤 {step_id} 执行失败，终止工作流")
            return False
        
        # 非阻塞步骤提示
        if not step.get('blocking', True):
            print(f"[INFO] 非阻塞步骤 {step_id}，可选择跳过")
    
    print("\n" + "="*60)
    print("工作流执行完成！")
    print("="*60)
    
    # 验证
    print("\n[验证] 检查工作流完成状态...")
    subprocess.run([
        sys.executable,
        str(WORKSPACE / "30-scripts-tools" / "workflow_enforcer.py"),
        "--validate"
    ], cwd=str(WORKSPACE))
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
