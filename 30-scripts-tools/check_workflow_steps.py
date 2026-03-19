import json

with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    wf = json.load(f)

print("工作流步骤配置:")
for step in wf['steps']:
    tool_id = step.get('tool_id', 'N/A')
    print(f"Step {step['step_id']:2d}: {step['name']:20s} -> {tool_id}")
