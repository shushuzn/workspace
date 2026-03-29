# Agent 安装配置索引

**最后更新:** 2026-03-27

---

## 📦 已安装 (20个 Agent)

位置: `D:\OpenClaw\workspace\30-AGENTS\installed\`

| # | 文件 | 用途 |
|---|------|------|
| 01 | `01-lens-pr-reviewer.md` | PR 审查 |
| 02 | `02-scribe-docs-writer.md` | 文档生成 |
| 03 | `03-trace-bug-hunter.md` | Bug 追踪 |
| 04 | `04-test-writer-qa.md` | 测试生成 |
| 05 | `05-dep-scanner.md` | 依赖扫描 |
| 06 | `06-incident-responder.md` | 事件响应 |
| 07 | `07-cost-optimizer.md` | 成本优化 |
| 08 | `08-inbox-zero.md` | 邮件管理 |
| 09 | `09-meeting-notes.md` | 会议纪要 |
| 10 | `10-orion-project-manager.md` | 项目管理 |
| 11 | `11-morning-briefing.md` | 每日早报 |
| 12 | `12-overnight-coder.md` | 夜间编码 |
| 13 | `13-personal-crm.md` | 人脉管理 |
| 14 | `14-churn-predictor.md` | 流失预警 |
| 15 | `15-echo-content.md` | 内容复用 |
| 16 | `16-email-digest.md` | 周报生成 |
| 17 | `17-seo-writer.md` | SEO 优化 |
| 18 | `18-news-curator.md` | 资讯抓取 |
| 19 | `19-vuln-scanner.md` | 漏洞扫描 |
| 20 | `20-gdpr-auditor.md` | 合规审计 |

---

## 📋 配置文档

| 文件 | 用途 |
|------|------|
| `README.md` | 安装索引清单 |
| `CONFIG.md` | 完整配置指南 |
| `QUICKREF.md` | 速查卡 |
| `CRON-TASKS.json` | 定时任务配置 |
| `AGENT-CONFIG.md` | Agent 行为配置 |
| `ACTIVATE.md` | 激活指南 |
| `ENV-SUMMARY.md` | API Key 状态 |

---

## 🔄 工作流集成

| 文件 | 用途 |
|------|------|
| `32-workflows/AGENT-WORKFLOWS.md` | Agent 工作流模板 |

---

## 🚀 快速开始

```bash
# 查看所有 Agent
ls 30-AGENTS/installed/

# 触发 PR 审查
# 告诉 Feishu: "帮我审查这个 PR <url>"

# 获取资讯
# 告诉 Feishu: "给我今天行业新闻"

# 设置定时任务 (需 CoPaw 运行)
copaw cron import --file 30-AGENTS/installed/CRON-TASKS.json
```

---

## 📊 配置状态

| 项目 | 状态 |
|------|------|
| 20 个 Agent 安装 | ✅ 完成 |
| 优先级分类 | ✅ 完成 |
| 定时任务配置 | ✅ 完成 (待导入) |
| 工作流模板 | ✅ 完成 |
| 激活指南 | ✅ 完成 |
| API Key 状态 | ✅ 记录 |
