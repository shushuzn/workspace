import logging
logger = logging.getLogger(__name__)

import json
with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    w = json.load(f)
steps = w.get('steps', [])
step_ids = [s.get('step_id') for s in steps]
print(f"Step IDs (first 15): {step_ids[:15]}")
print(f"Types: {[type(sid).__name__ for sid in step_ids[:15]]}")
