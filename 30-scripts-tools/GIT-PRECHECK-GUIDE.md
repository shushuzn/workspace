# Git Pre-Check 使用指南

**工具位置:** `30-scripts-tools/git-precheck.py`  
**创建日期:** 2026-03-18  
**版本:** v1.0  

---

## 📖 功能概述

在 `git commit` 前手动运行检查，提前发现问题，避免提交失败。

### 核心功能

| 检查项 | 说明 | 严重性 |
|--------|------|--------|
| **编码检查** | UTF-8 无 BOM | 🔴 错误 |
| **敏感信息** | .env, API 密钥，阿里云凭证 | 🔴 错误 |
| **报告文件** | `*-report-*.md` (全局阻止) | 🔴 错误 |
| **大文件** | >50MB | 🔴 错误 |
| **嵌套备份** | 备份目录深度>2 层 | 🔴 错误 |
| **重复文件** | `_from_` 模式 | 🔴 错误 |
| **中文文件名** | 研究目录外警告 | 🟡 警告 |

---

## 🚀 快速开始

### 基础用法

```bash
# 检查暂存区文件 (默认)
py 30-scripts-tools/git-precheck.py

# 检查所有工作区文件
py 30-scripts-tools/git-precheck.py --all

# 检查指定文件
py 30-scripts-tools/git-precheck.py --file path/to/file.py

# 快速检查 (仅关键项，跳过编码和大文件)
py 30-scripts-tools/git-precheck.py --quick
```

### 输出选项

```bash
# 详细输出
py 30-scripts-tools/git-precheck.py --verbose

# 保存报告到文件
py 30-scripts-tools/git-precheck.py --save my-check.json

# JSON 格式输出 (适合脚本集成)
py 30-scripts-tools/git-precheck.py --json

# 组合使用
py 30-scripts-tools/git-precheck.py --all --quick --json
```

---

## 📊 输出示例

### 检查通过

```
======================================================================
  Git Pre-Check 报告
======================================================================

检查时间：2026-03-18 09:36:02
检查文件：1 个

【总体状态】
  ✅ PASSED (通过:6, 失败:0, 警告:0, 跳过:0)

【✅ 检查通过】可以安全提交

  提交命令：git commit -m "你的提交消息"

======================================================================
```

### 检查失败

```
======================================================================
  Git Pre-Check 报告
======================================================================

检查时间：2026-03-18 09:35:51
检查文件：18346 个

【总体状态】
  ❌ FAILED (通过:68504, 失败:211, 警告:4669, 跳过:0)

【❌ 错误】必须修复后才能提交

  报告/敏感文件 (154 个):
    - 敏感文件：08-collectors\medium-文章\...\2026-03-05_...md
    - 自动生成报告 (全局): 10-data\报告输出\...\REP_...md
    ... 还有 149 个

  嵌套备份 (57 个):
    - 备份目录路径过深 (深度=6): 30-AGENTS\pm\backups\...
    ... 还有 52 个

  解决方案:
    1. 删除文件：git reset HEAD <file> && rm <file>
    2. 修复编码：用 VSCode 打开 → 另存为 UTF-8
    3. 或强制提交：git commit --no-verify (不推荐)

======================================================================
```

---

## 🎯 典型场景

### 场景 1: 提交前快速检查

```bash
# 添加文件后
git add .

# 运行检查
py 30-scripts-tools/git-precheck.py

# 如果通过，提交
git commit -m "修复：内存工具精简"

# 如果失败，根据提示修复
```

### 场景 2: 清理工作区

```bash
# 扫描整个工作区问题
py 30-scripts-tools/git-precheck.py --all --quick

# 查看报告，批量清理问题文件
```

### 场景 3: CI/CD 集成

```bash
# 在 CI 脚本中
py 30-scripts-tools/git-precheck.py --json --save pre-check-result.json

# 检查返回码
if [ $? -ne 0 ]; then
    echo "❌ Pre-check failed"
    exit 1
fi
```

### 场景 4: 单文件验证

```bash
# 创建新工具后检查
py 30-scripts-tools/new-tool.py

# 验证
py 30-scripts-tools/git-precheck.py --file 30-scripts-tools/new-tool.py
```

---

## 🔧 配置选项

### 敏感文件模式

在代码中修改 `SENSITIVE_PATTERNS`:

```python
SENSITIVE_PATTERNS = [
    '.env',
    'aliyun',
    'access_key',
    'secret',
    '.tiff',
    # 添加自定义模式
    'my_secret_pattern',
]
```

### 报告文件模式

在代码中修改 `BLOCKED_PATTERNS`:

```python
BLOCKED_PATTERNS = [
    '-report-',
    'operations-report',
    # 添加自定义模式
    'auto-generated',
]
```

