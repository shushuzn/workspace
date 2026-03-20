# 防护系统强化 v4.0 - 不可绕过

**日期:** 2026-03-20
**会话:** session-20260320111128

---

## 问题

用户指出："仍然能跳过 session，强化防护"

**可绕过的漏洞:**
1. `git commit --no-verify` - 跳过 pre-commit hook
2. 直接调用工具脚本 - 不通过 tool_wrapper
3. 修改 execution-state.json - 手动伪造 session
4. 使用 git 命令而不是包装器

---

## 解决方案

### 1. Pre-commit Hook v4.0 - 检测 --no-verify

**文件:** `.git/hooks/pre-commit`

**防护:**
- 检测 `GIT_NO_VERIFY` 环境变量
- 检测是否通过 `--no-verify` 调用
- 强制 session 检查
- 强制 tool_call_log 检查
- 强制 Workflow Guardian 检查
- 强制 Tool Call Tracker 检查

### 2. 模块级 Session 检查

**文件:** `30-scripts-tools/safe_shell_executor.py`

**防护:**
- 在模块导入时立即检查 session（不是函数内部）
- 无法通过导入后调用来绕过
- 检查在有任何代码执行前就进行

```python
# 模块加载时强制检查 - 在有任何代码执行前
_force_session_check()
```

### 3. Python Site Customize - 系统级拦截

**文件:** `30-scripts-tools/sitecustomize.py`

**防护:**
- 在所有 Python 脚本执行前自动运行
- 检查是否在工具目录
- 检查是否有 session
- 记录所有 Python 脚本执行

**激活方式:**
```bash
set PYTHONPATH=D:\OpenClaw\workspace\30-scripts-tools
```

### 4. Git 命令包装器

**文件:** 
- `30-scripts-tools/safe_git_executor.py` (Python)
- `30-scripts-tools/git_wrapper.bat` (批处理)

**防护:**
- 禁止 `--no-verify` 参数
- 禁止 `--no-hooks` 参数
- 禁止 `-n` 简写
- 强制 session 检查

### 5. Git Commit Helper 更新

**文件:** `30-scripts-tools/git_commit_helper.py`

**防护:**
- 在 main() 开始就检查禁止参数
- 发现 `--no-verify` 立即拒绝
- 不允许传递给 git

### 6. 工具执行器强化

**文件:** `30-scripts-tools/tool_executor.py`

**防护:**
- 集成 tool_wrapper
- before_tool_call 检查 session
- after_tool_call 记录日志

---

## 防护测试结果

```
测试：safe_shell_executor 无 session
  [PASS] 已阻断

测试：tool_executor 无 session
  [PASS] 已阻断

测试：git_commit_helper --no-verify
  [PASS] 已阻断

测试：safe_git_executor --no-verify
  [PASS] 已阻断

测试结果：4/4 通过
```

---

## 防护层级

| 层级 | 防护 | 绕过难度 |
|------|------|---------|
| **系统级** | sitecustomize.py | 🔴 需要修改 Python 环境 |
| **Git 级** | pre-commit hook v4.0 | 🔴 需要修改 hook |
| **命令级** | safe_git_executor | 🟡 需要使用包装器 |
| **模块级** | safe_shell_executor 模块检查 | 🟡 需要修改源码 |
| **函数级** | tool_wrapper | 🟢 标准检查 |

---

## 使用方式

### 启动会话
```bash
py 30-scripts-tools/copaw_entry.py "任务名称"
```

### 执行 Shell 命令
```bash
py 30-scripts-tools/safe_shell_executor.py "command"
```

### 执行 Git 命令
```bash
py 30-scripts-tools/safe_git_executor.py commit -m "message"
# 或
py 30-scripts-tools/git_commit_helper.py "message"
```

### 测试防护
```bash
py 30-scripts-tools/test_protection.py
```

---

## 核心原则

> **"无 session，不执行"**

- ✅ 所有工具调用强制检查 session
- ✅ 所有 git 提交强制检查 workflow
- ✅ 禁止任何方式绕过防护
- ✅ 模块级检查（导入时就检查）
- ✅ 系统级拦截（sitecustomize）

---

## 提交文件

| 文件 | 说明 |
|------|------|
| `.git/hooks/pre-commit` | v4.0 - 检测 --no-verify |
| `30-scripts-tools/safe_shell_executor.py` | 模块级 session 检查 |
| `30-scripts-tools/sitecustomize.py` | 系统级 Python 拦截 |
| `30-scripts-tools/safe_git_executor.py` | Git 命令包装器 |
| `30-scripts-tools/git_wrapper.bat` | Git 批处理包装器 |
| `30-scripts-tools/git_commit_helper.py` | 禁止 --no-verify |
| `30-scripts-tools/test_protection.py` | 防护测试 |

---

**状态:** 完成，等待提交
