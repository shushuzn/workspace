# 环境配置说明

**创建日期:** 2026-03-27

---

## 🔑 已配置 API Keys

| 服务 | 用途 | 状态 |
|------|------|------|
| GitHub (GH_TOKEN) | 代码操作、PR、Issue | ✅ 已配置 |
| GitHub (GH_TOKEN_2) | 备用 Token | ✅ 已配置 |
| Ruoli API | AI 能力接口 | ✅ 已配置 |
| Render | 部署服务 | ✅ 已配置 |
| Feishu | 飞书通知 | ⚠️ 待配置 |
| File Organizer | 文件整理 | ⚠️ 待配置 |

---

## ⚙️ Feishu 通知配置

当前 `.env` 中飞书配置为空。如需启用：

```bash
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=xxxxx
FEISHU_USER_ID=your_user_id
```

配置后可通过 `channel_message` skill 推送通知。

---

## 🔧 其他配置

### GitHub Token 权限
- GH_TOKEN: 有 PAT 权限，可操作仓库
- GH_TOKEN_2: 备用

### Ruoli API
- 用于 AI 对话/生成能力
- Endpoint: 已配置在代码中

### Render
- 云部署服务
- API Key 已配置

---

## 📁 配置文件位置

```
.env                    # 环境变量 (不提交 Git)
agent.json              # Agent 配置
.openclaw/config.json   # OpenClaw 运行时配置
```
