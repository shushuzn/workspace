# 外部集成配置指南

## 📱 飞书 (Feishu) 通知

### 当前状态
✅ **已配置** - 在 `01-CONFIG/config.json` 中已启用

```json
"feishu": {
  "enabled": true,
  "app_id": "cli_a93a6936eff81bcd",
  "app_secret": "vWIWGFZPYBi6clKb1IV5JfDGnWrT1bra"
}
```

### 配置步骤（如需修改）

1. 登录[飞书开放平台](https://open.feishu.cn/app)
2. 创建企业自建应用或使用现有应用
3. 获取 `App ID` 和 `App Secret`
4. 更新 `.env` 文件：
   ```
   FEISHU_APP_ID=your_app_id
   FEISHU_APP_SECRET=your_app_secret
   FEISHU_USER_ID=your_user_id
   ```
5. 在飞书开放平台配置机器人能力

### 使用方式

使用 `channel_message` skill 发送通知：
1. 先查询 session: `copaw chats list`
2. 发送消息: `copaw channels send`

---

## 📧 邮件 (Himalaya)

### 当前状态
❌ **未安装**

### 安装步骤

**Windows (使用 Scoop):**
```bash
scoop install himalaya
```

**或者下载二进制：**
1. 访问 https://github.com/pimalaya/himalaya/releases
2. 下载 Windows 版本
3. 解压到 PATH 中的目录

### 配置步骤

1. 创建配置文件 `~/.config/himalaya/config.toml`：
```toml
[[accounts]]
name = "default"
email = "your@email.com"
provider = "gmail"

[accounts.default]
imap_host = "imap.gmail.com"
imap_port = 993
smtp_host = "smtp.gmail.com"
smtp_port = 465
```

2. 添加认证令牌或应用密码

### 使用方式

```bash
# 列出邮件
himalaya list

# 读取邮件
himalaya read <id>

# 发送邮件
himalaya write | himalaya send

# 搜索
himalaya search "keyword"
```

---

## 🔔 其他集成

### 钉钉 (DingTalk)
- 使用 `dingtalk_channel_connect` skill
- 支持可视浏览器自动配置

### Discord
- 在 `01-CONFIG/config.json` 中配置 `discord` 频道

### iMessage (macOS)
- 需要 macOS 和 AppleScript
- 在 `01-CONFIG/config.json` 中配置 `imessage` 频道

---

## 快捷命令

| 你说 | 操作 |
|------|------|
| `测试飞书` | 发送测试消息到飞书 |
| `查邮件` | 列出未读邮件 |
| `发邮件` | 撰写并发送邮件 |
