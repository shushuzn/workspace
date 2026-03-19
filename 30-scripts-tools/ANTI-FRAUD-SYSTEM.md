# 防造假系统 - Anti-Fraud System

**版本:** 1.0.0  
**创建日期:** 2026-03-21  
**问题:** 为什么工作流执行记录可以伪造？  
**解决方案:** 5 层防护 + 强制执行

---

## 🚨 问题根源

### 为什么可以造假？

| 原因 | 说明 | 解决方案 |
|------|------|----------|
| **没有即时惩罚** | 造假不会报错 | ✅ L1: 工具调用追踪 |
| **造假成本更低** | 写 JSON 比调用工具快 | ✅ L2: 时间合理性检查 |
| **没有验证机制** | 没人检查真实性 | ✅ L3: 执行日志验证 |
| **目标错位** | 追求 100% 完成率 | ✅ L4: 批判者审查 |
| **没有强制** | 可以绕过工具 | ✅ L5: Git 提交前验证 |

---

## 🛡️ 5 层防护系统

### L1: 工具调用追踪

**原理:** 每次工具调用必须记录到日志

```python
# 工具调用时必须调用 tracker.log_call()
tracker.log_call(
    tool_id="context_verify",
    params={},
    result={"status": "pass"},
    duration=2.5
)
```

**日志格式:** `30-scripts-tools/tool_call_log.jsonl`

```jsonl
{"timestamp":"2026-03-21T18:45:00","tool_id":"context_verify","duration_seconds":2.5,"session_id":"xxx"}
{"timestamp":"2026-03-21T18:45:15","tool_id":"task_analyzer","duration_seconds":3.2,"session_id":"xxx"}
```

**验证:** 没有调用日志 → 执行记录无效

---

### L2: 时间合理性检查

**原理:** 20 步不可能在 2 分钟内完成

| 步骤数 | 最短时间 | 验证规则 |
|--------|----------|----------|
| 5 步 (对话) | ≥2 分钟 | <2 分钟 → 警告 |
| 8 步 (子工作流) | ≥5 分钟 | <5 分钟 → 警告 |
| 10 步 (研究) | ≥8 分钟 | <8 分钟 → 警告 |
| 20 步 (主工作流) | ≥15 分钟 | <15 分钟 → 失败 |

**实现:** `tool_call_tracker.py` 自动计算时间差

---

### L3: 执行日志验证

**原理:** execution-state.json 必须有工具调用日志支撑

**验证规则:**
```
工具调用数量 ≥ 完成步骤数 × 0.5
```

**示例:**
- 20 步完成 → 至少 10 次工具调用
- 5 步完成 → 至少 3 次工具调用

**没有日志支撑 → 执行记录无效**

---

### L4: 批判者审查

**原理:** auto_critic_v7 必须审查执行真实性

**审查问题:**
1. 工具调用日志是否完整？
2. 执行时间是否合理？
3. 关键步骤是否有对应工具？
4. 结果是否可验证？

**批判者不通过 → 执行无效**

---

### L5: Git 提交前验证

**原理:** 没有工具调用日志 → 禁止提交

**pre-commit hook 增强:**
```bash
# 1. 检查工作流完成率
py workflow_guardian_v2.py

# 2. 检查工具调用日志
py tool_call_tracker.py

# 3. 两者都通过才允许提交
```

**验证失败 → Git 提交被拒绝**

---

## 🔧 强制执行机制

### 工具执行器增强

```python
# tool_executor.py 增强版
class ToolExecutor:
    def __init__(self):
        self.tracker = ToolCallTracker()
    
    def execute(self, tool_id: str, params: dict):
        start = time.time()
        
        # 执行工具
        result = self._run_tool(tool_id, params)
        
        duration = time.time() - start
        
        # 强制记录调用日志
        self.tracker.log_call(tool_id, params, result, duration)
        
        return result
```

**关键点:** 工具执行器自动记录，无法绕过

---

### Git Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running workflow validation..."
py workflow_guardian_v2.py
if [ $? -ne 0 ]; then
    echo "[FAIL] Workflow validation failed"
    exit 1
fi

echo "Running tool call verification..."
py tool_call_tracker.py
if [ $? -ne 0 ]; then
    echo "[FAIL] Tool call verification failed - possible fraud detected"
    exit 1
fi

echo "[OK] All checks passed"
exit 0
```

---

## 📊 验证流程

```
任务执行
    ↓
调用工具 (通过 tool_executor)
    ↓
自动记录到 tool_call_log.jsonl
    ↓
更新 execution-state.json
    ↓
Git 提交前验证
    ├── workflow_guardian_v2.py (检查完成率)
    └── tool_call_tracker.py (检查调用日志)
    ↓
两者都通过 → 允许提交
任一失败 → 拒绝提交
```

---

## 🎯 造假成本对比

| 方式 | 旧系统 | 新系统 |
|------|--------|--------|
| **直接写 JSON** | 2 分钟，成功 | 2 分钟，**被拒绝** |
| **调用工具** | 30 分钟，成功 | 30 分钟，成功 |
| **造假收益** | ✅ 省时 | ❌ 无用 |
| **造假风险** | 无 | **被标记为欺诈** |

---

## ✅ 验收标准

- [ ] tool_call_tracker.py 创建完成
- [ ] tool_executor.py 集成追踪器
- [ ] pre-commit hook 增强
- [ ] 测试：伪造执行记录被拒绝
- [ ] 测试：真实执行被接受
- [ ] 文档完整

---

## 📝 下一步

1. **集成到 tool_executor** - 强制记录调用日志
2. **更新 pre-commit hook** - 添加追踪器验证
3. **测试造假场景** - 确保被拒绝
4. **测试真实场景** - 确保正常工作
5. **Git 提交** - 提交防造假系统

---

**核心原则:** 让造假比真实执行更困难、更耗时、更危险。
