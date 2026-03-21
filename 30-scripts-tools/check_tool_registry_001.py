import logging
logger = logging.getLogger(__name__)

import json

# 读取工具注册表
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

tools = registry.get('tools', {})

# 搜索 shell 相关工具
print("搜索 shell 相关工具:\n")
for tool_id in sorted(tools.keys()):
    if 'shell' in tool_id.lower() or 'executor' in tool_id.lower():
        tool = tools[tool_id]
        print(f"  [OK] {tool_id}")
        print(f"     描述：{tool.get('description', 'N/A')[:60]}")
        print(f"     命令：{tool.get('command', 'N/A')[:60]}")
        print()

# 检查特定工具
check_tools = ['execute_shell_command', 'safe_shell_executor', 'tool_executor', 'shell']
print("\n检查特定工具:")
for tool in check_tools:
    if tool in tools:
        print(f"  [OK] {tool} - 已注册")
    else:
        print(f"  [X] {tool} - 未注册")
