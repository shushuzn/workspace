import json

with open("flow-archive/20260318-universal-workflow-001/workflow.json", "r", encoding="utf-8") as f:
    workflow = json.load(f)

steps = workflow.get("steps", [])
print(f"工作流步骤总数：{len(steps)}\n")
print("步骤 ID 列表:")
for step in steps:
    step_id = step.get("step_id")
    name = step.get("name", "N/A")
    print(f"  {step_id} ({type(step_id).__name__}): {name}")
