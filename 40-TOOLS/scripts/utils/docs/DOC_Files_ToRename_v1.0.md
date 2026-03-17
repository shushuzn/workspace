# 需要重命名的文件清单

**创建日期:** 2026-03-06 23:52  
**来源:** 命名规范审查  
**状态:** ⏳ 待用户确认

---

## ✅ 已完成重命名

### 第 1 批：模板文件 (8 个) ✅

| 原名称 | 新名称 | 完成时间 |
|--------|--------|----------|
| `C-Note Template.md` | `c-note-template.md` | 23:56 |
| `Daily Note Template.md` | `daily-note-template.md` | 23:56 |
| `Learning Note Template.md` | `learning-note-template.md` | 23:56 |
| `M-Note Template.md` | `m-note-template.md` | 23:56 |
| `P-Note Template.md` | `p-note-template.md` | 23:56 |
| `P-Note-Template-v2.md` | `p-note-template-v2.md` | 23:56 |
| `Research Question Template.md` | `research-question-template.md` | 23:56 |
| `TEMPLATE INDEX.md` | `template-index.md` | 23:56 |

**提交:** fdf5c85

---

### 第 2 批：研究文档 (4 个) ✅

| 原名称 | 新名称 | 完成时间 |
|--------|--------|----------|
| `PAPER_DRAFT_V2.md` | `paper-draft-v2.md` | 23:56 |
| `JOURNAL_SELECTION.md` | `journal-selection.md` | 23:56 |
| `COVER_LETTER_FILLED.md` | `cover-letter-filled.md` | 23:56 |
| `SUBMISSION_CHECKLIST.md` | `submission-checklist.md` | 23:56 |

**提交:** e21655e

---

### 第 3 批：系统文档 (5 个) ✅

| 原名称 | 新名称 | 完成时间 |
|--------|--------|----------|
| `SYSTEM-ARCHITECTURE.md` | `system-architecture.md` | 23:57 |
| `DEPLOYMENT-GUIDE.md` | `deployment-guide.md` | 23:57 |
| `USAGE-EXAMPLES.md` | `usage-examples.md` | 23:57 |
| `TROUBLESHOOTING.md` | `troubleshooting.md` | 23:57 |
| `PERFORMANCE-OPTIMIZATION.md` | `performance-optimization.md` | 23:57 |

**提交:** 进行中

---

## ✅ 保持原样的文件

**核心文件 (标准约定):**
- `README.md` - 标准约定
- `SOUL.md` - 标准约定
- `AGENTS.md` - 标准约定
- `USER.md` - 标准约定
- `TOOLS.md` - 标准约定
- `IDENTITY.md` - 标准约定
- `HEARTBEAT.md` - 标准约定

**原因:** 这些是标准核心文件名，保持大写是常见约定。

---

## 🔄 重命名流程

```powershell
# 1. 创建备份
git add -A
git commit -m "Backup before renaming"
git push

# 2. 批量重命名模板文件
cd 05-templates
Rename-Item "C-Note Template.md" "c-note-template.md"
Rename-Item "Daily Note Template.md" "daily-note-template.md"
# ...

# 3. 更新引用
(Get-Content *.md -Raw) -replace 'C-Note Template', 'c-note-template' | Set-Content *.md

# 4. 提交
git add -A
git commit -m "Rename: template files to lowercase"
git push
```

---

## ⚠️ 注意事项

1. **更新引用** - 重命名后需更新所有引用这些文件的文档
2. **检查链接** - 检查 `[[link]]` 格式的内部链接
3. **备份** - 重命名前先提交备份
4. **分批** - 不要一次性重命名所有文件，分批进行

---

## 📊 优先级

### P0 - 立即处理
- [ ] 模板文件 (8 个)

### P1 - 本周处理
- [ ] 研究文档 (4 个)
- [ ] 系统文档 (5 个)

### P2 - 本月处理
- [ ] 其他文档

---

*清单由 Claw 生成*  
*等待用户确认*
