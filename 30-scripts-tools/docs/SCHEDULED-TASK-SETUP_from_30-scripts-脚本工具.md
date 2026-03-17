# 📅 每日简报定时任务配置指南

## 自动配置 (推荐)

**以管理员身份运行 PowerShell**，然后执行：

```powershell
py D:\OpenClaw\workspace\30-scripts\setup-scheduled-task.py
```

## 手动配置

**以管理员身份运行 PowerShell**，然后执行：

```powershell
schtasks /create /tn "DailyBrief-Feishu" /tr 'py "D:\OpenClaw\workspace\30-scripts\daily-brief.py" --send' /sc weekly /st 08:00 /d MON,TUE,WED,THU,FRI /mo 1 /ru SYSTEM /f
```

## 验证配置

```powershell
# 查看任务状态
schtasks /query /tn "DailyBrief-Feishu"

# 查看任务历史
Get-ScheduledTask -TaskName "DailyBrief-Feishu" | Get-ScheduledTaskInfo

# 手动触发测试
schtasks /run /tn "DailyBrief-Feishu"
```

## 管理命令

| 操作 | 命令 |
|------|------|
| 查看任务 | `schtasks /query /tn "DailyBrief-Feishu"` |
| 手动触发 | `schtasks /run /tn "DailyBrief-Feishu"` |
| 删除任务 | `schtasks /delete /tn "DailyBrief-Feishu" /f` |
| 禁用任务 | `schtasks /change /tn "DailyBrief-Feishu" /disable` |
| 启用任务 | `schtasks /change /tn "DailyBrief-Feishu" /enable` |

## 执行日志

日志文件位置：
- 简报文件：`D:\OpenClaw\workspace\21-reports\daily-briefs\brief-YYYY-MM-DD.md`
- Feishu 发送日志：`D:\OpenClaw\workspace\21-reports\feishu-send-log.jsonl`
- 队列文件：`D:\OpenClaw\workspace\13-memory\feishu-queue.json`

## 故障排查

### 问题 1: 任务未执行
**检查:**
```powershell
Get-ScheduledTask -TaskName "DailyBrief-Feishu" | Get-ScheduledTaskInfo
```

**解决:**
- 确认任务状态为"Ready"
- 检查上次运行结果
- 手动触发测试

### 问题 2: Python 未找到
**解决:**
```powershell
# 修改任务命令，使用 Python 完整路径
schtasks /change /tn "DailyBrief-Feishu" /tr 'C:\Users\你的用户名\AppData\Local\Programs\Python\Python313\python.exe "D:\OpenClaw\workspace\30-scripts\daily-brief.py" --send'
```

### 问题 3: Feishu 推送失败
**检查:**
- 查看 `feishu-queue.json` 是否有积压
- 运行 `py 30-scripts/process-feishu-queue.py` 手动处理队列

## 当前配置

- **任务名称:** DailyBrief-Feishu
- **执行时间:** 每周一到周五 08:00
- **执行脚本:** `daily-brief.py --send`
- **运行用户:** SYSTEM

---

*最后更新：2026-03-10*
