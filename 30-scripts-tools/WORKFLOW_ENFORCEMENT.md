# 🛡️ 工作流强制执行系统

**创建日期:** 2026-03-20  
**目的:** 防止不按主工作流执行

---

## 📋 系统组成

### 1. 会话前检查 (`start-session.bat`)
**作用:** 每次会话开始前强制检查工作流合规性

**使用方式:**
```bash
start-session.bat
```

**检查项:**
- ✅ 主工作流配置文件是否存在
- ✅ Flow ID 是否已绑定
- ✅ 当日笔记大小 (<5KB)
- ✅ 未完成的必需步骤

**阻止条件:**
- 主工作流配置不存在 → **阻止会话**
- 必需步骤未完成 → **警告并要求执行**

---

### 2. Git Pre-Commit Hook (`.git/hooks/pre-commit`)
**作用:** 每次 Git 提交前强制检查

**自动触发:** `git commit` 时自动运行

**检查项:**
- ✅ 当日笔记是否存在且 <5KB
- ✅ 工具文件是否已注册
- ✅ 工作流步骤是否完成

**阻止条件:**
- 当日笔记 >5KB → **阻止提交**
- 工具未注册 → **警告**
- 必需步骤未完成 → **阻止提交**

---

### 3. 会话结束检查 (`end-session.bat`)
**作用:** 会话结束时强制压缩 + 检查

**使用方式:**
```bash
end-session.bat
```

**检查流程:**
1. 检查当日笔记是否存在
2. 检查当日笔记大小 (<5KB)
3. 运行 Git 提交前合规检查
4. 执行 Git 提交

**阻止条件:**
- 当日笔记不存在 → **阻止结束**
- 当日笔记 >5KB → **阻止结束**
- 合规检查失败 → **阻止提交**

---

### 4. 工作流强制执行器 (`workflow_enforcer.py`)
**作用:** Python 级别的强制执行检查

**API:**
```python
from workflow_enforcer import WorkflowEnforcer

enforcer = WorkflowEnforcer()

# 任务前检查
enforcer.enforce_before_task("任务描述")

# 提交前检查
enforcer.enforce_before_commit(completed_steps)
```

**检查维度:**
- 工作流加载验证
- Flow ID 绑定验证
- 步骤完成度检查
- 笔记大小验证

---

### 5. 提交前检查器 (`pre_commit_checker.py`)
**作用:** 详细的 Git 提交前检查

**检查项:**
- 主工作流配置文件存在性
- 当日笔记大小
- 最近提交消息
- 未跟踪的工具文件

---

### 6. 工具注册检查器 (`check_tool_registration.py`)
**作用:** 确保所有工具都已注册

**检查逻辑:**
- 扫描 `30-scripts-tools/*.py`
- 对比 `tools_registry.json`
- 报告未注册工具

---

## 🚀 使用流程

### 开始会话
```bash
# 1. 启动会话 (强制检查)
start-session.bat

# 2. 按主工作流执行
# Step 1: 上下文加载验证
# Step 2: Flow ID 绑定
# Step 3: 任务解析
# ...
```

### 结束会话
```bash
# 1. 压缩当日笔记 (自动)
py 30-scripts-tools\post_session_compress.py --auto

# 2. 结束会话 (强制检查 + 提交)
end-session.bat
```

---

## 📊 检查点矩阵

| 检查点 | 触发时机 | 检查内容 | 阻止级别 |
|--------|----------|----------|----------|
| **会话前检查** | 运行 `start-session.bat` | 工作流配置、Flow ID | 🔴 严重 |
| **任务前检查** | 执行任务前 | 必需步骤完成度 | 🟡 警告 |
| **提交前检查** | Git commit 前 | 笔记大小、工具注册 | 🔴 严重 |
| **会话结束检查** | 运行 `end-session.bat` | 笔记压缩、合规性 | 🔴 严重 |
| **Git Hook** | 每次 `git commit` | 综合合规性 | 🔴 严重 |

---

## ⚠️ 常见阻止场景

### 场景 1: 忘记压缩笔记
```
❌ 当日笔记过大：7200 bytes (>5KB)
[BLOCK] Git 提交被阻止！
[ACTION] 请先压缩会话笔记！
```

**解决:**
```bash
py 30-scripts-tools\post_session_compress.py --auto
```

---

### 场景 2: 工具未注册
```
⚠️ 以下工具未注册:
  - my_new_tool.py
[ACTION] 请运行注册命令
```

**解决:**
```bash
# 手动添加到 tools_registry.json
# 或运行注册脚本
```

---

### 场景 3: 步骤未完成
```
[WARN] 未完成步骤：3
  - 工具集成验证
  - 会话压缩保存
  - Git 提交推送
[BLOCK] 不允许 Git 提交！
```

**解决:**
```bash
# 按顺序完成缺失步骤
# 1. 工具集成验证
# 2. 会话压缩保存
# 3. 运行 end-session.bat
```

---

## 📈 执行日志

所有强制执行检查都会记录到:
- `flow-archive/20260318-universal-workflow-001/enforcement-log.json`

**日志格式:**
```json
{
  "timestamp": "2026-03-20T21:45:00",
  "action": "before_commit",
  "passed": true,
  "details": {
    "compliance_rate": 100.0,
    "note_size_kb": 1.4
  }
}
```

---

## 🎯 预期效果

| 指标 | 实施前 | 实施后 | 改进 |
|------|--------|--------|------|
| **工作流合规率** | ~60% | 100% | +40% |
| **笔记压缩率** | ~50% | 100% | +50% |
| **Git 提交成功率** | ~80% | 100% | +20% |
| **工具注册率** | ~70% | 100% | +30% |

---

## 🔧 维护说明

### 添加新检查项
1. 编辑 `workflow_enforcer.py`
2. 在 `check_*` 方法中添加检查逻辑
3. 更新 `REQUIRED_STEPS` 列表
4. 测试并注册工具

### 更新阻止阈值
- 笔记大小阈值：`5120 bytes` (5KB)
- 步骤完成度阈值：`100%`
- 工具注册率阈值：`100%`

### 禁用检查 (紧急情况)
```bash
# 临时禁用 Git Hook
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled

# 跳过会话前检查
# 直接运行 Python 脚本而不使用 start-session.bat
```

**注意:** 禁用检查需要人工审批！

---

## 📚 相关文件

- `start-session.bat` - 会话启动脚本
- `end-session.bat` - 会话结束脚本
- `.git/hooks/pre-commit` - Git 提交钩子
- `30-scripts-tools/workflow_enforcer.py` - 工作流强制执行器
- `30-scripts-tools/pre_commit_checker.py` - 提交前检查器
- `30-scripts-tools/check_tool_registration.py` - 工具注册检查器
- `flow-archive/20260318-universal-workflow-001/enforcement-log.json` - 执行日志

---

**系统状态:** ✅ 已激活  
**最后更新:** 2026-03-20  
**Git 提交:** 最新提交包含所有强制执行工具
