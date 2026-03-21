import logging
logger = logging.getLogger(__name__)

import json
with open('flow-archive/20260318-universal-workflow-001/execution-state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)
completed = state.get('completed_steps', [])
print(f"Completed steps: {completed}")
print(f"Types: {[type(c).__name__ for c in completed]}")

with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    w = json.load(f)
required = [s.get('step_id') for s in w.get('steps', []) if s.get('required', True)]
print(f"\nRequired steps: {required}")
print(f"Types: {[type(r).__name__ for r in required]}")

matched = [c for c in completed if c in required]
print(f"\nMatched: {len(matched)}/{len(required)}")
missing = [r for r in required if r not in completed]
print(f"Missing: {missing}")
