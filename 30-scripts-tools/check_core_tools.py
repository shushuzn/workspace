import json

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

# 核心工具列表
core_tools = [
    'tool_executor', 'workflow_enforcer', 'auto_execute_workflow',
    'register_tools', 'check_tool_rules', 'check_tools',
    'check_workflow_steps', 'fix_tool_commands'
]

print("核心工具注册状态:")
for tool in core_tools:
    exists = tool in registry['tools']
    status = "✓" if exists else "✗"
    print(f"  {tool:30s} {status}")
