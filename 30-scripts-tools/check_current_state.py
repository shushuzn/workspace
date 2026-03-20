import json
from pathlib import Path

state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
with open(state_file, 'r', encoding='utf-8') as f:
    state = json.load(f)

print("当前 execution-state.json 状态:")
print(f"  Session: {state.get('session_id')}")
print(f"  当前步骤：{state.get('current_step')}")
print(f"  完成率：{state.get('completion_percentage')}%")
print(f"  已完成步骤数：{len(state.get('completed_steps', []))}")
print(f"\n最近 5 个 step_status:")

step_status = state.get('step_status', {})
for i, (step_id, step_data) in enumerate(list(step_status.items())[-5:]):
    print(f"  Step {step_id}: {step_data.get('name', 'N/A')} - {step_data.get('status', 'N/A')}")
