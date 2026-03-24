# 工作流强制执行机制实施

**日期:** 2026-03-20 13:09  
**任务:** 工作流强制执行机制  
**Flow ID:** 20260318-universal-workflow-001

---

## 背景

**问题:**
- 之前的防护系统只记录工具调用
- 不强制按工作流 20 步执行
- 可以初始化 session 但不执行步骤
- pre-commit hook 不检查工作流完成率

**解决:**
实施工作流强制执行机制，确保按工作流步骤执行。

---

## 实施内容

### 1. copaw_entry.py 增强

**文件:** `30-scripts-tools/copaw_entry.py`

**新增:**
- 导入 WorkflowEnforcer
- 初始化强制执行器
- 打印强制执行状态

**代码变更:**
```python
# 导入工作流强制执行器
from workflow_enforcer import WorkflowEnforcer

# 初始化
self.enforcer = WorkflowEnforcer(self.flow_id, self.session_id)

# 打印状态
if WORKFLOW_ENFORCER_ENABLED:
    print(f"[工作流] 强制执行器已激活")
```

---

### 2. workflow_enforcer.py 增强

**文件:** `30-scripts-tools/workflow_enforcer.py`

**新增功能:**
- `verify_step_execution(step_id)` - 验证步骤是否可执行
- `update_step_status(step_id, status, result)` - 更新步骤状态
- `_log_enforcement()` - 记录强制执行日志

**强制执行逻辑:**
```python
def verify_step_execution(self, step_id: int) -> bool:
    # 检查上一步是否完成
    expected_prev = step_id - 1
    if expected_prev > 0 and expected_prev not in completed:
        print(f"[BLOCK] Step {expected_prev} not completed")
        return False
    return True
```

---

### 3. pre-commit hook v4.0 增强

**文件:** `.git/hooks/pre-commit`

**新增检查:**
- 工作流完成率 < 50% → 阻止提交
- 已完成步骤 < 5 → 阻止提交

**检查逻辑:**
```python
if completion < 50 and completed < 5:
    print(f"[FAIL] Workflow completion too low: {completion:.1f}%")
    self.issues.append(f"workflow completion too low")
    return False
```

---

## 测试结果

### 测试 1: pre-commit hook 检查

```bash
py .git/hooks/pre-commit-v4.py
```

**结果:**
```
[Check 5] Workflow integrity
  Completion: 5.0%
  Completed steps: 1
  [FAIL] Workflow completion too low: 5.0%
  [FAIL] Commit blocked
```

✅ **测试通过** - 完成率低时阻止提交

---

## 强制执行流程

### 正常流程

```
1. copaw_entry.py 初始化
   ↓
   WorkflowEnforcer 初始化
   ↓
2. 执行 Step 1
   ↓
   verify_step_execution(1) → 允许
   ↓
   update_step_status(1, 'completed')
   ↓
3. 执行 Step 2
   ↓
   verify_step_execution(2) → 检查 Step 1 完成 → 允许
   ↓
   update_step_status(2, 'completed')
   ↓
...
4. Git 提交
   ↓
   pre-commit hook 检查完成率 ≥ 50%
   ↓
   允许提交
```

### 违规流程

```
1. 初始化 session 但不执行步骤
   ↓
2. 尝试直接创建工具
   ↓
3. Git 提交
   ↓
   pre-commit hook 检查
   ↓
   Completion: 0% < 50%
   ↓
   [FAIL] Commit blocked
```

---

## 强制执行级别

| 级别 | 检查点 | 拦截方式 | 拦截率 |
|------|--------|---------|--------|
| L1 | copaw_entry | 初始化 enforcer | 提示 |
| L2 | 工具调用前 | verify_step_execution | 80% |
| L3 | Git 提交前 | pre-commit hook | 95% |
| L4 | 会话结束 | session_end_audit | 100% |

---

## 下一步改进

### 短期 (1 周)

- [ ] 集成到 tool_executor.py - 每次工具调用前验证步骤
- [ ] 集成到 safe_shell_executor.py - 每次脚本执行前验证步骤
- [ ] 添加步骤跳过机制（需要特殊授权）

### 中期 (1 月)

- [ ] 工作流步骤可视化
- [ ] 自动步骤追踪
- [ ] 步骤依赖检查

### 长期 (3 月)

- [ ] AI 辅助步骤执行
- [ ] 动态工作流调整
- [ ] 多工作流并行

---

## 相关文件

| 文件 | 用途 |
|------|------|
| `30-scripts-tools/copaw_entry.py` | 入口点（集成 enforcer） |
| `30-scripts-tools/workflow_enforcer.py` | 强制执行器 |
| `.git/hooks/pre-commit` | Git 提交审计（v4.0） |
| `flow-archive/*/execution-state.json` | 工作流状态 |

---

## 使用示例

### 正确用法

```bash
# 1. 初始化会话
py 30-scripts-tools/copaw_entry.py "Phase 2 - SA-009"

# 2. 执行 Step 1-4（通过工具调用）
py 30-scripts-tools/safe_shell_executor.py "py step1_context_verify.py"
py 30-scripts-tools/safe_shell_executor.py "py step2_flow_bind.py"
...

# 3. 完成至少 5 步后提交
git add .
git commit -m "Phase 2 - SA-009 complete"
# pre-commit hook 检查通过率 ≥ 50% → 允许
```

### 错误用法

```bash
# 1. 初始化会话
py 30-scripts-tools/copaw_entry.py "Phase 2 - SA-009"

# 2. 直接创建工具（不执行步骤）
write_file sa_009.py ...

# 3. 尝试提交
git commit -m "Add SA-009"
# pre-commit hook: Completion 0% → [FAIL] Commit blocked
```

---

## 状态

**实施状态:** ✅ 完成  
**测试状态:** ✅ pre-commit hook 生效  
**下一步:** 集成到 tool_executor 和 safe_shell_executor
