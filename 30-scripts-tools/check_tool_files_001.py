import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path

registry_file = Path("30-scripts-tools/tools_registry.json")
with open(registry_file, "r", encoding="utf-8") as f:
    registry = json.load(f)

tools = registry.get("tools", {})
existing = []
missing = []

for tool_id, info in tools.items():
    command = info.get("command", "")
    # 从 command 中提取文件名
    if "py " in command:
        parts = command.split("py ")[1].split(" ")[0]
        filename = parts.split("\\")[-1].split("/")[-1]
        filepath = Path("30-scripts-tools") / filename
        if filepath.exists():
            existing.append(tool_id)
        else:
            missing.append((tool_id, filename))

print(f"工具文件检查:")
print(f"  存在：{len(existing)}")
print(f"  缺失：{len(missing)}")
print(f"\n存在的工具 (前 20 个):")
for t in existing[:20]:
    print(f"  - {t}")

if missing:
    print(f"\n缺失的工具 (前 20 个):")
    for tool_id, filename in missing[:20]:
        print(f"  - {tool_id}: {filename}")
