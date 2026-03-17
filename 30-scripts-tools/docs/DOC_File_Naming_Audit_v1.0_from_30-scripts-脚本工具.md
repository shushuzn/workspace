# 文件命名审查报告

**审查日期:** 2026-03-07 00:20  
**审查范围:** 全工作区 2190 个 Markdown 文件  
**状态:** ⏳ 进行中

---

## ✅ 符合规范的文件

### 根目录 (9 个文件)
```
✅ AGENTS.md           - 核心文件，全大写
✅ HEARTBEAT.md        - 核心文件，全大写
✅ IDENTITY.md         - 核心文件，全大写
✅ README.md           - 核心文件，全大写
✅ SOUL.md             - 核心文件，全大写
✅ TOOLS.md            - 核心文件，全大写
✅ USER.md             - 核心文件，全大写
⚠️  figures.md          - 应移至 11-research/figures/
```

### 模板文件 (9 个文件)
```
✅ C-Note-Template.md              - 描述前缀，首字母大写
✅ Daily-Note-Template.md          - 描述前缀，首字母大写
✅ Learning-Note-Template.md       - 描述前缀，首字母大写
✅ M-Note-Template.md              - 描述前缀，首字母大写
✅ P-Note-Template.md              - 描述前缀，首字母大写
✅ P-Note-Template-v2.md           - 描述前缀，首字母大写
✅ Research-Question-Template.md   - 描述前缀，首字母大写
✅ Template-Index.md               - 描述前缀，首字母大写
⚠️  distilled-viewpoint-template.md - 应改为 Distilled-Viewpoint-Template.md
```

---

## ⚠️ 需要整理的文件

### P0 - 立即处理

| 文件 | 问题 | 应改为 | 优先级 |
|------|------|--------|--------|
| `figures.md` (根目录) | 不应在根目录 | 移至 `11-research/figures/README.md` | 🔴 高 |
| `distilled-viewpoint-template.md` | 全小写 | `Distilled-Viewpoint-Template.md` | 🔴 高 |

### P1 - 本周处理

需要检查以下文件夹的命名：
- [ ] `11-research/docs/` - 研究文档
- [ ] `15-docs/` - 系统文档
- [ ] `21-reports/` - 报告文件
- [ ] `30-scripts/` - 脚本文件

---

## 📊 命名规范快速参考

### 6 层命名结构

| 层级 | 类型 | 规则 | 示例 |
|------|------|------|------|
| 1 | 核心文件 | 全大写 | `SOUL.md` |
| 2 | 笔记/模板 | 描述前缀 + 首字母大写 | `Daily-Note-Template.md` |
| 3 | 脚本文件 | 功能前缀 + 全小写 | `check-broken-links.ps1` |
| 4 | 报告文件 | 内容 + 类型 + 日期 | `audit-report-2026-03-06.md` |
| 5 | 研究文档 | 主题 + 子主题 | `paper-draft-v2.md` |
| 6 | 系统文档 | 功能/主题 | `deployment-guide.md` |

---

## 🔄 整理流程

```powershell
# 1. 备份当前状态
git add -A
git commit -m "Backup before file naming cleanup"
git push

# 2. 根目录整理
Move-Item "figures.md" "11-research/figures/README.md"

# 3. 模板文件重命名
Rename-Item "distilled-viewpoint-template.md" "Distilled-Viewpoint-Template.md"

# 4. 提交
git add -A
git commit -m "Organize: fix file naming issues"
git push
```

---

## ✅ 检查清单

### 提交前检查
- [ ] 根目录只有 7 个核心文件
- [ ] 模板文件使用描述前缀
- [ ] 脚本文件使用功能前缀 + 全小写
- [ ] 报告文件使用内容 + 类型 + 日期
- [ ] 文件夹使用数字前缀

---

*审查由 Claw 生成*  
*版本:* v1.0  
*最后更新:* 2026-03-07 00:20
