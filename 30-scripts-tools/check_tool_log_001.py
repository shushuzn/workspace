import logging
logger = logging.getLogger(__name__)

import json

with open('30-scripts-tools/tool_call_log.jsonl', 'r', encoding='utf-8') as f:
    logs = [json.loads(line) for line in f]

print(f"工具调用数量：{len(logs)}")
print("\n最近 10 次调用:")
for log in logs[-10:]:
    print(f"  {log.get('tool_id')}: {log.get('result')}")
