# 工具调用防护机制 - Tool Call Protection

**版本:** 1.4.0  
**更新日期:** 2026-03-20T02:14:56.959315  
**工作流:** 20260318-universal-workflow-001

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

**更新完成:** 2026-03-20 02:14
