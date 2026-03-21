import logging
logger = logging.getLogger(__name__)

import json
from datetime import datetime

# 加载 workflow.json
with open("flow-archive/20260318-universal-workflow-001/workflow.json", "r", encoding="utf-8") as f:
    workflow = json.load(f)

# 添加强制执行规则
workflow["version"] = "1.5.0"
workflow["updated_at"] = datetime.now().isoformat()

# 添加强制执行配置
workflow["mandatory_execution"] = {
    "enabled": True,
    "entry_point": "30-scripts-tools/copaw_entry.py",
    "rules": [
        "所有任务必须通过 copaw_entry.py 入口点启动",
        "禁止直接执行工具脚本",
        "禁止绕过主工作流",
        "所有会话必须初始化 execution-state.json",
        "会话结束必须更新 execution-state.json"
    ],
    "enforcement": {
        "pre_session": {
            "check": "copaw_entry.py 必须被调用",
            "action": "自动初始化 execution-state.json"
        },
        "during_session": {
            "check": "所有工具调用必须通过 tool_executor",
            "action": "记录到 tool_call_log.jsonl"
        },
        "post_session": {
            "check": "execution-state.json 必须更新",
            "action": "验证完成率 + Git 提交"
        }
    },
    "anti_bypass": {
        "enabled": True,
        "detect_direct_tool_calls": True,
        "detect_missing_state_file": True,
        "detect_missing_tool_log": True,
        "action_on_violation": "block_and_report"
    }
}

# 保存到文件
with open("flow-archive/20260318-universal-workflow-001/workflow.json", "w", encoding="utf-8") as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print(f"[OK] workflow.json 已更新到 v{workflow['version']}")
print(f"\nMandatory Execution 配置:")
print(f"  enabled: {workflow['mandatory_execution']['enabled']}")
print(f"  entry_point: {workflow['mandatory_execution']['entry_point']}")
print(f"  rules: {len(workflow['mandatory_execution']['rules'])} 条")
print(f"  anti_bypass.enabled: {workflow['mandatory_execution']['anti_bypass']['enabled']}")
