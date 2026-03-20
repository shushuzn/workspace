import json

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    registry = json.load(f)

tools = registry.get('tools', {})

# 查看 safe-shell-executor 详情
if 'safe-shell-executor' in tools:
    tool = tools['safe-shell-executor']
    print("safe-shell-executor 详情:\n")
    print(json.dumps(tool, indent=2, ensure_ascii=False)[:2000])
else:
    print("safe-shell-executor 未找到")
