import logging
logger = logging.getLogger(__name__)

import json

with open("flow-archive/20260318-universal-workflow-001/workflow.json", "r", encoding="utf-8") as f:
    w = json.load(f)

steps = w.get("steps", [])
print(f"总步骤数：{len(steps)}")
print("\nStep IDs:")
for s in steps:
    print(f"  {s.get('step_id')} - {s.get('name')}")
