import json

# 加载 workflow.json
with open("flow-archive/20260318-universal-workflow-001/workflow.json", "r", encoding="utf-8") as f:
    workflow = json.load(f)

# 添加强制读取核心规则
if "mandatory_rules" not in workflow:
    workflow["mandatory_rules"] = {}

workflow["mandatory_rules"]["core_execution_rules"] = {
    "enabled": True,
    "file": "flow-archive/20260318-universal-workflow-001/CORE-EXECUTION-RULES.md",
    "verify_tool": "core_rules_verifier.py",
    "verify_at_step": 1,
    "block_if_fail": True,
    "rules": [
        "纯执行代理",
        "工具调用获取",
        "严格单步执行",
        "禁止提前生成",
        "原样抛出错误",
        "禁止总结润色",
        "可验证字段",
        "禁止假设",
        "禁止过程描述",
        "终止并上报"
    ]
}

# 更新版本
workflow["version"] = "1.6.0"

# 保存
with open("flow-archive/20260318-universal-workflow-001/workflow.json", "w", encoding="utf-8") as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print(json.dumps({
    "status": "success",
    "message": "核心执行规则已添加到 workflow.json",
    "version": "1.6.0",
    "server_time": "2026-03-20T02:40:00+08:00"
}, ensure_ascii=False, indent=2))
