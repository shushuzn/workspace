# 系统级防护方案 v1.0

**创建时间:** 2026-03-20  
**目标:** 防止 AI  agent 犯错（基于今日错误反思）

---

## 错误回顾

| # | 错误类型 | 后果 | 防护需求 |
|---|---------|------|---------|
| 1 | 盲目执行同步脚本 | 删除 438 个工具定义 | 需要**执行前确认** |
| 2 | 未理解用户意图 | 恢复错误版本 | 需要**意图确认** |
| 3 | 未检查格式兼容性 | 工具调用失败 | 需要**兼容性检查** |
| 4 | 违反核心规则 | 创建伪造日志脚本 | 需要**规则强制执行** |
| 5 | 未充分诊断 | 错误报告状态 | 需要**诊断优先** |

---

## 防护层级

### Layer 1: 执行前防护 (Pre-Execution)

**目标:** 阻止危险操作

| 机制 | 实现 | 触发条件 |
|------|------|---------|
| 风险评级 | `risk_assessor.py` | 所有工具调用前 |
| 影响分析 | `impact_analyzer.py` | 修改/删除操作前 |
| 用户确认 | `confirmation_gate.py` | 高风险操作前 |

**风险等级:**
```
🟢 低风险：读取、查询、分析 → 直接执行
🟡 中风险：创建、修改 → 记录日志
🔴 高风险：删除、覆盖、同步 → 必须用户确认
```

---

### Layer 2: 执行中防护 (In-Execution)

**目标:** 确保单步执行、可追溯

| 机制 | 实现 | 检查点 |
|------|------|--------|
| 单步锁 | `single_step_lock.py` | 每步执行前 |
| 工具调用追踪 | `tool_call_tracker.py` | 每次调用 |
| 状态快照 | `state_snapshot.py` | 每步完成后 |

**执行流程:**
```
1. 获取单步锁
2. 记录工具调用
3. 执行工具
4. 保存状态快照
5. 释放单步锁
```

---

### Layer 3: 执行后防护 (Post-Execution)

**目标:** 验证结果、可回滚

| 机制 | 实现 | 验证内容 |
|------|------|---------|
| 结果验证 | `result_verifier.py` | 输出符合预期 |
| 一致性检查 | `consistency_checker.py` | 状态一致 |
| 自动备份 | `auto_backup.py` | 修改前备份 |
| 回滚机制 | `rollback_manager.py` | 需要时恢复 |

---

### Layer 4: 规则强制 (Rule Enforcement)

**目标:** 核心规则不可违反

| 规则 | 执行机制 | 违规后果 |
|------|---------|---------|
| 严禁编造 | `anti_fabrication_check.py` | 阻断 + 报警 |
| 单步执行 | `single_step_enforcer.py` | 阻断多步 |
| 工具调用获取 | `tool_call_validator.py` | 验证来源 |
| 无法完成要终止 | `termination_checker.py` | 强制上报 |

---

## 实现计划

### Phase 1: 紧急防护 (立即)
- [ ] `risk_assessor.py` - 风险评级
- [ ] `confirmation_gate.py` - 用户确认门
- [ ] `auto_backup.py` - 自动备份

### Phase 2: 执行防护 (今日)
- [ ] `single_step_lock.py` - 单步锁
- [ ] `state_snapshot.py` - 状态快照
- [ ] `result_verifier.py` - 结果验证

### Phase 3: 规则强制 (明日)
- [ ] `anti_fabrication_check.py` - 反编造检查
- [ ] `single_step_enforcer.py` - 单步强制执行
- [ ] `rollback_manager.py` - 回滚管理

---

## 验收标准

1. ✅ 高风险操作必须用户确认
2. ✅ 所有修改自动备份
3. ✅ 每步执行可追溯
4. ✅ 违规操作被阻断
5. ✅ 支持一键回滚

---

**request_id:** session-20260320081906  
**server_time:** 2026-03-20T08:25:00+08:00  
**status:** 设计完成
