# 📂 输出目录配置

**创建日期:** 2026-03-27

---

## 输出目录结构

```
D:\OpenClaw\workspace\outputs\
├── pr-reviews/              # PR 审查报告
├── security-reports/        # 安全扫描报告
├── content/                 # 生成的内容
│   ├── drafts/            # 草稿
│   ├── published/         # 已发布
│   └── social/            # 社交媒体版本
├── news-digests/           # 资讯摘要
├── meeting-notes/          # 会议纪要
├── reports/                # 综合报告
├── data-analysis/         # 数据分析结果
└── backups/               # 自动备份
```

---

## 按 Agent 输出映射

| Agent | 输出目录 |
|-------|----------|
| PR Reviewer | `outputs/pr-reviews/` |
| Vuln Scanner | `outputs/security-reports/` |
| News Curator | `outputs/news-digests/` |
| Meeting Notes | `outputs/meeting-notes/` |
| SEO Writer | `outputs/content/` |
| Echo | `outputs/content/social/` |
| Morning Briefing | `outputs/reports/daily/` |
| Churn Predictor | `outputs/reports/analysis/` |

---

## 文件命名规范

```
{日期}_{Agent名称}_{项目标识}.{扩展名}
```

示例:
```
2026-03-27_pr-review_issue-123.md
2026-03-27_vuln-scan_repo-abc.md
2026-03-27_news_tech-daily.md
```

---

## 自动归档规则

| 类型 | 保留时间 | 归档位置 |
|------|----------|----------|
| 日报告 | 30 天 | `outputs/archive/daily/` |
| 周报告 | 90 天 | `outputs/archive/weekly/` |
| 安全报告 | 1 年 | `outputs/archive/security/` |
| 会议纪要 | 6 个月 | `outputs/archive/meetings/` |

---

## 快捷命令

| 命令 | 执行 |
|------|------|
| `列出输出` | 查看 outputs 目录 |
| `查看报告` | 打开最新报告目录 |
| `归档` | 执行归档脚本 |
