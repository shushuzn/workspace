import json

# 工具 ID 映射（横杠 → 下划线）
TOOL_ID_MAP = {
    'context-verify': 'context_verify',
    'flow-manager': 'flow_manager',
    'task-analyzer': 'task_analyzer',
    'tool-suggester': 'tool_suggester',
    'workflow-selector': 'workflow_selector',
    'workflow-scheduler': 'workflow_scheduler',
    'tool-executor': 'tool_executor',
    'execution-logger': 'execution_logger',
    'checkpoint-saver': 'checkpoint_saver',
    'auto-critic-v7': 'auto_critic_v7',
    'quality-gate': 'quality_gate_check',
    'session-compress': 'session_end',
    'git-commit-push': 'git_commit_push'
}

# 加载 workflow.json
with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 更新工具 ID
updated = 0
for step in workflow.get('steps', []):
    old_id = step.get('tool_id')
    if old_id and old_id in TOOL_ID_MAP:
        new_id = TOOL_ID_MAP[old_id]
        step['tool_id'] = new_id
        print(f"  {old_id:25s} → {new_id}")
        updated += 1

# 保存
with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"\n[OK] 更新完成：{updated} 个工具 ID")
