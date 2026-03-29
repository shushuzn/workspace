# 🔔 通知配置

**创建日期:** 2026-03-27

---

## 通知渠道

| 渠道 | 状态 | 配置 |
|------|------|------|
| Console | ✅ 启用 | 默认 |
| Feishu | ⚠️ 待配置 | 需 APP_ID/SECRET |
| DingTalk | ⚠️ 待配置 | 需钉钉配置 |
| Telegram | ❌ 未启用 | 需 BOT_TOKEN |
| Discord | ❌ 未启用 | 需 BOT_TOKEN |
| Email | ⚠️ 待配置 | 需 himalaya |

---

## 通知类型

| 类型 | 触发 | 渠道 | 优先级 |
|------|------|------|--------|
| 定时任务完成 | Cron 执行完毕 | Console | 低 |
| 错误告警 | 命令失败 | Console + Feishu | 高 |
| 安全告警 | 发现漏洞 | Console + Feishu | 紧急 |
| 每日摘要 | 每天结束 | Console | 中 |
| 周报 | 每周结束 | Console | 中 |

---

## Feishu 通知配置

当前 `.env` 中配置为空，需要填写：

```bash
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=xxxxx
FEISHU_USER_ID=your_user_id
```

配置后可推送：
- 定时任务结果
- 安全告警
- 每日摘要

---

## 通知模板

### 任务完成
```
✅ [任务名] 完成
📁 输出: {路径}
⏱️ 耗时: {时间}
```

### 安全告警
```
🚨 安全告警
🔍 漏洞: {名称}
📍 位置: {路径}
⚡ 建议: {操作}
```

### 每日摘要
```
📊 每日摘要 - {日期}

✅ 已完成任务:
- {任务1}
- {任务2}

⚠️ 待处理:
- {任务1}

📈 统计数据:
- 执行命令: {数量}
- 生成文件: {数量}
```

---

## 静默时段

可设置免打扰时段：

```yaml
quiet_hours:
  enabled: false
  start: "22:00"
  end: "07:00"
  timezone: "Asia/Shanghai"
  
# 紧急告警不受静默影响
emergency_override:
  - security_alerts
  - critical_errors
```

---

## 快捷命令

| 命令 | 执行 |
|------|------|
| `通知测试` | 发送测试通知 |
| `开启飞书通知` | 配置飞书推送 |
| `静默` | 开启免打扰 |
| `恢复通知` | 关闭免打扰 |
