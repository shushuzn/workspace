import json
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    r = json.load(f)
sa_tools = [k for k in r['tools'].keys() if k.startswith('sa_')]
print(f"Stock Analysis Tools: {len(sa_tools)}")
print(sa_tools)
