import json

with open("flow-archive/20260318-universal-workflow-001/workflow.json", "r", encoding="utf-8") as f:
    w = json.load(f)

print(f"Workflow: {w['flow_id']}")
print(f"版本：{w['version']}")
print(f"总步骤：{w['total_steps']}")
print(f"\n阶段定义:")
for stage, desc in w.get('stages', {}).items():
    print(f"  {stage}: {desc}")

print(f"\n步骤列表:")
steps = w.get('steps', [])
for s in steps:
    step_id = s.get('step_id')
    name = s.get('name')
    tool_id = s.get('tool_id')
    stage = s.get('stage')
    print(f"  {step_id:5} | {name:20} | {tool_id:25} | {stage}")
