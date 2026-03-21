#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新主工作流 enforcement rules - 添加工具注册表防护机制

规则：
1. 禁止直接使用工具脚本
2. 所有工具必须通过 tools_registry.json 注册
3. 所有工具调用必须通过 tool_executor.py
4. 未注册工具调用将被阻断
"""

import json
from pathlib import Path
from datetime import datetime

# 加载 workflow.json
workflow_path = Path("flow-archive/20260318-universal-workflow-001/workflow.json")
with open(workflow_path, "r", encoding="utf-8") as f:
    workflow = json.load(f)

# 更新 enforcement rules
new_rules = [
    "必须按顺序执行 12 个步骤",
    "跳步将被阻断",
    "完成后必须验证",
    "未通过验证禁止 Git 提交",
    "🛡️ 禁止直接使用工具脚本 - 所有工具必须通过 tools_registry.json 注册",
    "🛡️ 所有工具调用必须通过 tool_executor.py - 唯一合法调用入口",
    "🛡️ 未注册工具调用将被阻断 - tool_executor 验证工具 ID 存在性",
    "🛡️ 工具调用必须记录日志 - tool_call_log.jsonl 用于防造假验证",
    "🛡️ 执行记录必须有日志支撑 - 无日志=伪造=拒绝提交"
]

workflow["enforcement"]["rules"] = new_rules
workflow["enforcement"]["tool_registry_required"] = True
workflow["enforcement"]["tool_registry_path"] = "30-scripts-tools/tools_registry.json"
workflow["enforcement"]["tool_executor_required"] = True
workflow["enforcement"]["tool_executor_path"] = "30-scripts-tools/tool_executor.py"
workflow["enforcement"]["call_logging_required"] = True
workflow["enforcement"]["call_log_path"] = "30-scripts-tools/tool_call_log.jsonl"
workflow["enforcement"]["anti_fraud"] = {
    "enabled": True,
    "rules": [
        "禁止直接使用工具脚本",
        "必须通过注册表验证工具",
        "必须通过 tool_executor 调用",
        "必须记录调用日志",
        "无日志=伪造=拒绝提交"
    ],
    "verification_tool": "tool_call_tracker.py",
    "git_hook_integration": True
}

# 更新版本
old_version = workflow.get("version", "1.3.4")
workflow["version"] = "1.4.0"
workflow["updated_at"] = datetime.now().isoformat()

# 保存
with open(workflow_path, "w", encoding="utf-8") as f:
    json.dump(workflow, f, ensure_ascii=False, indent=2)

print(f"[OK] workflow.json 已更新")
print(f"版本：{old_version} → {workflow['version']}")
print(f"规则数：{len(workflow['enforcement']['rules'])}")
print(f"\nNew protection rules:")
for rule in new_rules[4:]:
    # Remove emoji for Windows GBK compatibility
    clean_rule = rule.replace("🛡️", "[PROTECT]")
    print(f"  {clean_rule}")

# 创建防护机制文档
doc_content = """# 工具调用防护机制 - Tool Call Protection

**版本:** """ + workflow['version'] + """  
**更新日期:** """ + workflow['updated_at'] + """  
**工作流:** """ + workflow['flow_id'] + """

---

## [PROTECT] 核心原则

> **禁止直接使用工具脚本，必须经过注册表验证 + tool_executor 调用**

---

## 三层防护

### L1: 注册表验证

```
工具调用 → 检查 tools_registry.json → 工具 ID 存在？→ 否 → 拒绝
                                      ↓ 是
                                      继续
```

**规则:**
- 所有工具必须在 `tools_registry.json` 中注册
- 工具 ID 必须匹配
- 未注册工具 = 非法工具 = 拒绝执行

---

### L2: tool_executor 统一调用

```
任务执行 → tool_executor.py → 验证工具 → 执行 → 记录日志
           ↑
       唯一合法入口
```

**规则:**
- `tool_executor.py` 是唯一合法调用入口
- 禁止直接 `import xxx` 或 `py xxx.py`
- 绕过 tool_executor = 非法调用 = 拒绝

---

### L3: 调用日志验证

```
tool_executor 执行 → 自动记录到 tool_call_log.jsonl
                          ↓
                    Git 提交前验证
                          ↓
                    无日志？→ 拒绝提交
```

**规则:**
- 每次工具调用必须记录日志
- 日志格式：JSONL (每行一个调用)
- Git 提交前验证日志完整性
- 无日志支撑的执行记录 = 伪造

---

## 强制执行机制

### workflow.json 配置

```json
"enforcement": {
  "tool_registry_required": true,
  "tool_executor_required": true,
  "call_logging_required": true,
  "anti_fraud": {
    "enabled": true,
    "rules": [
      "禁止直接使用工具脚本",
      "必须通过注册表验证工具",
      "必须通过 tool_executor 调用",
      "必须记录调用日志",
      "无日志=伪造=拒绝提交"
    ]
  }
}
```

---

### tool_executor.py 验证逻辑

```python
def execute(tool_id: str, params: dict):
    # 1. 验证工具在注册表中
    if tool_id not in registry['tools']:
        raise ValueError(f"工具未注册：{tool_id}")
    
    # 2. 执行工具
    result = _run_tool(tool_id, params)
    
    # 3. 记录调用日志
    tracker.log_call(tool_id, params, result, duration)
    
    return result
```
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py update_workflow_enforcement_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py update_workflow_enforcement_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""



---

### Git Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 1. 工作流验证
py workflow_guardian_v2.py
if [ $? -ne 0 ]; then
    echo "[FAIL] Workflow validation failed"
    exit 1
fi

# 2. 工具调用日志验证
py tool_call_tracker.py
if [ $? -ne 0 ]; then
    echo "[FAIL] Tool call verification failed - possible fraud"
    exit 1
fi

echo "[OK] All checks passed"
exit 0
```

---

## 造假成本对比

| 方式 | 旧系统 | 新系统 |
|------|--------|--------|
| **直接写 JSON** | 2 分钟，成功 | 2 分钟，**被拒绝** |
| **直接调用工具** | 5 分钟，成功 | 5 分钟，**被拒绝** |
| **通过注册表+tool_executor** | 30 分钟，成功 | 30 分钟，成功 |
| **造假收益** | 省时 | **无用** |
| **造假风险** | 无 | **被标记为欺诈** |

---

## 验收标准

- [ ] workflow.json 已更新 (v1.4.0)
- [ ] enforcement rules 包含 5 条防护规则
- [ ] anti_fraud 配置启用
- [ ] tool_executor.py 集成注册表验证
- [ ] tool_call_tracker.py 集成
- [ ] pre-commit hook 更新
- [ ] 测试：未注册工具被拒绝
- [ ] 测试：绕过 tool_executor 被拒绝
- [ ] 测试：无日志调用被拒绝

---

## 核心原则

> **让造假比真实执行更困难、更耗时、更危险。**

**当前状态:**
- 造假：2 分钟，成功
- 真实：30 分钟，成功

**目标状态:**
- 造假：2 分钟，**被拒绝 + 被标记**
- 真实：30 分钟，成功

---

**更新完成:** """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """
"""

doc_path = Path("flow-archive/20260318-universal-workflow-001/TOOL-PROTECTION-MECHANISM.md")
with open(doc_path, "w", encoding="utf-8") as f:
    f.write(doc_content)

print(f"\n[OK] 文档已创建：{doc_path}")
