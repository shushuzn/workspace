# 记忆工具精简计划

**分析日期:** 2026-03-18  
**状态:** 待执行  
**目标:** 精简 10-15 个文件  

---

## 📊 当前状态

**记忆工具总数:** 58 个 Python 文件

**问题:**
- 多版本共存 (v1, v2, v3)
- 功能重复 (fix 工具 5 个，util 工具 3 个)
- 测试文件混杂

---

## 🎯 精简目标

| 类别 | 当前 | 目标 | 精简 |
|------|------|------|------|
| **多版本文件** | 12 个 | 5 个 | -7 |
| **Fix 工具** | 5 个 | 2 个 | -3 |
| **Util 工具** | 3 个 | 1 个 | -2 |
| **测试文件** | 1 个 | 0 个 | -1 |
| **总计** | 58 个 | 45 个 | **-13** |

---

## 📋 执行计划

### P1: 删除旧版本 (7 个文件)

**原则:** 保留最新版本

| 保留 | 删除 | 原因 |
|------|------|------|
| `memory_dashboard_v2.py` | `memory_dashboard_v1.py` | v2 功能完整 |
| `memory_distiller_v2.py` | `memory_distiller_v1.py` | v1 仅 559 字节 (占位符) |
| `memory_forgetting.py` | `memory_forgetting_v1.py` | 保留无版本号的主版本 |
| `memory_quality_scorer.py` | `memory_quality_scorer_v1.py` | 保留主版本 |
| `ultimate_memory_search_v3.py` | `ultimate_memory_search.py` | v3 最新 |
| `ultimate_memory_search_v3.py` | `ultimate_memory_search_v2.py` | v3 最新 |

**执行:**
```bash
cd 30-scripts-tools
del memory_dashboard_v1.py
del memory_distiller_v1.py
del memory_forgetting_v1.py
del memory_quality_scorer_v1.py
del ultimate_memory_search.py
del ultimate_memory_search_v2.py
```

---

### P2: 合并 Fix 工具 (5→2)

**当前:**
- `fix_memory_complete.py`
- `fix_memory_encoding.py`
- `fix_memory_encoding_deep.py`
- `memory_fix_auto.py`
- `memory_fix_ultimate.py`

**合并方案:**

**保留:**
1. `memory_fix_tools.py` (新建，整合所有修复功能)
2. `fix_memory_encoding.py` (编码修复专用)

**删除:**
- `fix_memory_complete.py` (功能重复)
- `fix_memory_encoding_deep.py` (合并到 encoding)
- `memory_fix_auto.py` (合并到 fix_tools)
- `memory_fix_ultimate.py` (合并到 fix_tools)

**执行:**
```bash
# 创建整合工具
# memory_fix_tools.py - 包含 auto, complete, ultimate 功能

# 删除旧文件
del fix_memory_complete.py
del fix_memory_encoding_deep.py
del memory_fix_auto.py
del memory_fix_ultimate.py
```

---

### P3: 合并 Util 工具 (3→1)

**当前:**
- `memory_util_audit.py`
- `memory_util_health.py`
- `memory_util_indexer.py`

**合并方案:**

**保留:**
- `memory_utils.py` (新建，整合所有工具函数)

**删除:**
- `memory_util_audit.py`
- `memory_util_health.py`
- `memory_util_indexer.py`

**执行:**
```bash
# 创建整合工具
# memory_utils.py - 包含 audit, health, indexer 功能

# 删除旧文件
del memory_util_audit.py
del memory_util_health.py
del memory_util_indexer.py
```

---

### P4: 清理测试文件 (1 个)

**当前:**
- `test_memory_distillation_v2.py`

**处理:**
- 如果测试仍需要 → 移动到 `92-tests/`
- 如果不需要 → 删除

**建议:** 移动到 `92-tests/`

**执行:**
```bash
move test_memory_distillation_v2.py 92-tests\
```

---

## 📊 精简统计

### 删除文件清单 (13 个)

