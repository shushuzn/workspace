import json

# 修复工具 ID 映射（使用实际存在的文件）
TOOL_ID_FIXES = {
    'context_verify': 'context_search',  # context_verify.py 不存在
}

# 加载 workflow.json
with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# 更新工具 ID
updated = 0
for step in workflow.get('steps', []):
    old_id = step.get('tool_id')
    if old_id and old_id in TOOL_ID_FIXES:
        new_id = TOOL_ID_FIXES[old_id]
        step['tool_id'] = new_id
        print(f"  {old_id:30s} → {new_id}")
        updated += 1

# 保存
with open('flow-archive/20260318-universal-workflow-001/workflow.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print(f"\n[OK] 修复完成：{updated} 个工具 ID")
