import json
d = json.load(open('30-scripts-tools/tools_registry.json', encoding='utf-8'))
tools = d.get('tools', {})
sa_tools = [k for k in tools.keys() if k.startswith('SA')]
print('Total tools:', len(tools))
print('SA tools:', sa_tools)