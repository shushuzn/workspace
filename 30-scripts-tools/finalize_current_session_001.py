import json
from datetime import datetime

# 读取 execution-state.json
with open('flow-archive/20260318-universal-workflow-001/execution-state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)

# 更新状态
state['status'] = 'completed'
state['completion_percentage'] = 100.0
state['current_step'] = 13.2
state['workflow_compliance'] = True

# 添加最终步骤
state['step_status'][13.2] = {
    "name": "会话结束",
    "status": "completed",
    "started_at": datetime.now().isoformat(),
    "completed_at": datetime.now().isoformat(),
    "result": "工作流强制防护系统集成完成"
}

# 保存
with open('flow-archive/20260318-universal-workflow-001/execution-state.json', 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print("会话状态已更新为 completed")
print(f"  Session: {state['session_id']}")
print(f"  完成率：{state['completion_percentage']}%")
