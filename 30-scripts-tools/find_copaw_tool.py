import json

with open("30-scripts-tools/tools_registry.json", "r", encoding="utf-8") as f:
    registry = json.load(f)

tools = registry["tools"]

# 查找包含 copaw 的工具
copaw_tools = [k for k in tools.keys() if "copaw" in k.lower()]
print(f"Copaw 相关工具：{copaw_tools}")

# 查找包含 entry 的工具
entry_tools = [k for k in tools.keys() if "entry" in k.lower()]
print(f"Entry 相关工具：{entry_tools}")

# 查找包含 executor 的工具
executor_tools = [k for k in tools.keys() if "executor" in k.lower()]
print(f"Executor 相关工具：{executor_tools[:10]}")

# 检查 copaw_entry.py 对应的工具 ID
print(f"\n总工具数：{len(tools)}")
