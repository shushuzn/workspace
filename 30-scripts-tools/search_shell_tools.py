import json

# 读取工具注册表
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

# 搜索 shell 相关工具
shell_tools = {}
for tool_id, tool_data in registry.get('tools', {}).items():
    if 'shell' in tool_id.lower() or 'shell' in str(tool_data).lower():
        shell_tools[tool_id] = tool_data

print(f"找到 {len(shell_tools)} 个 shell 相关工具:\n")
for tool_id, data in shell_tools.items():
    print(f"  - {tool_id}: {data.get('description', 'N/A')[:50]}")

# 检查是否有 execute_shell_command
if 'execute_shell_command' in registry.get('tools', {}):
    print("\n✅ execute_shell_command 已注册")
else:
    print("\n❌ execute_shell_command 未注册")
