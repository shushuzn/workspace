# 21-reports 文件夹整理报告

**日期:** 2026-03-11 01:18  
**整理前:** 根目录 90 个文件  
**整理后:** 根目录 1 个文件 (README.md + .gitignore)

---

## 文件夹结构

```
21-reports/
├── README.md
├── lig-domain/          # LIG 领域数据 (15 个文件)
├── lig-authors/         # LIG 作者分析 (5 个文件)
├── lig-opportunities/   # LIG 机会分析 (9 个文件)
├── lig-risk/            # LIG 风险预警 (6 个文件)
├── lig-general/         # LIG 综合报告 (5 个文件)
├── skills/              # 技能相关
├── automation/          # 自动化任务
├── learning-resources/  # 学习资源
├── general-reports/     # 综合报告
└── misc/                # 其他
```

---

## 分类规则

| 关键词 | 目标文件夹 |
|--------|-----------|
| lig + domain/industry/citation | lig-domain/ |
| lig + author/network | lig-authors/ |
| lig + opportunity | lig-opportunities/ |
| lig + risk | lig-risk/ |
| lig (其他) | lig-general/ |
| skill | skills/ |
| auto/task/batch | automation/ |
| learning/resource | learning-resources/ |
| DOC_/REP_ 前缀 | general-reports/ |
| 其他 | misc/ |

---

**整理脚本:** `30-scripts/organize-reports-folder.py`
