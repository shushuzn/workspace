import logging
logger = logging.getLogger(__name__)

import json
with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    r = json.load(f)

# 查找工作流相关工具
keywords = ['context', 'task', 'tool_', 'flow', 'workflow', 'executor']
matched = {}
for kw in keywords:
    for k in r['tools'].keys():
        if kw.lower() in k.lower():
            matched[k] = r['tools'][k].get('description', '')

print(f"工具总数：{len(r['tools'])}")
print(f"\n匹配工具：{len(matched)}")
for k, v in list(matched.items())[:30]:
    print(f"  - {k}: {v[:60]}...")
