# 工具调用规则 - 强制性审查标准

**版本:** v1.0.0  
**生效日期:** 2026-03-19  
**位置:** `30-scripts-tools/tools_registry.json`

---

## 📜 核心原则

### 1. 禁止重写工具原则
> **所有工具脚本禁止被其他脚本重写或修改**

**违规示例:**
```python
# ❌ 禁止：直接修改工具脚本
with open('30-scripts-tools/context_search.py', 'w') as f:
    f.write(new_code)
```

**合规示例:**
```python
# ✅ 合规：通过 tools_registry.json 配置调整
registry['tools']['context_search']['command'] = 'py context_search.py --demo'
```

**理由:**
- 保持工具稳定性和一致性
- 避免工具行为被意外修改
- 确保工具可追溯、可审计

---

### 2. 统一调用原则
> **所有工具只能通过 tool_executor.py 调用，禁止直接调用工具脚本**

**违规示例:**
```python
# ❌ 禁止：直接调用工具脚本
subprocess.run(['py', '30-scripts-tools/context_search.py', '--demo'])
```

**合规示例:**
```python
# ✅ 合规：通过 tool_executor 调用
subprocess.run(['py', '30-scripts-tools/tool_executor.py', 'context_search'])
```

**理由:**
- 确保步骤追踪自动生效
- 确保强制检查统一执行
- 确保日志记录完整
- 确保工作流合规性验证

---

### 3. 工具注册原则
> **新工具必须注册到 tools_registry.json**

**违规示例:**
```python
# ❌ 禁止：创建未注册的工具脚本
# 创建了 30-scripts-tools/new_tool.py 但未注册
```

**合规示例:**
```python
# ✅ 合规：使用 register_tools.py 批量注册
py 30-scripts-tools/register_tools.py

# 或手动添加到 tools_registry.json
{
  "tools": {
    "new_tool": {
      "tool_id": "new_tool",
      "command": "py 30-scripts-tools/new_tool.py",
      "description": "新工具描述"
    }
  }
}
```

**理由:**
- 确保工具可追踪
- 确保工具可验证
- 确保工具可审计

---

## 🔍 审查检查表

### 代码审查时必须检查:

- [ ] 是否有直接调用工具脚本的代码？
- [ ] 是否有修改工具脚本的代码？
- [ ] 是否有未注册的工具？
- [ ] 所有工具调用是否通过 tool_executor？

### 自动化检查脚本:

```bash
# 检查直接调用工具脚本的代码
grep -r "subprocess.run.*\.py" 30-scripts-tools/ --include="*.py"

# 检查修改工具脚本的代码
grep -r "open.*\.py.*'w'" 30-scripts-tools/ --include="*.py"

# 检查未注册的工具
py 30-scripts-tools/check_unregistered_tools.py
```

---

## 🚨 违规处理

### 一级违规（直接调用工具）
- **警告**
- **要求整改**
- **代码审查不通过**

### 二级违规（重写工具）
- **严重警告**
- **回滚修改**
- **代码审查不通过**
- **记录到 MEMORY.md**

### 三级违规（恶意修改）
- **禁止访问权限**
- **报告管理员**
- **记录到 MEMORY.md**

---

## 📋 合规工具调用流程

```
┌─────────────┐
│ 工作流脚本   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ tool_executor│ ← 唯 一 合 法 调 用 方 式
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ tools_registry│ ← 查 找 工 具 命 令
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 工具脚本     │
└─────────────┘
```

---

## 📖 相关文档

- `tools_registry.json` - 工具注册表（唯一真值来源）
- `tool_executor.py` - 工具执行器（唯一调用入口）
- `workflow_enforcer.py` - 工作流强制检查
- `auto_execute_workflow.py` - 自动化工作流执行（合规示例）

---

## ✅ 合规模板

### auto_execute_workflow.py (合规示例)

```python
def execute_step_via_executor(tool_id):
    """通过 tool_executor 执行工具（唯一合法方式）"""
    result = subprocess.run([
        sys.executable,
        str(TOOL_EXECUTOR),  # tool_executor.py
        tool_id              # 工具 ID（从 registry 查找）
    ], cwd=str(WORKSPACE), capture_output=True, text=True)
    
    return result.returncode == 0
```

### 工作流配置 (合规示例)

```json
{
  "step_id": 1,
  "name": "上下文加载验证",
  "tool_id": "context_search",  // ← 引用 tool_id，禁止硬编码命令
  "blocking": true
}
```

---

**记住:**
> 工具是系统的基石，必须保持稳定、一致、可追溯。
> 任何对工具的修改或绕过都是对系统完整性的威胁。
