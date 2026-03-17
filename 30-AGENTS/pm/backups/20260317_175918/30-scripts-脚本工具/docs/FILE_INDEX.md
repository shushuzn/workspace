# 文件索引

**创建:** 2026-03-07 02:11  
**更新:** 每次整理后

## 快速查找

### 按类型

| 前缀 | 类型 | 位置 |
|------|------|------|
| `MAT_PAP_*` | 论文 | 11-research/paper/ |
| `MAT_DOC_*` | 文档 | 11-research/docs/ |
| `MAT_ANA_*` | 分析 | 11-research/docs/ |
| `MAT_PLAN_*` | 计划 | 11-research/docs/ |
| `MAT_SOP_*` | 标准操作 | 11-research/docs/ |
| `MAT_REP_*` | 报告 | 11-research/docs/ |
| `MAT_RES_*` | 结果 | 11-research/docs/ |
| `NOTE_*` | 笔记 | 13-memory/ |
| `CS_NOTE_*` | CS/AI 笔记 | 10-ai-research/ |
| `SCRIPT_*` | 脚本 | 30-scripts/ |
| `TMPL_*` | 模板 | 05-templates/ |
| `DOC_*` | 通用文档 | 15-docs/ 30-scripts/ |
| `REP_*` | 报告 | 21-reports/ |

### 按项目

| 项目 | 前缀 | 数量 |
|------|------|------|
| LIG 导电率 | `MAT_*_LIGConductivity_*` | ~50 |
| CNT 碳纳米管 | `MAT_*_CNTConductivity_*` | ~20 |
| LIG 理论 | `MAT_*_LIGTheory_*` | ~15 |
| CS/AI | `CS_NOTE_*` | ~10 |

### 按日期

| 日期 | 文件 |
|------|------|
| 2026-03-06 | 论文投稿文件 |
| 2026-03-07 | 命名标准整理 |

## 完整索引

- CSV: `FILE_INDEX_2026-03-07.csv`
- 搜索: `Select-String -Path *.md -Pattern "关键词"`

## 常用命令

```powershell
# 搜索文件
Get-ChildItem -Recurse -Filter "*LIG*.md"

# 搜索内容
Select-String -Path *.md -Pattern "关键词" -Recurse

# 按类型查找
Get-ChildItem -Filter "MAT_PAP_*.md"
Get-ChildItem -Filter "NOTE_*.md"
Get-ChildItem -Filter "SCRIPT_*.ps1"
```
