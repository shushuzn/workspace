import json

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

tools = data.get('tools', {})
print(f"总工具数：{len(tools)}")
print(f"\n工具列表:")
for tool_id in sorted(tools.keys()):
    print(f"  - {tool_id}")
