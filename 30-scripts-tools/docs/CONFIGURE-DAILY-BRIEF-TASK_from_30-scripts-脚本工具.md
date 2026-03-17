# 📅 配置每日简报定时任务

**创建日期:** 2026-03-10  
**任务名称:** DailyBrief-Feishu  
**执行时间:** 每工作日 08:00

---

## 🚀 快速配置

### 方法 1: 一键配置 (推荐)

**以管理员身份运行 PowerShell**，执行：

```powershell
py D:\OpenClaw\workspace\30-scripts\setup-scheduled-task.py
```

---

### 方法 2: 手动配置

**以管理员身份运行 PowerShell**，执行：

```powershell
schtasks /create /tn "DailyBrief-Feishu" /tr "py D:\OpenClaw\workspace\30-scripts\daily-brief.py --send" /sc weekly /st 08:00 /d MON,TUE,WED,THU,FRI /mo 1 /ru SYSTEM /f
```

**参数说明:**
- `/tn "DailyBrief-Feishu"` - 任务名称
- `/tr "py ..."` - 执行的命令
- `/sc weekly` - 每周触发
- `/st 08:00` - 早上 8 点
- `/d MON,TUE,WED,THU,FRI` - 工作日
- `/mo 1` - 每 1 周
- `/ru SYSTEM` - 以 SYSTEM 用户运行
- `/f` - 强制覆盖已存在的任务

---

## ✅ 验证配置

### 查看任务状态
```powershell
schtasks /query /tn "DailyBrief-Feishu"
```

### 手动触发测试
```powershell
schtasks /run /tn "DailyBrief-Feishu"
```

### 查看任务历史
```powershell
Get-ScheduledTask -TaskName "DailyBrief-Feishu" | Get-ScheduledTaskInfo
```

---

## 📁 输出位置

- **简报文件:** `21-reports/daily-briefs/brief-YYYY-MM-DD.md`
- **发送队列:** `13-memory/feishu-queue.json`
- **发送日志:** `21-reports/feishu-send-log.jsonl`

---

## 🔧 管理命令

| 操作 | 命令 |
|------|------|
| 查看任务 | `schtasks /query /tn "DailyBrief-Feishu"` |
| 手动触发 | `schtasks /run /tn "DailyBrief-Feishu"` |
| 删除任务 | `schtasks /delete /tn "DailyBrief-Feishu" /f` |
| 禁用任务 | `schtasks /change /tn "DailyBrief-Feishu" /disable` |
| 启用任务 | `schtasks /change /tn "DailyBrief-Feishu" /enable` |

---

## 🐛 故障排查

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
schtasks /change /tn "DailyBrief-Feishu" /tr '"C:\Users\你的用户名\AppData\Local\Programs\Python\Python313\python.exe" "D:\OpenClaw\workspace\30-scripts\daily-brief.py" --send'
```

### 问题 3: Feishu 推送失败

**检查:**
- 查看 `feishu-queue.json` 是否有积压
- 运行 `py 30-scripts/process-feishu-queue.py` 手动处理队列

---

## 📊 预期效果

**每工作日 8:00 AM 自动执行:**
1. 收集昨日 arXiv/Medium/GitHub/HN 数据
2. 生成 Markdown 简报
3. 发送到 Feishu
4. 记录执行日志

**简报内容:**
- 📊 核心指标 (arXiv/Medium/GitHub 统计)
- 🏆 领域段位 Top 3
- 🔥 高优先级内容
- 🌐 HackerNews 热门
- 🌤️ 天气信息
- 📅 今日日历
- 📈 7 天趋势图

---

*配置完成后，每日自动接收研究简报！*
