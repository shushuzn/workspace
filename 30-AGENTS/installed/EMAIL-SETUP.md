# 📧 邮件配置指南

**创建日期:** 2026-03-27

---

## 工具: Himalaya CLI

Himalaya 是一个终端邮件管理工具，支持 IMAP/SMTP。

### 安装

```bash
# macOS
brew install himalaya

# Windows (需要 WSL 或 Scoop)
scoop install himalaya

# Cargo
cargo install himalaya
```

---

## 配置文件位置

```
~/.config/himalaya/config.toml
```

---

## 常用邮箱配置示例

### Gmail

```toml
[accounts.gmail]
email = "your@gmail.com"
display-name = "Your Name"
default = true

# IMAP
backend.type = "imap"
backend.host = "imap.gmail.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "your@gmail.com"
backend.auth.type = "oauth2"
backend.auth.cmd = "gmail-oauth2-helper"

# SMTP
message.send.backend.type = "smtp"
message.send.backend.host = "smtp.gmail.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "your@gmail.com"
message.send.backend.auth.type = "oauth2"
```

### Outlook/Hotmail

```toml
[accounts.outlook]
email = "your@outlook.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "outlook.office365.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "your@outlook.com"
backend.auth.type = "password"
backend.auth.raw = "your-app-password"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp-mail.outlook.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "your@outlook.com"
message.send.backend.auth.type = "password"
```

### QQ 邮箱

```toml
[accounts.qq]
email = "your@qq.com"
display-name = "你的名字"
default = true

backend.type = "imap"
backend.host = "imap.qq.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "your@qq.com"
backend.auth.type = "password"
backend.auth.raw = "your-authorization-code"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.qq.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "your@qq.com"
message.send.backend.auth.type = "password"
```

> ⚠️ QQ 邮箱需要开启 IMAP/SMTP 并获取授权码

### 企业邮箱 (通用)

```toml
[accounts.work]
email = "your@company.com"
display-name = "Your Name"
default = true

backend.type = "imap"
backend.host = "imap.company.com"
backend.port = 993
backend.encryption.type = "tls"
backend.login = "your@company.com"
backend.auth.type = "password"
backend.auth.raw = "your-password"

message.send.backend.type = "smtp"
message.send.backend.host = "smtp.company.com"
message.send.backend.port = 587
message.send.backend.encryption.type = "start-tls"
message.send.backend.login = "your@company.com"
message.send.backend.auth.type = "password"
```

---

## 常用命令

```bash
# 列出邮件
himalaya list

# 阅读邮件
himalaya read <id>

# 搜索邮件
himalaya search "keyword"

# 发送邮件
himalaya write

# 回复邮件
himalaya reply <id>

# 删除邮件
himalaya move <id> Trash
```

---

## 集成 Inbox Zero Agent

配置好 Himalaya 后，Inbox Zero Agent 可以：

1. 自动分类邮件 (紧急/待处理/存档)
2. 生成回复建议
3. 定时清理收件箱
4. 会议邀请自动提取

---

## 状态

| 邮箱服务 | 配置状态 |
|----------|----------|
| Gmail | 待配置 |
| Outlook | 待配置 |
| QQ 邮箱 | 待配置 |
| 企业邮箱 | 待配置 |

如需配置，请告诉我：
1. 邮箱类型 (Gmail/Outlook/QQ/企业)
2. 邮箱地址
3. 是否已有授权码/应用密码
