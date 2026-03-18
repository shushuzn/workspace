# Cron Task Notifications | 定时任务通知配置

## 📋 概述

定时任务完成后自动发送飞书通知，实现远程任务监控。

## 🔧 配置

### 必需文件
- `feishu-config.json` - 飞书 API 配置
- `cron_notification.py` - 通知发送脚本

### 环境变量 (可选)
```bash
FEISHU_APP_ID=cli_xxxxx
FEISHU_APP_SECRET=xxxxx
FEISHU_RECEIVE_ID=ou_xxxxx
```

## 📝 使用方法

### 命令行调用

```bash
# 任务成功
python cron_notification.py "Task Name" "success" "All checks passed"

# 任务失败
python cron_notification.py "Task Name" "failed" "Error: timeout after 300s"

# 警告状态
python cron_notification.py "Task Name" "warning" "2 checks failed, 5 passed"
```

### 在 Cron 任务中集成

#### 方法 1: 任务完成后调用

```bash
# Windows Task Scheduler
your_task.bat && python cron_notification.py "Your Task" "success" "Completed"
|| python cron_notification.py "Your Task" "failed" "Exit code: %ERRORLEVEL%"
```

#### 方法 2: 在脚本内部调用

```python
# your_script.py
import subprocess
import sys

def main():
    try:
        # Your task logic
        result = do_something()
        
        # Send success notification
        subprocess.run([
            sys.executable, "cron_notification.py",
            "Your Task", "success", f"Processed {result} items"
        ])
        
    except Exception as e:
        # Send failure notification
        subprocess.run([
            sys.executable, "cron_notification.py",
            "Your Task", "failed", str(e)
        ])
        raise

if __name__ == "__main__":
    main()
```

#### 方法 3: Copaw Cron 任务

```bash
# 创建带通知的 agent 任务
copaw cron create ^
  --schedule "0 7 * * *" ^
  --type agent ^
  --channel console ^
  --text "Run 7AM risk warning and send notification via: python cron_notification.py '7AM Risk Warning' 'success' 'Report sent'"
```

## 🎯 通知模板

### 状态类型

| 状态 | Emoji | 颜色 | 使用场景 |
|------|-------|------|----------|
| success | ✅ | green | 任务正常完成 |
| failed | ❌ | red | 任务执行失败 |
| warning | ⚠️ | orange | 部分失败/需要注意 |
| running | ⏳ | blue | 长时间任务开始 |
| skipped | ⭕ | gray | 任务被跳过 |

### 消息格式

```
📋 定时任务通知 | Cron Task Notification

任务名称 | Task Name: 7AM Risk Warning
状态 | Status: ✅ SUCCESS
执行时间 | Executed: 2026-03-14 15:58:30

详情 | Details:
- Scanned 15 tasks
- 0 high priority overdue
- 3 medium priority pending
- System health: Good

🐾 Claw AI Agent - OpenClaw Workspace
```

## 📦 预设通知场景

### 1. 7AM 风险预警

```bash
python cron_notification.py ^
  "7AM Risk Warning" ^
  "success" ^
  "Scanned 15 tasks, 0 overdue, system healthy"
```

### 2. 记忆蒸馏 (周日 5AM)

```bash
python cron_notification.py ^
  "Weekly Memory Distillation" ^
  "success" ^
  "Distilled 23 points from 7 daily notes, updated MEMORY.md"
```

### 3. Git 同步检查

```bash
python cron_notification.py ^
  "Git Sync Check" ^
  "warning" ^
  "3 uncommitted changes detected, please review"
```

### 4. 服务器健康检查

```bash
python cron_notification.py ^
  "Cloud Server Health" ^
  "success" ^
  "CPU: 2%, Memory: 56%, Disk: 34%, Status: Healthy"
```

### 5. 定时备份完成

```bash
python cron_notification.py ^
  "Daily Backup" ^
  "success" ^
  "Backed up 1.2GB to cloud storage, verification passed"
```

## 🔍 测试

```bash
# 测试通知链路
python cron_notification.py "Test Notification" "success" "This is a test message"

# 测试失败通知
python cron_notification.py "Test Notification" "failed" "Simulated failure"
```

## 📊 最佳实践

1. **简洁消息** - 保持消息在一屏内，重点突出
2. **状态明确** - 使用标准状态码 (success/failed/warning)
3. **包含时间戳** - 便于追踪任务执行时间
4. **错误详情** - 失败时提供足够调试信息
5. **避免骚扰** - 只在必要时发送通知

## 🚨 故障排查

### 问题：通知未发送

```bash
# 检查 Token 状态
python feishu_api.py token_info

# 检查配置
cat feishu-config.json

# 测试 API
python feishu_api.py send_text "Test"
```

### 问题：中文乱码

确保文件编码为 UTF-8：
```bash
# Windows PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

---

**Last Updated:** 2026-03-14 15:58  
**Version:** 1.0  
**Author:** Claw AI Agent 🐾
