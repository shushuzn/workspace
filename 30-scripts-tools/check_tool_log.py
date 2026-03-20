import json
from pathlib import Path

log_file = Path("30-scripts-tools/tool_call_log.jsonl")

if log_file.exists():
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    print(f"工具调用日志总数：{len(lines)}")
    print(f"\n最近 10 条记录:")
    for line in lines[-10:]:
        entry = json.loads(line)
        print(f"  - {entry['timestamp']}: {entry['tool_id']} ({entry['duration_seconds']:.2f}s)")
else:
    print("日志文件不存在")
