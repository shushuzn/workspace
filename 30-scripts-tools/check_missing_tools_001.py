import logging
logger = logging.getLogger(__name__)

import json
from pathlib import Path

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

tools = registry["tools"]
scripts_dir = Path("30-scripts-tools")

# 检查实际存在的文件
py_files = [f.stem.replace("_", "-") for f in scripts_dir.glob("*.py")]

# 查找 registry 中不存在的文件
missing_from_registry = []
for f in py_files[:30]:  # 前 30 个
    if f not in tools and f.replace("-", "_") not in tools:
        missing_from_registry.append(f)

print("实际存在但 Registry 中没有的工具 (前 30):")
for f in missing_from_registry[:20]:
    print(f"  - {f}")

# 检查关键工具
key_files = ["copaw_entry", "tool_executor", "tool_call_tracker", "workflow_guardian_v2"]
print("\n关键工具检查:")
for key in key_files:
    key_dash = key.replace("_", "-")
    key_under = key.replace("-", "_")
    found = key_dash in tools or key_under in tools
    print(f"  {key}: {'[OK]' if found else '[MISSING]'}")
