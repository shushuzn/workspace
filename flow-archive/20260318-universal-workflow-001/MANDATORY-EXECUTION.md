# 强制执行主工作流 - Mandatory Workflow Execution

**版本:** 1.5.0  
**更新日期:** 2026-03-21  
**工作流:** 20260318-universal-workflow-001

---

## 🎯 核心原则

> **所有任务必须通过主工作流执行，禁止绕过。**

---

## 🛡️ 强制执行机制

### 三层防护

| 层级 | 机制 | 说明 |
|------|------|------|
| **L1: 入口点** | copaw_entry.py | 所有任务必须从此入口启动 |
| **L2: 执行器** | workflow_auto_executor.py | 自动执行 20 步 |
| **L3: 验证** | workflow_guardian + tool_call_tracker | Git 提交前验证 |

---

## 📋 使用方式

### 方式 1: 手动执行任务

```bash
# 1. 通过入口点启动
py 30-scripts-tools\copaw_entry.py "我的任务名称"

# 2. 执行任务 (工具调用会自动记录)
# ... 执行你的任务 ...

# 3. 结束会话 (在 Python 中)
entry.finalize(success=True)
```

### 方式 2: 自动执行工作流

```bash
# 自动执行完整 20 步工作流
py 30-scripts-tools\workflow_auto_executor.py "我的任务名称"
```

### 方式 3: 命令行快捷方式

```bash
# 创建批处理文件 workflow.bat
@echo off
py 30-scripts-tools\copaw_entry.py %*
```

---

## 🔧 工作流程

```
任务开始
    ↓
copaw_entry.py (强制入口点)
    ↓
1. 初始化 execution-state.json
2. 绑定 Flow ID + Session ID
3. 验证上下文加载 (Step 1)
    ↓
workflow_auto_executor.py (自动执行器)
    ↓
按顺序执行 20 步
    ↓
每步调用工具 → 记录到 tool_call_log.jsonl
    ↓
Git 提交前验证
    ├── workflow_guardian_v2.py (检查完成率)
    └── tool_call_tracker.py (检查调用日志)
    ↓
两者都通过 → Git 提交
任一失败 → 拒绝提交
    ↓
entry.finalize() (结束会话)
```

---

## 🚫 被禁止的行为

| 行为 | 状态 | 后果 |
|------|------|------|
| 直接执行工具脚本 | ❌ 禁止 | Git 提交被拒绝 |
| 绕过 copaw_entry | ❌ 禁止 | 无 execution-state.json |
| 不记录工具调用 | ❌ 禁止 | tool_call_tracker 失败 |
| 手动编辑 execution-state | ❌ 禁止 | 类型不匹配 |
| 跳过工作流步骤 | ❌ 禁止 | completion_percentage <100% |

---

## ✅ 验证检查

### Git Pre-commit Hook 自动执行

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 1. 检查 entry point 是否被使用
if [ ! -f "flow-archive/20260318-universal-workflow-001/execution-state.json" ]; then
    echo "[FAIL] execution-state.json 不存在"
    echo "[FAIL] 必须通过 copaw_entry.py 启动任务"
    exit 1
fi

# 2. 工作流验证
py workflow_guardian_v2.py
if [ $? -ne 0 ]; then
    echo "[FAIL] Workflow validation failed"
    exit 1
fi

# 3. 工具调用日志验证
py tool_call_tracker.py
if [ $? -ne 0 ]; then
    echo "[FAIL] Tool call verification failed"
    exit 1
fi

echo "[OK] All checks passed"
exit 0
```

---

## 📊 违规检测

### anti_bypass 配置

```json
"mandatory_execution": {
  "anti_bypass": {
    "enabled": true,
    "detect_direct_tool_calls": true,
    "detect_missing_state_file": true,
    "detect_missing_tool_log": true,
    "action_on_violation": "block_and_report"
  }
}
```

### 检测场景

| 场景 | 检测方法 | 动作 |
|------|----------|------|
| 直接调用工具脚本 | 检查 tool_call_log | 拒绝 Git 提交 |
| 缺少 execution-state | 检查文件存在性 | 拒绝 Git 提交 |
| 缺少工具调用日志 | 检查日志条目 | 拒绝 Git 提交 |
| 完成率<100% | workflow_guardian | 拒绝 Git 提交 |

---

## 🎯 执行示例

### 示例 1: 创建工具

```bash
# 错误方式 (被禁止)
py 30-scripts-tools\create_tool.py

# 正确方式
py 30-scripts-tools\copaw_entry.py "创建工具 - 防造假系统"
py 30-scripts-tools\workflow_auto_executor.py "创建工具 - 防造假系统"
```

### 示例 2: 研究任务

```bash
# 错误方式 (被禁止)
py 30-scripts-tools\research_task.py

# 正确方式
py 30-scripts-tools\copaw_entry.py "研究 CNT 导电性"
py 30-scripts-tools\workflow_auto_executor.py "研究 CNT 导电性"
```

### 示例 3: 日常对话

```bash
# 错误方式 (被禁止)
# 直接聊天

# 正确方式
py 30-scripts-tools\copaw_entry.py "对话 - 讨论工作流优化"
# 对话内容会自动记录到日志
py 30-scripts-tools\workflow_auto_executor.py "对话 - 讨论工作流优化"
```

---

## 📈 合规性指标

| 指标 | 目标 | 当前 |
|------|------|------|
| 入口点使用率 | 100% | 待统计 |
| 工作流完成率 | 100% | 待统计 |
| 工具调用记录率 | 100% | 待统计 |
| Git 提交通过率 | 100% | 待统计 |

---

## 🔍 故障排除

### 问题 1: Git 提交被拒绝

```
[FAIL] Workflow Guardian 验证失败！
[BLOCK] Git 提交被阻止！
```

**解决:**
1. 检查 execution-state.json 是否存在
2. 运行 workflow_guardian_v2.py 查看详细错误
3. 修复后重新提交

### 问题 2: 工具调用日志为空

```
工具调用过少：0 calls for 20 steps
```

**解决:**
1. 确保通过 copaw_entry 启动
2. 确保工具调用通过 tool_executor
3. 检查 tool_call_log.jsonl 是否被写入

### 问题 3: 完成率不是 100%

```
完成率计算错误 - 报告值=50%, 实际值=100%
```

**解决:**
1. 运行 workflow_guardian_v2.py --auto-fix
2. 或手动更新 execution-state.json

---

## ✅ 验收标准

- [ ] copaw_entry.py 创建完成
- [ ] workflow_auto_executor.py 创建完成
- [ ] workflow.json v1.5.0 配置完成
- [ ] pre-commit hook 更新
- [ ] 测试：绕过入口点被拒绝
- [ ] 测试：完整流程通过
- [ ] 文档完整

---

## 🎯 核心原则

> **让绕过工作流比使用工作流更困难。**

**当前状态:**
- 绕过工作流：可能，但会被检测
- 使用工作流：自动化，一键执行

**目标状态:**
- 绕过工作流：**不可能** (系统级阻止)
- 使用工作流：自动化，无感执行

---

**更新完成:** 2026-03-21  
**状态:** ✅ 已部署 (v1.5.0)
