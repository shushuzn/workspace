# 工具调用规则实施总结

**日期:** 2026-03-19  
**状态:** ✅ 已完成  
**审查结果:** 0 违规

---

## 📜 核心规则

### 1. 禁止重写工具原则
> 所有工具脚本禁止被其他脚本重写或修改

**实施:**
- ✅ 写入 `tools_registry.json` principles
- ✅ 写入 `TOOL-CALLING-RULES.md`
- ✅ 自动化审查脚本 `check_tool_rules.py`

### 2. 统一调用原则
> 所有工具只能通过 `tool_executor.py` 调用，禁止直接调用工具脚本

**实施:**
- ✅ 写入 `tools_registry.json` enforcement_rules
- ✅ 写入 `TOOL-CALLING-RULES.md`
- ✅ 自动化审查脚本 `check_tool_rules.py`
- ✅ `auto_execute_workflow.py` 作为合规模板

### 3. 工具注册原则
> 新工具必须注册到 `tools_registry.json`

**实施:**
- ✅ 批量注册脚本 `register_tools.py`
- ✅ 核心工具手动注册 `register_core_tools.py`
- ✅ 自动化审查检测未注册工具

---

## 📊 工具统计

| 类别 | 数量 |
|------|------|
| 总工具数 | **380** |
| 核心工具 | 10 |
| 普通工具 | 370 |
| 审查违规 | **0** ✅ |

---

## 🔍 审查机制

### 自动化审查脚本

**文件:** `30-scripts-tools/check_tool_rules.py`

**检查项:**
1. 直接调用工具脚本 (违规)
2. 重写/修改工具脚本 (违规)
3. 未注册工具 (违规)

**执行方式:**
```bash
py 30-scripts-tools/check_tool_rules.py
```

**输出:**
```
✅ 无违规！所有代码遵守工具调用规则
```

---

## 📋 合规示例

### ✅ 合规：通过 tool_executor 调用

```python
# auto_execute_workflow.py
def execute_step_via_executor(tool_id):
    result = subprocess.run([
        sys.executable,
        str(TOOL_EXECUTOR),  # tool_executor.py
        tool_id
    ], cwd=str(WORKSPACE))
    return result.returncode == 0
```

### ❌ 违规：直接调用工具脚本

```python
# 禁止！
subprocess.run(['py', '30-scripts-tools/context_search.py', '--demo'])
```

### ✅ 合规：通过配置调整工具行为

```python
# 修改 tools_registry.json
registry['tools']['context_search']['command'] = 'py context_search.py --demo'
```

### ❌ 违规：重写工具脚本

```python
# 禁止！
with open('30-scripts-tools/context_search.py', 'w') as f:
    f.write(new_code)
```

---

## 🛡️ 保护机制

### 5 层保护

1. **规则文档** - `TOOL-CALLING-RULES.md`
2. **注册表原则** - `tools_registry.json` principles
3. **自动化审查** - `check_tool_rules.py`
4. **合规模板** - `auto_execute_workflow.py`
5. **Git 审查** - 代码提交前必须通过审查

---

## 📖 相关文档

- `tools_registry.json` - 工具注册表（唯一真值来源）
- `TOOL-CALLING-RULES.md` - 工具调用规则详细说明
- `tool_executor.py` - 工具执行器（唯一调用入口）
- `check_tool_rules.py` - 自动化审查脚本
- `auto_execute_workflow.py` - 合规执行示例

---

## 🎯 验收标准

- [x] 规则写入 `tools_registry.json`
- [x] 规则写入 `TOOL-CALLING-RULES.md`
- [x] 自动化审查脚本可用
- [x] 审查结果 0 违规
- [x] 所有工具已注册（380 个）
- [x] 合规模板可用

---

## 🚀 使用指南

### 开发者日常流程

1. **创建新工具**
   ```bash
   # 创建工具脚本
   echo "print('Hello')" > 30-scripts-tools/my_tool.py
   
   # 自动注册
   py 30-scripts-tools/register_tools.py
   
   # 验证
   py 30-scripts-tools/check_tool_rules.py
   ```

2. **使用工具**
   ```python
   # 合规方式
   subprocess.run(['py', 'tool_executor.py', 'my_tool'])
   
   # 违规方式（禁止！）
   subprocess.run(['py', 'my_tool.py'])
   ```

3. **代码审查**
   ```bash
   # 提交前必须通过
   py 30-scripts-tools/check_tool_rules.py
   ```

---

## 📈 持续改进

- [ ] Git 预提交钩子集成审查
- [ ] CI/CD 流水线集成审查
- [ ] 违规自动修复建议
- [ ] 工具使用统计报告

---

**总结:** 工具调用规则已全面实施，自动化审查机制已建立，系统工具管理进入规范化阶段。
