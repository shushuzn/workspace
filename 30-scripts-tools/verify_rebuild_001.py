import json
from pathlib import Path

registry_file = Path("30-scripts-tools/tools_registry.json")
scripts_dir = Path("30-scripts-tools")

with open(registry_file, "r", encoding="utf-8") as f:
    registry = json.load(f)

tools = registry.get("tools", {})
print(f"Registry 工具数：{len(tools)}")

# 验证每个工具的文件是否存在
found = 0
missing = 0

for tool_id, info in tools.items():
    command = info.get("command", "")
    if "py " in command:
        filename = command.split("py ")[1].split(" ")[0].split("\\")[-1]
        if (scripts_dir / filename).exists():
            found += 1
        else:
            missing += 1
            print(f"  [MISSING] {tool_id}: {filename}")

print(f"\n文件存在：{found}")
print(f"文件缺失：{missing}")
print(f"匹配率：{found/(found+missing)*100:.1f}%")
