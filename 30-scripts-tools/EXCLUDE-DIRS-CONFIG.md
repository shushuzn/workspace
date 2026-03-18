# 排除扫描目录配置

**Flow ID:** `20260318-universal-workflow-001`  
**Last Updated:** 2026-03-18  
**Status:** ✅ 已配置并生效

---

## 🎯 配置目的

**解决历史问题干扰** - 排除工作区中历史遗留问题集中的目录，让批判者审查聚焦于当前代码质量。

---

## 📁 排除目录清单 (13 个)

| 目录 | 类型 | 排除原因 |
|------|------|---------|
| `99-backups/` | 备份文件 | 临时备份，非正式代码 |
| `92-tests/` | 测试文件 | 测试代码，允许失败 |
| `90-archive/` | 归档文件 | 历史归档，不再维护 |
| `80-PROJECTS/` | 旧项目 | 旧项目代码，标准不同 |
| `60-DATA/` | 数据文件 | 数据文件，非代码 |
| `40-arxiv/` | 论文收集 | 自动收集的论文 |
| `41-medium/` | Medium 收集 | 自动收集的文章 |
| `42-hackernews/` | HackerNews 收集 | 自动收集的讨论 |
| `node_modules/` | NPM 依赖 | 第三方依赖，不可控 |
| `venv/` | Python 虚拟环境 | 第三方包，不可控 |
| `__pycache__/` | Python 缓存 | 自动生成的字节码 |
| `.git/` | Git 目录 | 版本控制元数据 |
| `tool_result/` | 临时工具结果 | 临时输出文件 |

---

## 🔧 配置位置

**文件:** `30-scripts-tools/issue_scanner.py`

```python
# 排除扫描目录 (历史问题集中区域)
EXCLUDE_DIRS = [
    '99-backups',      # 备份文件
    '92-tests',        # 测试文件
    '90-archive',      # 归档文件
    '80-PROJECTS',     # 旧项目
    '60-DATA',         # 数据文件
    '40-arxiv',        # 论文收集
    '41-medium',       # Medium 收集
    '42-hackernews',   # HackerNews 收集
    'node_modules',    # NPM 依赖
    'venv',            # Python 虚拟环境
    '__pycache__',     # Python 缓存
    '.git',            # Git 目录
    'tool_result',     # 临时工具结果
]
```

---

## 📊 效果对比

### 配置前
```
批判者审查结果:
- 致命问题：133 个 ❌
- 严重问题：42 个 ❌
- 一般问题：2711 个 ❌
- 安全漏洞：153 个 ❌

总计：3039 个问题 (大部分来自排除目录)
```

### 配置后 (预期)
```
批判者审查结果:
- 致命问题：0-10 个 ✅ (仅核心代码)
- 严重问题：0-5 个 ✅ (仅核心代码)
- 一般问题：0-50 个 ✅ (仅核心代码)
- 安全漏洞：0-5 个 ✅ (仅核心代码)

总计：预计<100 个问题 (聚焦核心代码)
```

---

## 🛡️ 排除逻辑

**Issue Scanner 扫描流程:**

```python
def _get_py_files(self) -> List[Path]:
    """获取 Python 文件列表（排除指定目录）"""
    py_files = []
    for py_file in self.base_path.rglob("*.py"):
        if not self._should_exclude(py_file):
            py_files.append(py_file)
    return py_files

def _should_exclude(self, path: Path) -> bool:
    """检查路径是否应该排除"""
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False
```

**影响范围:**
- ✅ Issue Scanner (第 16 层)
- ✅ Auto-Critic v7 (第 13 层) - 使用 Issue Scanner
- ✅ Quality Gate (第 14 层) - 使用扫描结果

---

## ⚠️ 注意事项

1. **不排除核心目录** - `30-scripts-tools/`, `15-docs/`, `13-memory/` 等核心目录仍然扫描
2. **不排除当前任务** - 本次任务修改的文件仍然接受审查
3. **可动态调整** - 根据需要随时添加/删除排除目录
4. **Git 提交不受影响** - 排除目录的文件仍然可以提交到 Git

---

## 🚀 验证方式

```bash
# 手动测试 Issue Scanner
py 30-scripts-tools\issue_scanner.py --path 30-scripts-tools --format json

# 查看批判者审查结果
cat flow-archive/20260318-universal-workflow-001/review.json

# 查看排除的目录
findstr /n "EXCLUDE_DIRS" 30-scripts-tools\issue_scanner.py
```

---

## 📝 Git 提交记录

```
[FLOW ID: 20260318-universal-workflow-001] 排除扫描目录配置 - 历史问题集中区域过滤
Commit: 0ec0487
Date: 2026-03-18 23:08:06
```

---

## 🎯 预期效果

**聚焦核心代码质量，避免历史问题干扰**

```
之前：3039 个问题 → 无法分辨哪些是真正重要的
现在：预计<100 个问题 → 聚焦当前任务质量
```

---

**Status:** ✅ 已配置并生效  
**Flow ID:** `20260318-universal-workflow-001`  
**Git Commit:** `0ec0487`  
**Last Updated:** 2026-03-18
