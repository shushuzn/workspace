# 工作流强制防护系统 - 提交说明

**日期:** 2026-03-20
**会话:** session-20260320105005

---

## 问题

**用户指出:** "你还能不用工作流，强化防护"

**根本问题:**
- 工具调用（write_file, edit_file 等）可以直接使用
- 没有强制检查 session 状态
- 可以绕过工作流直接执行操作

---

## 解决方案

### 1. 创建工具调用包装器 (`tool_wrapper.py`)

**功能:**
- 每次工具调用前自动检查 session
- 无 session → 拒绝执行
- 有 session → 记录调用日志

**使用方式:**
```python
from tool_wrapper import before_tool_call, after_tool_call

def my_tool(params):
    if not before_tool_call('my_tool', params):
        raise PermissionError("未初始化会话")
    # 执行工具逻辑
    result = ...
    after_tool_call('my_tool', params, result)
    return result
```

**装饰器:**
```python
from tool_wrapper import require_workflow

@require_workflow
def my_tool(params):
    # 自动检查 session
    ...
```

### 2. 测试结果

```
测试：无 session 时调用工具
结果：拒绝 ✓

输出:
======================================================================
[BLOCK] 工具调用被拒绝
[BLOCK] 原因：execution-state.json 不存在
[BLOCK] 请先运行：py 30-scripts-tools/copaw_entry.py <task>
======================================================================
```

---

## 提交文件

| 文件 | 说明 |
|------|------|
| `30-scripts-tools/tool_wrapper.py` | 工具调用包装器（核心防护） |
| `30-scripts-tools/test_wrapper_strict.py` | 测试脚本 |
| `30-scripts-tools/test_wrapper.py` | 测试脚本 |
| `30-scripts-tools/check_state_files.py` | 测试辅助 |

---

## 用户需要执行

```bash
cd D:\OpenClaw\workspace
git add .
git commit -m "Add-mandatory-workflow-enforcement-for-all-tool-calls"
git push
```

---

## 下一步

**需要将 tool_wrapper 集成到所有工具脚本中:**

1. `safe_shell_executor.py` - 添加 `before_tool_call`
2. `tool_executor.py` - 添加 `before_tool_call`
3. 所有其他工具脚本 - 添加 `@require_workflow` 装饰器

**这样可确保:**
- 所有工具调用都强制检查工作流
- 无法绕过 session 检查
- 所有操作都有日志记录

---

**状态:** 等待用户提交
