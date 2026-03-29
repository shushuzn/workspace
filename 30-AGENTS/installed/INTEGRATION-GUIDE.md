# 🔗 集成指南

**创建日期:** 2026-03-27

---

## 已集成服务

### GitHub ✅
- **Token:** GH_TOKEN, GH_TOKEN_2 已配置
- **能力:** PR 操作、Issue 管理、代码推送
- **Agent:** PR Reviewer, Dep Scanner

### Ruoli API ✅
- **Token:** RUOLI_API_KEY 已配置
- **能力:** AI 对话/生成

### Render ✅
- **Token:** RENDER_API_KEY 已配置
- **能力:** 云部署

### Feishu ⚠️
- **状态:** 需配置 APP_ID/SECRET
- **能力:** 消息推送、通知

### Email (Himalaya) ⚠️
- **状态:** 需配置 IMAP/SMTP
- **能力:** 邮件收发
- **Agent:** Inbox Zero, Morning Briefing

---

## 待集成服务

| 服务 | 用途 | 配置难度 |
|------|------|----------|
| Telegram | 通知 | 简单 |
| Discord | 通知 | 简单 |
| Slack | 通知 | 简单 |
| Notion | 笔记同步 | 中等 |
| Linear | 项目管理 | 中等 |
| Jira | 缺陷追踪 | 中等 |
| PagerDuty | 告警 | 中等 |

---

## 快速集成模板

### Telegram Bot

1. @BotFather 创建机器人
2. 获取 BOT_TOKEN
3. 配置:

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "bot_token": "your-token",
      "dm_policy": "open"
    }
  }
}
```

### Discord Webhook

1. 服务器设置 → Webhooks → 创建
2. 复制 Webhook URL
3. 配置:

```json
{
  "channels": {
    "discord": {
      "enabled": true,
      "webhook_url": "https://discord.com/api/webhooks/..."
    }
  }
}
```

---

## 工作流集成

### GitHub Actions

```yaml
# .github/workflows/agent-notify.yml
name: Agent Notification
on:
  pull_request:
    types: [opened, closed]
  issues:
    types: [opened, labeled]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Agent
        run: |
          curl -X POST ${{ secrets.AGENT_WEBHOOK }} \
            -d '{"event": "${{ github.event_name }}", "url": "${{ github.event.pull_request.html_url }}"}'
```

### Cron 集成

```bash
# 系统 Cron 触发 Agent
0 8 * * * curl -X POST http://localhost:3000/webhook/morning-briefing
```

---

## API 端点

| 端点 | 方法 | 用途 |
|------|------|------|
| `/webhook/agent` | POST | 外部触发 Agent |
| `/api/tasks` | GET | 查询任务状态 |
| `/api/health` | GET | 健康检查 |

---

## 集成检查清单

- [x] GitHub 集成
- [x] Ruoli API 集成
- [x] Render API 集成
- [ ] Telegram Bot (可选)
- [ ] Discord Webhook (可选)
- [ ] Email 配置 (可选)
- [ ] Feishu 配置 (可选)

---

## 获取帮助

```bash
# 查看已集成的服务
"查看集成状态"

# 配置新服务
"配置 Telegram"
"配置飞书"

# 测试集成
"测试 GitHub"
"测试邮件"
```
