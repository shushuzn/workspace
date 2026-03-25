import json

with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

steps = workflow.get('steps', [])
print("Workflow 步骤定义 (step_id):")
for step in steps:
    step_id = step.get('step_id')
    name = step.get('name', 'N/A')
    print(f"  {step_id}: {name}")
