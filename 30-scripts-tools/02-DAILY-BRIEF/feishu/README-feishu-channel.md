# 🐾 OpenClaw 飞书通道使用指南

**状态:** ✅ 已启用  
**App ID:** `cli_a93a6936eff81bcd`  
**最后会话:** `6d929252` (用户：`ou_72a847b95fc25870dcdd8ce56d929252`)

---

## 🚀 快速开始

### 1️⃣ 打开飞书
- **网页版:** https://www.feishu.cn
- **桌面客户端:** 已安装则直接打开

### 2️⃣ 找到 OpenClaw 机器人

**方法 A: 搜索应用**
1. 在飞书顶部搜索框输入 `OpenClaw`
2. 点击应用/机器人

**方法 B: 查看已安装应用**
1. 点击左侧边栏「应用」
2. 找到 `OpenClaw` 或 `Claw`

**方法 C: 使用机器人链接**
- 如果之前已添加，直接在聊天列表中找到

### 3️⃣ 开始聊天

在 OpenClaw 机器人对话框中：
- 直接发送消息（无需前缀）
- 支持文件、图片、链接
- 支持群聊（需配置群策略）

---

## 📋 配置详情

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_a93a6936eff81bcd",
      "appSecret": "vWIWGFZPYBi6clKb1IV5JfDGnWrT1bra",
      "botPrefix": "",
      "filterToolMessages": false,
      "filterThinking": false,
      "dmPolicy": "open",
      "groupPolicy": "open",
      "requireMention": false
    }
  }
}
```

### 配置说明

| 配置项 | 值 | 说明 |
|--------|-----|------|
| `enabled` | `true` | 飞书通道已启用 |
| `dmPolicy` | `open` | 私聊消息全部响应 |
| `groupPolicy` | `open` | 群聊消息全部响应 |
| `requireMention` | `false` | 群聊中无需 @机器人 |
| `filterToolMessages` | `false` | 显示工具调用消息 |
| `filterThinking` | `false` | 显示思考过程 |

---

## 💡 使用技巧

### 私聊模式
- 直接在 OpenClaw 机器人对话框发送消息
- 所有对话自动保存，支持会话连续性

### 群聊模式
- 在群中添加 OpenClaw 机器人
- 无需 @ 即可响应（`requireMention: false`）
- 适合团队协作场景

### 消息过滤
- 工具调用消息：✅ 显示
- 思考过程：✅ 显示
- 完整对话历史：✅ 保存在飞书

---

## 🔧 故障排查

### 问题 1: 找不到 OpenClaw 机器人

**解决:**
1. 确认飞书账号已授权 OpenClaw 应用
2. 联系管理员添加应用到企业
3. 检查飞书「应用管理」中是否已安装

### 问题 2: 机器人不响应

**检查清单:**
- [ ] 飞书通道已启用 (`enabled: true`)
- [ ] App ID 和 App Secret 正确
- [ ] 飞书 OAuth 授权有效
- [ ] 网络连接正常

### 问题 3: 会话不同步

**说明:**
- 飞书会话独立保存，不与 Console 共享
- 每次在飞书聊天都是连续会话
- 切换通道后需要重新建立上下文

---

## 📊 会话管理

### 查看会话历史
```bash
# 查看最近的飞书会话
dir /b /o-d "C:\Users\华为\.copaw\sessions\*feishu*"
```

### 会话文件命名
- 格式：`{user_id}_{session_id}.json`
- 示例：`ou_72a847b95fc25870dcdd8ce56d929252_6d929252.json`

---

## 🎯 下一步行动

1. **打开飞书** → https://www.feishu.cn
2. **登录账号** → 使用已授权的飞书账号
3. **找到 OpenClaw** → 搜索或从应用列表
4. **开始聊天** → 发送第一条消息
5. **验证响应** → 确认机器人正常响应

---

## 📝 与 Console 的区别

| 特性 | Console | 飞书通道 |
|------|---------|---------|
| 会话保存 | 本地 JSON | 飞书 + 本地双保存 |
| 多设备同步 | ❌ | ✅ 飞书自动同步 |
| 消息历史 | 有限 | 完整飞书历史 |
| 移动访问 | ❌ | ✅ 飞书 App |
| 通知推送 | ❌ | ✅ 飞书通知 |

---

**创建日期:** 2026-03-14  
**最后更新:** 2026-03-14 00:40  
**状态:** ✅ 飞书通道已启用，等待用户开始聊天
