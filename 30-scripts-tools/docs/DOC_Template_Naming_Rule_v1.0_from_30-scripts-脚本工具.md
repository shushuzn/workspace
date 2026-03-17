# 模板文件命名规则

**创建日期:** 2026-03-07 00:01  
**来源:** 用户明确要求 — "最好是像 P，C，M 等笔记那样的前面要加大写字母"  
**状态:** ✅ 强制执行

---

## 🎯 核心原则

> **模板文件的笔记类型前缀 (P、C、M 等) 保留大写**

这样更有规律和辨识度！

---

## 📋 命名格式

### 标准格式

```
<类型前缀>-<描述>.md
```

**类型前缀 (大写):**
- `P` - Paper/论文笔记
- `C` - Concept/概念笔记
- `M` - Meeting/会议笔记
- `D` - Daily/每日笔记
- `L` - Learning/学习笔记
- `T` - Template/模板索引

---

## ✅ 正确示例

```
✅ P-Note-Template.md        # P 大写
✅ C-Note-Template.md        # C 大写
✅ M-Note-Template.md        # M 大写
✅ D-Note-Template.md        # D 大写
✅ L-Note-Template.md        # L 大写
✅ Template-Index.md         # T 大写

✅ daily-note-template.md    # 普通描述全小写
✅ learning-note-template.md # 普通描述全小写
```

---

## ❌ 错误示例

```
❌ p-note-template.md        # P 应该大写
❌ c-note-template.md        # C 应该大写
❌ m-note-template.md        # M 应该大写
❌ P-note-template.md        # 连字符后应该大写或全小写
❌ P_Note_Template.md        # 使用下划线
❌ P Note Template.md        # 使用空格
```

---

## 🔄 恢复模板文件命名

### 需要恢复的文件

| 原名称 | 新名称 | 完成时间 |
|--------|--------|----------|
| `c-note-template.md` | `C-Note-Template.md` | 00:01 |
| `daily-note-template.md` | `Daily-Note-Template.md` | 00:01 |
| `learning-note-template.md` | `Learning-Note-Template.md` | 00:01 |
| `m-note-template.md` | `M-Note-Template.md` | 00:01 |
| `p-note-template.md` | `P-Note-Template.md` | 00:01 |
| `p-note-template-v2.md` | `P-Note-Template-v2.md` | 00:02 |
| `research-question-template.md` | `Research-Question-Template.md` | 00:01 |
| `template-index.md` | `Template-Index.md` | 00:01 |

**提交:** 4a8c018

---

## 📊 命名层次

### 第 1 层：核心文件 (全大写)
```
README.md
SOUL.md
AGENTS.md
USER.md
TOOLS.md
IDENTITY.md
HEARTBEAT.md
```

### 第 2 层：模板文件 (首字母/前缀大写)
```
P-Note-Template.md
C-Note-Template.md
M-Note-Template.md
Daily-Note-Template.md
Template-Index.md
```

### 第 3 层：脚本文件 (全小写 + 连字符)
```
check-broken-links.ps1
auto-backlink-generator.ps1
run-all-audit.ps1
```

### 第 4 层：报告文件 (全小写 + 连字符)
```
broken-links-report.md
link-heat-report.md
daily-summary-2026-03-06.md
```

---

## 📝 更新记录

| 日期 | 变更 | 来源 |
|------|------|------|
| 2026-03-07 00:01 | 模板文件前缀大写原则确立 | 用户教导 |
| 2026-03-06 23:51 | 初始命名规范 (全小写) | 用户教导 |

---

*模板文件命名规则由 Claw 制定并遵守*  
*版本:* v1.0  
*最后更新:* 2026-03-07 00:01