**多版本旧文件 (6 个):**
1. `memory_dashboard_v1.py`
2. `memory_distiller_v1.py`
3. `memory_forgetting_v1.py`
4. `memory_quality_scorer_v1.py`
5. `ultimate_memory_search.py`
6. `ultimate_memory_search_v2.py`

**Fix 工具重复 (4 个):**
7. `fix_memory_complete.py`
8. `fix_memory_encoding_deep.py`
9. `memory_fix_auto.py`
10. `memory_fix_ultimate.py`

**Util 工具重复 (3 个):**
11. `memory_util_audit.py`
12. `memory_util_health.py`
13. `memory_util_indexer.py`

**测试文件 (移动，不删除):**
- `test_memory_distillation_v2.py` → `92-tests/`

---

### 新增文件清单 (2 个)

1. `memory_fix_tools.py` - 整合 fix 功能
2. `memory_utils.py` - 整合 util 功能

**净减少:** 13 - 2 = **11 个文件**

---

## ⚠️ 风险评估

### 低风险 (可安全删除)

- `memory_distiller_v1.py` (559 字节，占位符)
- `memory_dashboard_v1.py` (v2 功能完整)
- 测试文件 (已测试过)

### 中风险 (需检查引用)

- `ultimate_memory_search.py` (检查 CLI 引用)
- `memory_forgetting_v1.py` (检查外部调用)

### 高风险 (需谨慎)

- Fix 工具合并 (需测试功能完整性)
- Util 工具合并 (需更新导入语句)

---

## 🔧 执行步骤

### 阶段 1: 备份

```bash
# 创建备份目录
mkdir 99-backups\memory-tools-cleanup

# 备份待删除文件
xcopy *v1.py 99-backups\memory-tools-cleanup\
xcopy *util*.py 99-backups\memory-tools-cleanup\
xcopy *fix*.py 99-backups\memory-tools-cleanup\
```

### 阶段 2: 检查引用

```bash
# 搜索代码引用
findstr /s /i "ultimate_memory_search.py" *.py
findstr /s /i "memory_forgetting_v1.py" *.py
```

### 阶段 3: 执行删除

```bash
# 删除旧版本
del memory_dashboard_v1.py
del memory_distiller_v1.py
del memory_forgetting_v1.py
del memory_quality_scorer_v1.py
del ultimate_memory_search.py
del ultimate_memory_search_v2.py

# 删除重复 fix 工具
del fix_memory_complete.py
del fix_memory_encoding_deep.py
del memory_fix_auto.py
del memory_fix_ultimate.py

# 删除重复 util 工具
del memory_util_audit.py
del memory_util_health.py
del memory_util_indexer.py

# 移动测试文件
move test_memory_distillation_v2.py 92-tests\
```

### 阶段 4: 创建整合工具

- 创建 `memory_fix_tools.py`
- 创建 `memory_utils.py`

### 阶段 5: 测试验证

```bash
# 测试 CLI 命令
py unified_cli_v3.py "memory search test"
py unified_cli_v3.py "memory quality"

# 测试关键功能
py memory_dashboard_v2.py
py ultimate_memory_search_v3.py --demo
```

### 阶段 6: Git 提交

```bash
git add -A
git commit -m "精简：记忆工具 58→45 文件 (-13)"
git push origin master
```

---

## ✅ 验收标准

| 标准 | 状态 | 验证方法 |
|------|------|----------|
| 文件数 58→45 | ⏳ | `dir *memory*.py /b` |
| CLI 命令正常 | ⏳ | 测试 memory 命令 |
| 无引用错误 | ⏳ | 运行关键工具 |
| Git 提交成功 | ⏳ | `git log` 检查 |

---

## 📝 决策记录

**决策 1:** 保留最新版本

**理由:** v2/v3 包含所有 v1 功能，且更稳定

---

**决策 2:** 合并 Fix 工具

**理由:** 5 个 fix 工具功能重叠，整合后更易维护

---

**决策 3:** 合并 Util 工具

**理由:** 3 个 util 工具都是辅助函数，适合单文件

---

**决策 4:** 移动测试文件

**理由:** 测试文件不应与工具混放

---

*计划创建时间：2026-03-18 09:35*
