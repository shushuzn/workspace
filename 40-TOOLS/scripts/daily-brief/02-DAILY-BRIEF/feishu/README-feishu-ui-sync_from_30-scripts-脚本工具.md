# Feishu ↔ Control UI 消息同步工具

**功能:** 双向同步飞书和 Control UI 的消息，实现跨通道聊天。

---

## 🚀 快速开始

### 1️⃣ 手动同步一次
```bash
py 30-scripts\feishu-ui-sync.py --sync-last 10
```

### 2️⃣ 持续监听模式
```bash
py 30-scripts\feishu-ui-sync.py --watch --interval 30
```

### 3️⃣ 后台运行 (Windows 任务计划)
```bash
# 创建定时任务 (每 30 秒同步一次)
schtasks /Create /TN "OpenClaw-Feishu-UI-Sync" /TR "py D:\OpenClaw\workspace\30-scripts\feishu-ui-sync.py --watch --interval 30" /SC MINUTE /MO 1 /RL HIGHEST /F
```

---

## 📖 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--watch, -w` | 持续监听模式 | 否 |
| `--interval, -i` | 监听间隔 (秒) | 30 |
| `--sync-last, -s` | 同步最近 N 条消息 | - |
| `--gateway, -g` | Gateway URL | http://127.0.0.1:18789 |
| `--user, -u` | 飞书用户 ID | ou_72a847b95fc25870dcdd8ce56d929252 |
| `--reset, -r` | 重置同步状态 | 否 |

---

## 📊 同步逻辑

### 飞书 → UI
```
飞书消息 → 检测新消息 → 转发到 Control UI → 标记已同步
```

### UI → 飞书
```
UI 消息 → 检测新消息 → 转发到飞书 → 标记已同步
```

### 状态文件
**位置:** `13-memory/feishu-ui-sync-state.json`

**内容:**
```json
{
  "last_feishu_msg_id": "om_xxx",
  "last_ui_msg_id": "msg_xxx",
  "last_sync_time": "2026-03-11T12:11:42",
  "synced_count": 0
}
```

---

## ⚠️ 注意事项

1. **避免循环同步** - 已同步的消息不会重复转发
2. **跳过机器人消息** - 只同步用户消息
3. **跳过工具调用** - 不转发 `/command` 和工具调用消息
4. **会话隔离** - 仅同步 `agent:main:main` 会话

---

## 🔧 故障排查

### 问题 1: 同步不工作
```bash
# 检查 Gateway 是否运行
openclaw status

# 检查飞书通道状态
openclaw config get channels.feishu

# 重置同步状态
py 30-scripts\feishu-ui-sync.py --reset
```

### 问题 2: 消息重复
```bash
# 重置同步状态
py 30-scripts\feishu-ui-sync.py --reset
```

### 问题 3: 权限错误
```bash
# 确保飞书用户 OAuth 已授权
# 在飞书中重新授权 OpenClaw 插件
```

---

## 📝 日志示例

```
🔄 开始同步... (12:11:42)
📥 飞书消息：3 条
✅ 已发送到 UI: [飞书] 用户：测试消息...
📥 UI 消息：2 条
✅ 已发送到飞书：[UI] 你好...
✅ 同步完成 (累计：5 条)
```

---

## 🎯 使用场景

- ✅ 在 Control UI 配置，在飞书聊天
- ✅ 在飞书接收通知，在 UI 查看历史
- ✅ 多设备同步 (手机飞书 + 电脑 UI)
- ✅ 消息备份和归档

---

## 📄 相关文件

| 文件 | 说明 |
|------|------|
| `feishu-ui-sync.py` | 同步脚本 |
| `feishu-ui-sync-cron.json` | Cron 配置 |
| `13-memory/feishu-ui-sync-state.json` | 同步状态 |

---

**版本:** 1.0  
**最后更新:** 2026-03-11
