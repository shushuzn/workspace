import json
from pathlib import Path

# 读取 workflow.json 获取所有步骤
with open("flow-archive/20260318-universal-workflow-001/workflow.json", "r", encoding="utf-8") as f:
    workflow = json.load(f)

steps = workflow.get("steps", [])
print(f"主步骤数：{len(steps)}")
print("\n步骤列表:")
for step in steps:
    print(f"  {step['step_id']}: {step['name']}")
