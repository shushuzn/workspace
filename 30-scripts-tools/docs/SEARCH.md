# 快速搜索指南

## 按类型搜索

```powershell
# 论文
Get-ChildItem -Recurse -Filter "MAT_PAP_*.md"

# 笔记
Get-ChildItem -Recurse -Filter "NOTE_*.md"

# 脚本
Get-ChildItem -Recurse -Filter "SCRIPT_*.ps1"

# 模板
Get-ChildItem -Recurse -Filter "TMPL_*.md"

# 文档
Get-ChildItem -Recurse -Filter "MAT_DOC_*.md"
```

## 按项目搜索

```powershell
# LIG 导电率
Get-ChildItem -Recurse -Filter "*LIG*.md"

# CNT 碳纳米管
Get-ChildItem -Recurse -Filter "*CNT*.md"

# CS/AI
Get-ChildItem -Recurse -Filter "CS_*.md"
```

## 按内容搜索

```powershell
# 搜索关键词
Select-String -Path *.md -Pattern "关键词" -Recurse

# 搜索日期
Select-String -Path *.md -Pattern "2026-03-06" -Recurse
```

## 常用文件

| 文件 | 路径 |
|------|------|
| 论文草稿 | `11-research/paper/MAT_PAP_*` |
| 每日笔记 | `13-memory/NOTE_Daily_*` |
| 脚本 | `30-scripts/SCRIPT_*.ps1` |
| 模板 | `05-templates/TMPL_*.md` |
| 报告 | `21-reports/REP_*.md` |

## CSV 索引

打开 `FILE_INDEX_2026-03-07.csv` 用 Excel 筛选查找
