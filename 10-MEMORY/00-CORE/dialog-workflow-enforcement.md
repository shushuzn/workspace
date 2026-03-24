# 对话工作流强制系统

**日期:** 2026-03-20
**会话:** session-20260320111128

---

## 问题

用户指出："对话仍无法强制调用工作流"

**根本问题:**
- LLM 可以直接回复用户，不经过任何脚本
- 工具调用被防护，但对话响应没有防护
- 没有机制强制 LLM 在回复前检查工作流

---

## 解决方案

### 1. 对话工作流强制器 (`dialog_workflow_enforcer.py`)

**功能:**
- 检查 session 状态
- 判断问题复杂度
- 决定是否允许回复

**检查逻辑:**
```python
def enforce_workflow(user_input: str) -> dict:
    has_session, workflow_type = check_session()
    is_simple = is_simple_question(user_input)
    
    if has_session:
        return {"allowed": True, "workflow_type": workflow_type}
    
    if is_simple:
        return {"allowed": True, "workflow_type": "none", "warning": "..."}
    
    return {"allowed": False, "message": "必须先启动 session"}
```

**简单问题列表:**
- 时间、日期、状态、版本
- 长度 < 20 字符
- 无工作流关键词

**需要 session 的任务:**
- 研究、分析、报告
- 创建、修改、执行
- 代码、脚本、工具
- 文件操作、git 提交

### 2. 对话入口 (`dialog_entry.py`)

**功能:**
- 所有对话必须通过此入口
- 无 session 时自动启动简化会话
- 记录所有对话到工作流日志

**使用方式:**
```bash
py 30-scripts-tools/dialog_entry.py "用户问题"
```

### 3. Pre-commit Hook 检查

**新增 Check 3.6:**
```bash
# 检查对话日志关联
echo "[Check 3.6] Checking dialog log association..."
if [ -f "dialog/${TODAY}.jsonl" ]; then
    # 检查是否有 session_id
    py -c "检查 session 关联"
fi
```

### 4. SOUL.md 更新

**新增规则:**
- 每次回复前检查 session 状态
- 无 session + 复杂任务 → 拒绝回复
- 有 session → 强制记录到工作流

---

## 工作流程

### 场景 1: 有 session

```
用户：帮我分析这个数据
  ↓
检查 session → 存在
  ↓
允许回复 + 记录到工作流步骤
  ↓
LLM 回复
```

### 场景 2: 无 session + 简单问题

```
用户：现在几点？
  ↓
检查 session → 不存在
检查问题 → 简单
  ↓
允许回复 + 警告
  ↓
LLM 回复
```

### 场景 3: 无 session + 复杂任务

```
用户：创建研究报告
  ↓
检查 session → 不存在
检查问题 → 复杂
  ↓
拒绝回复
  ↓
返回：必须先启动 session
```

---

## 使用方式

### 启动会话

**完整工作流:**
```bash
py 30-scripts-tools/copaw_entry.py "任务描述"
```

**简化工作流（仅问答）:**
```bash
py 30-scripts-tools/copaw_entry.py "简单问答" --simplified
```

### 对话入口

**推荐方式:**
```bash
py 30-scripts-tools/dialog_entry.py "用户问题"
```

**自动处理:**
- 无 session → 自动启动简化会话
- 有 session → 关联到现有会话
- 记录所有对话到日志

---

## 防护层级

| 层级 | 防护 | 效果 |
|------|------|------|
| **对话入口** | dialog_entry.py | 🟡 需要手动使用 |
| **强制器检查** | dialog_workflow_enforcer.py | 🟢 自动检查 |
| **Pre-commit** | Check 3.6 | 🟢 提交时验证 |
| **SOUL 规则** | LLM 自我约束 | 🟡 依赖遵守 |

---

## 限制

### 当前限制

1. **LLM 自我约束** - 最终依赖 LLM 遵守规则
2. **无法完全强制** - LLM 可以直接回复
3. **需要入口脚本** - 用户需要使用 dialog_entry.py

### 未来改进

1. **系统级拦截** - 修改 agent 响应逻辑
2. **自动 session** - 无 session 时自动启动
3. **对话审计** - 记录所有对话并验证

---

## 提交文件

| 文件 | 说明 |
|------|------|
| `30-scripts-tools/dialog_workflow_enforcer.py` | 对话强制器 |
| `30-scripts-tools/dialog_entry.py` | 对话入口 |
| `.git/hooks/pre-commit` | 添加 Check 3.6 |
| `SOUL.md` | 添加对话工作流规则 |

---

## 核心原则

> **"无 session，不回复复杂任务"**

- ✅ 每次回复前检查 session
- ✅ 简单问题可以直接回复
- ✅ 复杂任务必须有 session
- ✅ 所有对话记录到日志
- ✅ 提交时验证对话关联

---

**状态:** 完成，等待提交