### 允许中文文件名的目录

在代码中修改 `ALLOW_CHINESE_PATH`:

```python
ALLOW_CHINESE_PATH = [
    '10-RESEARCH/',
    '06-research/',
    # 添加自定义目录
    'my-research/',
]
```

### 大文件阈值

在代码中修改 `check_large_file()` 函数:

```python
if size_mb > 50:  # 修改 50 为其他值
```

---

## ⚠️ 常见问题

### Q1: 为什么检查失败？

**A:** 查看【❌ 错误】部分，根据提示修复：

- **敏感文件**: 删除或移出不跟踪
- **报告文件**: 删除或重命名为 `-GUIDE-`
- **嵌套备份**: 清理备份目录
- **编码错误**: 用 VSCode 另存为 UTF-8

### Q2: 如何强制提交？

**A:** 使用 `--no-verify` (不推荐):

```bash
git commit --no-verify -m "紧急提交"
```

### Q3: 如何跳过某些检查？

**A:** 使用 `--quick` 跳过编码和大文件检查:

```bash
py git-precheck.py --quick
```

### Q4: 中文文件名总是警告怎么办？

**A:** 如果是研究文件，添加到 `ALLOW_CHINESE_PATH`:

```python
ALLOW_CHINESE_PATH.append('my-research/')
```

### Q5: 如何查看 JSON 报告？

**A:** 使用 `--json` 或 `--save`:

```bash
# 输出到控制台
py git-precheck.py --json

# 保存到文件
py git-precheck.py --save report.json
cat 20-data-reports/report.json
```

---

## 📈 最佳实践

### ✅ 推荐做法

1. **每次提交前运行**
   ```bash
   git add .
   py git-precheck.py
   git commit -m "..."
   ```

2. **使用 --quick 快速检查**
   ```bash
   py git-precheck.py --quick
   ```

3. **定期全工作区扫描**
   ```bash
   # 每周一次
   py git-precheck.py --all --quick --save weekly-scan.json
   ```

4. **集成到工作流**
   ```bash
   # 在 build.bat 或 deploy.bat 中
   py 30-scripts-tools/git-precheck.py --quick || exit 1
   ```

### ❌ 避免做法

1. **不要依赖 --no-verify**
   - 除非紧急情况
   - 可能导致问题积累

2. **不要忽略警告**
   - 警告可能变成错误
   - 中文文件名影响跨平台

3. **不要跳过检查**
   - 节省 1 分钟，浪费 1 小时修复

---

## 🔗 相关工具

### Git Hook

```bash
# 安装自动检查 Hook
py 30-scripts-tools/install-git-hooks.py

# Hook 会在 git commit 时自动运行相同检查
```

### 文件整理工具

```bash
# 清理重复文件
py 30-scripts-tools/clean-duplicates-safe.py

# 扫描大文件
py 30-scripts-tools/file-organizer.py --scan
```

### 备份策略

```bash
# 重构备份目录
py 30-scripts-tools/backup-strategy-restructure.py
```

---

## 📝 更新日志

### v1.0 (2026-03-18)

**功能:**
- ✅ 编码检查 (UTF-8, 无 BOM)
- ✅ 敏感信息扫描
- ✅ 报告文件阻止
- ✅ 大文件检测
- ✅ 嵌套备份检测
- ✅ 重复文件检测
- ✅ 中文文件名警告

**输出:**
- ✅ 详细报告
- ✅ JSON 格式
- ✅ 文件保存

**模式:**
- ✅ 暂存区检查 (默认)
- ✅ 全工作区检查 (--all)
- ✅ 单文件检查 (--file)
- ✅ 快速检查 (--quick)

---

## 🎯 验收标准

| 标准 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 编码检查 | 检测 BOM | ✅ | 通过 |
| 敏感文件 | 检测 .env | ✅ | 通过 |
| 报告文件 | 全局阻止 | ✅ | 通过 |
| 大文件检测 | >50MB | ✅ | 通过 |
| 嵌套备份 | >2 层 | ✅ | 通过 |
| 重复文件 | _from_ | ✅ | 通过 |
| 中文文件名 | 警告 | ✅ | 通过 |
| JSON 输出 | --json | ✅ | 通过 |
| 报告保存 | --save | ✅ | 通过 |
| 快速模式 | --quick | ✅ | 通过 |

**通过率:** 10/10 = 100% ✅

---

## 📞 支持

**问题反馈:** 直接运行 `py git-precheck.py --help` 查看帮助

**代码位置:** `30-scripts-tools/git-precheck.py`

**文档位置:** `30-scripts-tools/GIT-PRECHECK-GUIDE.md`

---

**🎉 Git Pre-Check 工具完成！**

*最后更新：2026-03-18*
