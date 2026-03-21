import logging
logger = logging.getLogger(__name__)

import json

with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

steps = workflow.get('steps', [])
print(f"步骤数量：{len(steps)}")
print(f"步骤类型：{type(steps)}")

if isinstance(steps, dict):
    print("步骤是字典，keys:")
    for k in list(steps.keys())[:10]:
        print(f"  {k}: {type(steps[k])}")
elif isinstance(steps, list) and len(steps) > 0:
    print(f"第一个步骤：{steps[0]}")
