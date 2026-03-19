import json
import sys
import io

# 修复中文乱码
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tools = data.get('tools', {})

# 检查工作流步骤需要的关键工具
workflow_tools = [
    'context-verify', 'flow-manager', 'task-analyzer', 
    'tool-suggester', 'workflow-scheduler', 'tool-executor',
    'execution-logger', 'checkpoint-saver', 'auto-critic-v7',
    'quality-gate', 'session-compress', 'git-commit-push'
]

# 实际注册的工具 ID（下划线版本）
actual_tools = [
    'context_verify', 'flow_manager', 'task_analyzer',
    'tool_suggester', 'workflow_scheduler', 'tool_executor',
    'execution_logger', 'checkpoint_saver', 'auto_critic_v7',
    'quality_gate_check', 'session_end', 'git_commit_push'
]

print("工作流步骤工具注册状态:")
print("="*60)

for workflow_tool, actual_tool in zip(workflow_tools, actual_tools):
    exists = actual_tool in tools
    status = "✓" if exists else "✗"
    print(f"  {workflow_tool:25s} → {actual_tool:25s}  {status}")

print("="*60)
print(f"总工具数：{len(tools)}")
