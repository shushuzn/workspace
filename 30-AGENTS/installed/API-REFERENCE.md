# 📡 API 参考

**创建日期:** 2026-03-27

---

## 内部 API

### CoPaw CLI

```bash
# Agent 管理
copaw agents list
copaw agents chat <agent-id> --message "..."

# Cron 管理
copaw cron list
copaw cron create --name "..." --schedule "..."
copaw cron delete <id>

# 聊天管理
copaw chats list
copaw chats history <session-id>
```

---

## 外部 API

### GitHub API

**认证:** `GH_TOKEN` 环境变量

```bash
# 列出 PR
gh pr list

# 创建 PR
gh pr create --title "..." --body "..."

# 审查 PR
gh pr view <pr-number>
```

**常用端点:**
- `GET /repos/{owner}/{repo}/pulls`
- `POST /repos/{owner}/{repo}/pulls/{pr_number}/reviews`

---

### Ruoli API

**用途:** AI 对话/生成

**端点:** 已配置在代码中

**参数:**
```json
{
  "model": "...",
  "messages": [...],
  "temperature": 0.7
}
```

---

### Render API

**用途:** 云部署

**认证:** `RENDER_API_KEY`

```bash
# 列出服务
curl -H "Authorization: Bearer $RENDER_API_KEY" \
  https://api.render.com/v1/services

# 触发部署
curl -X POST -H "Authorization: Bearer $RENDER_API_KEY" \
  https://api.render.com/v1/services/{id}/deploys
```

---

## Webhook

### Agent Webhook

**端点:** `/webhook/agent`

**方法:** POST

**参数:**
```json
{
  "event": "pr.created|pr.closed|issue.opened",
  "data": {
    "url": "...",
    "action": "...",
    "timestamp": "..."
  }
}
```

---

## 环境变量

```bash
# GitHub
GH_TOKEN=ghp_xxxxx
GH_TOKEN_2=ghp_xxxxx

# Ruoli
RUOLI_API_KEY=sk-xxxxx

# Render
RENDER_API_KEY=rnd_xxxxx

# Feishu (待配置)
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=xxxxx
FEISHU_USER_ID=xxxxx
```

---

## 速率限制

| API | 限制 | 窗口 |
|-----|------|------|
| GitHub | 5000 | 每小时 |
| Ruoli | 100 | 每分钟 |
| Render | 100 | 每分钟 |
| OpenAI | 取决于计划 | — |

---

## 错误码

| 错误码 | 说明 | 处理 |
|--------|------|------|
| 401 | 认证失败 | 检查 API Key |
| 403 | 权限不足 | 检查权限 |
| 404 | 资源不存在 | 确认资源 ID |
| 429 | 限流 | 等待后重试 |
| 500 | 服务器错误 | 重试 |
| 503 | 服务不可用 | 等待恢复 |

---

## 快捷命令

| 命令 | 用途 |
|------|------|
| `查看 token` | 显示 API Key 状态 |
| `测试 GitHub` | 测试 GitHub 连接 |
| `API 文档` | 显示此文档 |
