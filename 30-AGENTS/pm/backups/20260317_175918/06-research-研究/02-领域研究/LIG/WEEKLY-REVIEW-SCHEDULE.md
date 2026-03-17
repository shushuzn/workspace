# 周审查定时任务配置说明

**配置日期:** 2026-03-13  
**任务:** 配置每周日 5AM 自动批判者审查

---

## 📋 配置步骤

### 1. 确认脚本存在

```powershell
Test-Path "D:\OpenClaw\workspace\30-scripts-脚本工具\weekly-critic-review.ps1"
# 应返回：True
```

### 2. 手动测试脚本

```powershell
cd "D:\OpenClaw\workspace\30-scripts-脚本工具"
powershell -ExecutionPolicy Bypass -File weekly-critic-review.ps1
```

### 3. 配置 Windows 定时任务

**以管理员身份运行 PowerShell:**

```powershell
$taskName = "OpenClaw-Weekly-Critic-Review"
$scriptPath = "D:\OpenClaw\workspace\30-scripts-脚本工具\weekly-critic-review.ps1"

$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 5am
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Force
```

### 4. 验证配置

```powershell
Get-ScheduledTask -TaskName "OpenClaw-Weekly-Critic-Review"
```

**预期输出:**
```
TaskPath                                       TaskName                          State     
--------                                       --------                          -----     
\                                              OpenClaw-Weekly-Critic-Review     Ready     
```

---

## 📊 审查输出

### 生成文件
- `WEEKLY-CRITIC-REVIEW-YYYYMMDD.md` - 周审查报告
- `91-logs-日志\critic-review-*.log` - 审查日志

### 审查内容
1. 工作日志检查
2. 任务状态检查
3. 文档覆盖率检查
4. 定时任务状态检查
5. 批判者评分

---

## ⏰ 审查时间

| 项目 | 时间 |
|------|------|
| 审查频率 | 每周日 |
| 审查时间 | 5:00 AM |
| 预计用时 | 5-10 分钟 |
| 输出位置 | 30-scripts-脚本工具/ |

---

## 🔔 通知机制

### 审查完成通知
审查完成后自动生成报告，用户可在飞书查看。

### 异常告警
如审查发现致命问题，自动发送告警通知。

---

## 📝 配置记录

| 日期 | 操作 | 状态 | 备注 |
|------|------|------|------|
| 2026-03-13 | 创建配置说明 | ✅ | 待执行配置 |
| 2026-03-13 | 配置定时任务 | ⏳ | 待执行 |
| 2026-03-16 | 首次审查 | ⏳ | 待执行 |

---

*Created:* 2026-03-13 13:10  
*Status:* ⏳ 待配置定时任务  
*Next:* 执行 PowerShell 配置命令
