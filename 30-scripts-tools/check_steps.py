import json
with open('flow-archive/20260318-universal-workflow-001/workflow.json', encoding='utf-8') as f:
    w = json.load(f)
steps = [s['step_id'] for s in w['steps']]
print(f"Total steps: {len(steps)}")
print(f"Step IDs: {steps}")
