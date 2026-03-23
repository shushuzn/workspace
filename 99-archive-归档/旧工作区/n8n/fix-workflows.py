import json
import uuid
import os

workflows_dir = "D:/OpenClaw/workspace/n8n/workflows"
output_dir = "D:/OpenClaw/workspace/n8n/workflows/fixed"

os.makedirs(output_dir, exist_ok=True)

workflow_files = [
    "file-maintenance-workflow.json",
    "git-auto-commit-workflow.json",
    "log-rotation-workflow.json",
    "data-preprocessing-workflow.json"
]

for wf_file in workflow_files:
    input_path = os.path.join(workflows_dir, wf_file)
    output_path = os.path.join(output_dir, wf_file)

    with open(input_path, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    # 添加工作流 ID
    workflow['id'] = str(uuid.uuid4())

    # 修复节点 ID 为数字
    for i, node in enumerate(workflow['nodes']):
        if 'id' in node and isinstance(node['id'], str):
            node['id'] = i + 1000  # 从 1000 开始避免冲突

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print(f"Fixed: {wf_file}")

print(f"\nAll workflows saved to: {output_dir}")
