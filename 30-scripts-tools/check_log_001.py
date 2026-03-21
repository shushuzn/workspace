import logging
logger = logging.getLogger(__name__)

import json
lines = open("30-scripts-tools/tool_call_log.jsonl", "r", encoding="utf-8").readlines()
print(f"总行数：{len(lines)}")
print("最后 5 行时间戳:")
for l in lines[-5:]:
    entry = json.loads(l)
    print(f"  {entry.get('timestamp', 'N/A')}")
