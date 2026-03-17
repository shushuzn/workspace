# Quick Integration Guide | 飞书通知快速集成

## 🚀 5 分钟集成定时任务通知

### Step 1: 确认配置 (1 分钟)

```bash
cd D:\OpenClaw\workspace\30-scripts-tools\feishu-tools

# 检查配置文件
cat feishu-config.json

# 测试 Token 状态
python feishu_api.py token_info
```

### Step 2: 测试通知 (1 分钟)

```bash
# 发送测试通知
python cron_notification.py "Test" "success" "Integration test"
```

✅ 收到飞书消息 = 配置正确

### Step 3: 集成到脚本 (3 分钟)

#### 方法 A: Python 脚本

```python
# your_task.py
import subprocess
import sys

def main():
    try:
        # Your task logic here
        result = do_your_task()
        
        # Send success notification
        subprocess.run([
            sys.executable,
            "cron_notification.py",
            "Your Task",
            "success",
            f"Completed: {result}"
        ], cwd=r"D:\OpenClaw\workspace\30-scripts-tools\feishu-tools")
        
    except Exception as e:
        # Send failure notification
        subprocess.run([
            sys.executable,
            "cron_notification.py",
            "Your Task",
            "failed",
            str(e)
        ], cwd=r"D:\OpenClaw\workspace\30-scripts-tools\feishu-tools")
        raise

if __name__ == "__main__":
    main()
```

#### 方法 B: 批处理脚本

```batch
@echo off
cd /d D:\OpenClaw\workspace\30-scripts-tools\feishu-tools

REM Run your task
your_task.bat

REM Send notification based on exit code
if %ERRORLEVEL% EQU 0 (
    python cron_notification.py "Your Task" "success" "Completed successfully"
) else (
    python cron_notification.py "Your Task" "failed" "Exit code: %ERRORLEVEL%"
)
```

#### 方法 C: PowerShell 脚本

```powershell
# your_task.ps1
$feishuDir = "D:\OpenClaw\workspace\30-scripts-tools\feishu-tools"

try {
    # Your task logic
    & .\your_task.ps1
    
    # Success notification
    & python "$feishuDir\cron_notification.py" `
        "Your Task" `
        "success" `
        "Completed successfully"
}
catch {
    # Failure notification
    & python "$feishuDir\cron_notification.py" `
        "Your Task" `
        "failed" `
        $_.Exception.Message
}
```

### Step 4: 配置定时任务

#### Windows 任务计划程序

1. 打开 **任务计划程序**
2. 创建基本任务
3. 设置触发器 (如：每天 7:00)
4. 操作：启动程序
   - 程序：`python.exe`
   - 参数：`cron_notification.py "Task" "success" "Done"`
   - 起始于：`D:\OpenClaw\workspace\30-scripts-tools\feishu-tools`

#### Copaw Cron (如果可用)

```bash
copaw cron create ^
  --schedule "0 7 * * *" ^
  --type agent ^
  --channel console ^
  --text "Run task and notify via feishu"
```

## 📋 常用通知模板

### 每日风险预警 (7AM)

```bash
python cron_notification.py ^
  "7AM Risk Warning" ^
  "success" ^
  "✓ 0 overdue | ✓ 3 pending | ✓ System healthy"
```

### 记忆蒸馏 (周日 5AM)

```bash
python cron_notification.py ^
  "Weekly Memory Distillation" ^
  "success" ^
  "Distilled 20+ points from 7 daily notes"
```

### Git 同步检查

```bash
python cron_notification.py ^
  "Git Sync Check" ^
  "warning" ^
  "⚠ 3 uncommitted changes detected"
```

### 服务器健康检查

```bash
python cron_notification.py ^
  "Cloud Server Health" ^
  "success" ^
  "CPU 2% | Memory 56% | Disk 34% | Status: Healthy"
```

## 🔍 故障排查

### 问题 1: 收不到通知

```bash
# 检查 Token
python feishu_api.py token_info

# 测试基础功能
python feishu_api.py send_text "Test"

# 检查配置
cat feishu-config.json
```

### 问题 2: 中文乱码

```powershell
# PowerShell 设置 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### 问题 3: 脚本找不到

使用绝对路径：
```bash
python D:\OpenClaw\workspace\30-scripts-tools\feishu-tools\cron_notification.py "Task" "success" "Done"
```

## ✅ 验证清单

- [ ] feishu-config.json 配置正确
- [ ] Token 状态有效
- [ ] 测试消息成功发送
- [ ] 脚本集成到任务
- [ ] 定时任务已配置
- [ ] 收到通知消息

---

**集成时间:** < 5 分钟  
**难度:** ⭐☆☆☆☆ (简单)  
**支持:** 🐾 Claw AI Agent
