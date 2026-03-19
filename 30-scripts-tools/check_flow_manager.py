import json
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
tool = d.get('tools', {}).get('flow-manager')
if tool:
    print("flow-manager config:", json.dumps(tool, indent=2, ensure_ascii=False))
else:
    print("flow-manager not found in tools registry")
