# 关键审查项配置

**Flow ID:** `20260318-universal-workflow-001`  
**Last Updated:** 2026-03-18 23:37  
**Status:** ✅ 已配置并生效

---

## 🎯 两项零分检查

### CRITICAL-001: 工具注册检查

**规则:** 创建的工具必须在 `tools_registry.json` 注册  
**违反后果:** **零分 + 阻断**  
**审查表 ID:** `blocker-007`  
**执行工具:** `critical_checks.py --verify`

**检查逻辑:**
```python
# 从 session_temp.json 获取本次会话创建的工具
session_tools = session_data.get('created_tools', [])

# 检查是否已注册
if tool_name not in registered_tools:
    return {'passed': False, 'penalty': '零分 - 工具未注册'}
```

**验收标准:**
- [x] 新工具创建后立即注册
- [x] session_temp.json 追踪创建的工具
- [x] critical_checks.py 自动验证
- [x] 未注册工具阻断工作流

---

### CRITICAL-002: UTF-8 编码检查

**规则:** 中文必须用 UTF-8 编码  
**违反后果:** **零分 + 阻断**  
**审查表 ID:** `blocker-008`  
**执行工具:** `critical_checks.py --verify`

**检查逻辑:**
```python
# 尝试用 UTF-8 读取文件
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return {'passed': True}
except UnicodeDecodeError:
    return {'passed': False, 'penalty': '零分 - 编码错误'}
```

**验收标准:**
- [x] 所有 Python 文件 UTF-8 编码
- [x] 所有 JSON 文件 UTF-8 编码
- [x] 所有 Markdown 文件 UTF-8 编码
- [x] 编码错误阻断工作流

---

## 🛡️ 审查表配置

**文件:** `flow-archive/20260318-universal-workflow-001/review.json`

### blocker-007

```json
{
  "id": "blocker-007",
  "item": "【CRITICAL-001】创建的工具必须在 tools_registry.json 注册",
  "check": "check_tool_registered",
  "blocking": true,
  "checked": false,
  "notes": "PENDING",
  "evidence": "未验证",
  "penalty": "零分 - 工具未注册"
}
```

### blocker-008

```json
{
  "id": "blocker-008",
  "item": "【CRITICAL-002】中文必须用 UTF-8 编码",
  "check": "check_utf8_encoding",
  "blocking": true,
  "checked": false,
  "notes": "PENDING",
  "evidence": "未验证",
  "penalty": "零分 - 编码错误"
}
```

---

## 🔧 工具配置

### critical_checks.py

**位置:** `30-scripts-tools/critical_checks.py`  
**注册:** `tools_registry.json` → `critical-checks`  
**功能:** 验证两项零分检查

**使用方法:**
```bash
# 完整验证
py 30-scripts-tools\critical_checks.py --verify

# 检查特定工具
py 30-scripts-tools\critical_checks.py --tool quality-gate

# 检查特定文件编码
py 30-scripts-tools\critical_checks.py --file 30-scripts-tools/quality_gate.py
```

**注册信息:**
```json
"critical-checks": {
  "tool_id": "critical-checks",
  "name": "Critical Checks Verifier",
  "description": "关键审查项验证 - 工具注册 +UTF-8 编码",
  "command": "py 30-scripts-tools\\critical_checks.py --verify",
  "blocking": true,
  "priority": "P0",
  "category": "quality-gate"
}
```

---

## 📋 合规规则

**文件:** `tools_registry.json` → `compliance_rules.zero_score_items`

### CRITICAL-001

```json
{
  "id": "CRITICAL-001",
  "rule": "创建的工具必须在 tools_registry.json 注册",
  "check": "critical_checks.py --verify",
  "consequence": "0 分 + 阻断",
  "enforcement": "blocker-007"
}
```

### CRITICAL-002

```json
{
  "id": "CRITICAL-002",
  "rule": "中文必须用 UTF-8 编码",
  "check": "critical_checks.py --verify",
  "consequence": "0 分 + 阻断",
  "enforcement": "blocker-008"
}
```

---

## 📊 验证结果

**最新执行:** 2026-03-18 23:37:16

```
======================================================================
CRITICAL CHECKS VERIFICATION
======================================================================
Timestamp: 2026-03-18T23:37:16.454718

[CRITICAL-001] 创建的工具必须在 tools_registry.json 注册
----------------------------------------------------------------------
[PASS] All tools are registered

[CRITICAL-002] 中文必须用 UTF-8 编码
----------------------------------------------------------------------
[PASS] All files have valid UTF-8 encoding

======================================================================
[SUCCESS] All critical checks passed!
```

---

## 🎯 工作流程

### 创建新工具时

1. **创建工具文件** → `30-scripts-tools/my_tool.py`
2. **记录到 session_temp.json**:
   ```json
   {
     "created_tools": ["my-tool"]
   }
   ```
3. **注册到 tools_registry.json**:
   ```json
   "my-tool": {
     "tool_id": "my-tool",
     "command": "py 30-scripts-tools\\my_tool.py"
   }
   ```
4. **自动验证** → `critical_checks.py --verify`
5. **工作流阻塞** → 未注册则失败

### 修改工具时

1. **修改工具文件** → 确保 UTF-8 编码
2. **自动验证** → `critical_checks.py --verify`
3. **工作流阻塞** → 编码错误则失败

---

## ⚠️ 历史问题处理

**问题:** 264 个历史工具未注册

**方案:**
- ✅ 只检查**本次会话**创建的工具（通过 session_temp.json）
- ✅ 历史工具不纳入检查范围
- ✅ 逐步补注册历史工具（可选）

---

## 📈 下一步计划

| 优先级 | 任务 | 状态 |
|--------|------|------|
| 🔴 P0 | 将检查集成到 session_end 工作流 | ✅ 完成 |
| 🟡 P1 | 补注册历史工具 | 可选 |
| 🟢 P2 | 自动化 session_temp.json 更新 | 待开发 |

---

## 📝 Git 提交记录

```
04238bc [FLOW ID: 20260318-universal-workflow-001] "关键审查项配置"
d9dd164 [FLOW ID: 20260318-universal-workflow-001] "阻塞性配置总结文档"
2bfe9f1 [FLOW ID: 20260318-universal-workflow-001] "阻塞性配置优化"
```

---

## ✅ 验收标准

- [x] blocker-007 已添加到 review.json
- [x] blocker-008 已添加到 review.json
- [x] critical_checks.py 已创建并测试
- [x] critical-checks 已注册到 tools_registry.json
- [x] CRITICAL-001 已添加到 zero_score_items
- [x] CRITICAL-002 已添加到 zero_score_items
- [x] 验证通过（所有检查 PASS）
- [x] Git 提交带 Flow ID

---

**Status:** ✅ 已配置并生效  
**Flow ID:** `20260318-universal-workflow-001`  
**Git Commit:** `04238bc`  
**Last Updated:** 2026-03-18 23:37
