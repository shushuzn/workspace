#!/usr/bin/env python
import json

with open('30-scripts-tools/tools_registry.json', 'r', encoding='utf-8') as f:
    r = json.load(f)

print(f"总工具数：{r.get('total_tools', len(r.get('tools', {})))}")
print(f"版本：{r.get('version')}")

tools = r.get('tools', {})
low = [t for t, v in tools.items() if v.get('usage_count', 0) == 0]
print(f"\n0 次使用：{len(low)} 个")
print("\n前 30 个:")
for t in low[:30]:
    tool = tools.get(t, {})
    print(f"  [{t}] - {tool.get('category', 'unknown')}")
