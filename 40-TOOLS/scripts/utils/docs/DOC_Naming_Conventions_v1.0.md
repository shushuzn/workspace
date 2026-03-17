# 文件命名规范

**创建日期:** 2026-03-07 00:12  
**来源:** 用户教导 — 参照 C/P/M 模式设计，但不用 C/P/M 字母  
**状态:** ✅ 强制执行

---

## 🎯 核心原则

> **参照 C/P/M 的命名思想（类型前缀 + 描述），但使用更有意义的前缀**

**核心思想:**
- **类型前缀 + 描述** - 让人一看就知道文件类型/用途
- **有规律的分类** - 统一的命名模式
- **辨识度优先** - 通过前缀快速识别
- **不用 C/P/M** - 使用更清晰的前缀

---

## 📋 命名层次

### 第 1 层：核心文件 (全大写，无连字符)

**用途:** 系统核心配置文件

```
README.md
SOUL.md
AGENTS.md
USER.md
TOOLS.md
IDENTITY.md
HEARTBEAT.md
```

**规则:**
- 全部大写
- 无连字符
- 简短清晰

---

### 第 2 层：笔记/模板文件 (描述性前缀)

**用途:** 不同类型的笔记和模板

**前缀分类 (不用 C/P/M):**
```
paper-*.md         # 论文笔记 (替代 P-Note)
concept-*.md       # 概念笔记 (替代 C-Note)
meeting-*.md       # 会议笔记 (替代 M-Note)
daily-*.md         # 每日笔记
learning-*.md      # 学习笔记
template-*.md      # 模板文件
```

**模板文件示例:**
```
paper-template.md
concept-template.md
meeting-template.md
daily-template.md
learning-template.md
template-index.md
```

**规则:**
- 使用完整单词作前缀
- 全部小写
- 连字符分隔

---

### 第 3 层：脚本文件 (功能前缀 + 全小写)

**用途:** PowerShell 和 Python 脚本

**功能前缀:**
```
check-*.ps1      # 检查类脚本
analyze-*.ps1    # 分析类脚本
auto-*.ps1       # 自动化类脚本
run-*.ps1        # 执行类脚本
setup-*.ps1      # 设置类脚本
cleanup-*.ps1    # 清理类脚本
test-*.ps1       # 测试类脚本
```

**示例:**
```
check-broken-links.ps1
analyze-link-heat.ps1
auto-backlink-generator.ps1
run-all-audit.ps1
setup-audit-tasks.ps1
```

**规则:**
- 功能前缀 + 连字符 + 描述
- 全部小写
- 描述清晰

---

### 第 4 层：报告文件 (内容 + 类型 + 日期)

**用途:** 各类报告和审计结果

**格式:**
```
<内容>-report-<日期>.md
<内容>-analysis-<日期>.md
<内容>-summary-<日期>.md
```

**示例:**
```
broken-links-report.md
link-heat-report.md
audit-report-2026-03-06.md
daily-summary-2026-03-06.md
weekly-report-2026-W10.md
```

**规则:**
- 内容 + 类型 + 日期
- 全部小写
- 日期格式 YYYY-MM-DD

---

### 第 5 层：研究文档 (主题 + 子主题)

**用途:** 研究项目相关文档

**格式:**
```
<主题>-<子主题>.md
```

**示例:**
```
paper-draft-v2.md
journal-selection.md
cover-letter-filled.md
submission-checklist.md
```

**规则:**
- 主题 + 连字符 + 子主题
- 全部小写
- 描述清晰

---

### 第 6 层：系统文档 (功能/主题)

**用途:** 系统配置、部署、使用文档

**格式:**
```
<功能>.md
<主题>-<子主题>.md
```

**示例:**
```
SYSTEM-ARCHITECTURE.md    # 核心系统文档大写
deployment-guide.md       # 部署指南
usage-examples.md         # 使用示例
troubleshooting.md        # 故障排除
```

**规则:**
- 核心系统文档可大写
- 普通文档全小写
- 保持统一

---

## 📁 文件夹命名

### 数字前缀分类

**格式:** `<数字>-<描述>/`

```
00-clawhub/
01-obsidian/
03-config/
05-templates/
11-research/
13-memory/
15-docs/
21-reports/
30-scripts/
31-skills/
32-workflows/
40-arxiv/
41-medium/
90-archive/
```

**规则:**
- 数字前缀 (2 位)
- 连字符
- 描述全小写

---

## 📊 命名模式总结

| 层级 | 文件类型 | 命名模式 | 示例 |
|------|----------|----------|------|
| 1 | 核心文件 | 全大写 | `SOUL.md` |
| 2 | 笔记/模板 | 描述前缀 + 全小写 | `paper-template.md` |
| 3 | 脚本文件 | 功能前缀 + 全小写 | `check-broken-links.ps1` |
| 4 | 报告文件 | 内容 + 类型 + 日期 | `audit-report-2026-03-06.md` |
| 5 | 研究文档 | 主题 + 子主题 | `paper-draft-v2.md` |
| 6 | 系统文档 | 功能/主题 | `deployment-guide.md` |
| - | 文件夹 | 数字 + 描述 | `30-scripts/` |

---

## 🔄 设计原则

### 参照 C/P/M 模式但不使用 C/P/M

**C-Note、M-Note、P-Note 的命名启示:**
1. **类型前缀** - 让人一眼看出文件类型
2. **统一格式** - 同类文件命名一致
3. **易于扩展** - 新类型容易添加
4. **高辨识度** - 通过前缀快速识别

**但使用更清晰的前缀:**
```
# 不用 C/P/M，改用完整单词
paper-*         # 替代 P-Note (更清晰)
concept-*       # 替代 C-Note (更清晰)
meeting-*       # 替代 M-Note (更清晰)

# 脚本功能前缀
check-*         # 检查类
analyze-*       # 分析类
auto-*          # 自动化类
```

---

## ✅ 检查清单

### 提交前检查

```markdown
- [ ] 核心文件使用全大写
- [ ] 笔记/模板使用描述前缀 (不用 C/P/M)
- [ ] 脚本使用功能前缀 + 全小写
- [ ] 报告使用内容 + 类型 + 日期
- [ ] 文件夹使用数字前缀
- [ ] 日期格式 YYYY-MM-DD
- [ ] 使用连字符 (非下划线/空格)
```

---

## 📝 更新记录

| 日期 | 变更 | 来源 |
|------|------|------|
| 2026-03-07 00:12 | 不用 C/P/M 字母，改用描述前缀 | 用户教导 |
| 2026-03-07 00:08 | 参照 C/M/P 模式设计 | 用户教导 |
| 2026-03-06 23:51 | 初始版本 (全小写) | 用户教导 |

---

*文件命名规范由 Claw 制定并遵守*  
*版本:* v3.0  
*最后更新:* 2026-03-07 00:12
