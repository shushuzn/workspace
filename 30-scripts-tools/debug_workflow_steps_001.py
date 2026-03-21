import logging
logger = logging.getLogger(__name__)

import json
with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    w = json.load(f)
steps = w.get('steps', [])
print(f"Total steps defined: {len(steps)}")
print("\nStep IDs and required status:")
for s in steps:
    step_id = s.get('step_id')
    required = s.get('required', True)
    print(f"  {step_id} (type: {type(step_id).__name__}) - required: {required}")
