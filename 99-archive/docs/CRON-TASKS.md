# OpenClaw 定时任务配置

**创建时间:** 2026-03-04  
**状态:** ✅ 已配置

---

## 📋 任务列表

### 每日收集任务（9:00 AM）

```json
{
  "name": "daily-collect",
  "schedule": "0 9 * * *",
  "command": "cd D:\\OpenClaw\\workspace\\scripts && py collect-all.ps1",
  "enabled": true,
  "description": "每日收集 Arxiv/Medium/Twitter/Reddit/HackerNews"
}
```

### 每周报告（周一 10:00 AM）

```json
{
  "name": "weekly-report",
  "schedule": "0 10 * * 1",
  "command": "cd D:\\OpenClaw\\workspace\\scripts && py report-generator.py weekly",
  "enabled": true,
  "description": "生成研究周报"
}
```

### 自动标签（每周三 11:00 AM）

```json
{
  "name": "auto-tag",
  "schedule": "0 11 * * 3",
  "command": "cd D:\\OpenClaw\\workspace\\scripts && py auto-tagger.py --dir all --limit 50",
  "enabled": true,
  "description": "自动为新笔记打标签"
}
```

---

## ⚙️ 配置方法

### 方法 1: Windows 任务计划程序（推荐）

```powershell
# 1. 打开任务计划程序
taskschd.msc

# 2. 创建基本任务
# - 名称：OpenClaw-Daily-Collect
# - 触发器：每天 9:00 AM
# - 操作：启动程序
#   - 程序：py
#   - 参数：collect-all.ps1
#   - 起始于：D:\OpenClaw\workspace\scripts
```

### 方法 2: 使用脚本自动注册

运行 `setup-tasks.ps1` 自动创建所有任务。

### 方法 3: 手动运行

```powershell
cd D:\OpenClaw\workspace\scripts
.\collect-all.ps1
```

---

## 📊 监控日志

日志位置：`D:\OpenClaw\workspace\scripts\*.log`

- `x-twitter.log` - Twitter 收集日志
- `reddit-monitor.log` - Reddit 收集日志
- `auto-tagger.log` - 自动标签日志

---

## 🛑 禁用任务

编辑此文件，将 `enabled` 改为 `false`，然后运行：

```powershell
.\setup-tasks.ps1 --unregister
```

---

**最后更新:** 2026-03-04
