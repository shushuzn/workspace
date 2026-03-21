import logging
logger = logging.getLogger(__name__)

import json

with open("flow-archive/20260318-universal-workflow-001/execution-state.json", "r", encoding="utf-8") as f:
    state = json.load(f)

print("=" * 70)
print("工作流执行状态")
print("=" * 70)
print(f"任务：{state['task']}")
print(f"会话：{state['session_id']}")
print(f"状态：{state['status']}")
print(f"完成步骤：{len(state['completed_steps'])}/20")
print(f"完成率：{state['completion_percentage']}%")
print(f"工作流合规：{state['workflow_compliance']}")

print("\n步骤完成情况:")
for step_id in sorted(state['step_status'].keys(), key=float):
    status = state['step_status'][step_id]
    print(f"  Step {step_id:5} | {status['status']:10} | {status['name']}")
