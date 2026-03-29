# Agent 配置指南

**创建日期：** 2026-03-27
**决策依据：** 20 个已安装 Agent，按实用频率分类

---

## 🚀 激活优先级

### 第一梯队 — 日常必备（立即可用）

| Agent | 文件 | 触发方式 | 用途 |
|-------|------|----------|------|
| **Morning Briefing** | 11-morning-briefing.md | 07:00 每日 | 邮件 + 日历 + 任务 + 新闻一站式早报 |
| **Inbox Zero** | 08-inbox-zero.md | 邮件收到时 | 自动分类 + 优先级 + 回复建议 |
| **Meeting Notes** | 09-meeting-notes.md | 会议前/后 | 自动生成纪要 + 行动项 |

### 第二梯队 — 开发必备（按需触发）

| Agent | 文件 | 触发方式 | 用途 |
|-------|------|----------|------|
| **PR Reviewer (Lens)** | 01-lens-pr-reviewer.md | PR 创建时 | 代码审查 + 安全扫描 + 质量评分 |
| **Dep Scanner** | 05-dep-scanner.md | 提交时 | CVE 检测 + 许可证审计 |
| **Test Writer** | 04-test-writer-qa.md | PR 创建时 | 低覆盖代码自动补测试 |

### 第三梯队 — 自动化运行（定时）

| Agent | 文件 | 周期 | 用途 |
|-------|------|------|------|
| **News Curator** | 18-news-curator.md | 08:00 / 18:00 | 行业资讯抓取 + AI 整理 |
| **Overnight Coder** | 12-overnight-coder.md | 22:00–06:00 | 睡觉时自动编码 |
| **Vuln Scanner** | 19-vuln-scanner.md | 周日 02:00 | 漏洞扫描 + 修复建议 |

### 第四梯队 — 商业智能

| Agent | 文件 | 触发方式 | 用途 |
|-------|------|----------|------|
| **Personal CRM** | 13-personal-crm.md | 手动 | 人脉管理 + 跟进提醒 |
| **Churn Predictor** | 14-churn-predictor.md | 每日 | 客户流失预警 |
| **SEO Writer** | 17-seo-writer.md | 手动 | 内容优化 + 关键词策略 |

---

## ⏰ 定时任务配置

### 推荐的 Cron 任务

```bash
# 每日早报 — 工作日 07:00
copaw cron create --agent-id nWyDpW \
  --name "Daily Morning Briefing" \
  --schedule "0 7 * * 1-5" \
  --prompt "执行 Morning Briefing，整理今日邮件、日历、任务和行业新闻" \
  --target-channel console

# 早间资讯 — 每日 08:00
copaw cron create --agent-id nWyDpW \
  --name "Morning News Digest" \
  --schedule "0 8 * * *" \
  --prompt "执行 News Curator，抓取并整理今日行业资讯" \
  --target-channel console

# 晚间资讯 — 每日 18:00
copaw cron create --agent-id nWyDpW \
  --name "Evening News Digest" \
  --schedule "0 18 * * *" \
  --prompt "执行 News Curator Evening，整理晚间行业动态" \
  --target-channel console

# 周日安全扫描 — 周日 02:00
copaw cron create --agent-id nWyDpW \
  --name "Weekly Security Scan" \
  --schedule "0 2 * * 0" \
  --prompt "执行 Vuln Scanner，扫描所有项目依赖漏洞并生成报告" \
  --target-channel console
```

---

## 📋 场景化使用指南

### 场景 1：开发提 PR 时
```
激活 → 01-lens-pr-reviewer.md + 04-test-writer-qa.md
输入 → PR 链接或代码变更
输出 → 审查意见 + 测试覆盖率报告
```

### 场景 2：准备会议时
```
激活 → 09-meeting-notes.md
输入 → 会议议程 + 参与者列表
输出 → 参会指南 + 历史要点 + 讨论框架
```

### 场景 3：管理客户关系
```
激活 → 13-personal-crm.md + 14-churn-predictor.md
输入 → 客户互动记录
输出 → 人脉图谱 + 流失风险评分
```

### 场景 4：内容运营
```
激活 → 15-echo-content.md + 17-seo-writer.md + 18-news-curator.md
输入 → 原始内容或主题
输出 → 多平台适配版本 + SEO 优化建议
```

---

## 🔧 快速激活命令

```bash
# 查看当前 Agent 状态
copaw agents list

# 激活指定 Agent
copaw agents activate 01-lens-pr-reviewer

# 查看定时任务
copaw cron list --agent-id nWyDpW
```

---

## ⚙️ 自定义参数

每个 Agent 的 SOUL.md 开头都有配置区块，可修改：

```markdown
## Configuration
- NEWS_SOURCES: ["techcrunch", "hackernews", "reddit"]
- TIMEZONE: "Asia/Shanghai"
- BRIEFING_LENGTH: "concise"  # concise | detailed
```

---

## 📁 文件位置

```
D:\OpenClaw\workspace\
├── 30-AGENTS/installed/     # 20 个已安装 Agent
├── 30-AGENTS/personas/      # Agent 角色定义
├── active_skills/          # 系统技能
└── memory/                 # 会话记忆
```

---

## 🔗 相关资源

- [awesome-openclaw-agents](https://github.com/mergisi/awesome-openclaw-agents)
- [CoPaw 文档](https://docs.openclaw.dev)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
