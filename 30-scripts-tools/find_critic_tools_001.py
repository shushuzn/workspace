import logging
logger = logging.getLogger(__name__)

import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

# 查找所有 critic 相关工具
critic_tools = {k: v for k, v in registry["tools"].items() if "critic" in k.lower()}

print(f"Critic 相关工具：{len(critic_tools)}\n")

for tool_id, info in list(critic_tools.items())[:10]:
    command = info.get("command", "N/A")
    print(f"{tool_id}:")
    print(f"  command: {command}")
    print()
