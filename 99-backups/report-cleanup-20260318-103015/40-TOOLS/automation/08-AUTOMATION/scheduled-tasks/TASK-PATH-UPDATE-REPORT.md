# 定时任务路径更新报告

**更新日期:** 2026-03-11 19:10  
**更新状态:** 部分完成 (需管理员权限)

---

## ✅ 已更新任务

### 1. DailyBrief-Feishu
- **旧路径:** `30-scripts\daily-brief.py`
- **新路径:** `30-scripts\02-DAILY-BRIEF\core\daily-brief.py`
- **状态:** ✅ 已更新
- **命令:**
```powershell
$action = New-ScheduledTaskAction -Execute "C:\Windows\py.exe" -Argument "D:\OpenClaw\workspace\30-scripts\02-DAILY-BRIEF\core\daily-brief.py --send"
Set-ScheduledTask -TaskName "DailyBrief-Feishu" -Action $action
```

### 2. nightly-security-audit
- **旧路径:** `nightly-security-audit.ps1`
- **新路径:** `30-scripts\13-SECURITY\scripts\SCRIPT_Nightly_SecurityAudit_v1.0.ps1`
- **状态:** ✅ 已更新
- **命令:**
```powershell
$action = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File D:\OpenClaw\workspace\30-scripts\13-SECURITY\scripts\SCRIPT_Nightly_SecurityAudit_v1.0.ps1"
Set-ScheduledTask -TaskName "nightly-security-audit" -Action $action
```

---

## ⚠️ 需要手动更新的任务

以下任务因权限问题需要手动更新 (以管理员身份运行 PowerShell):

### 3. OpenClaw-Nightly-Security-Audit
- **旧路径:** `nightly-security-audit.ps1`
- **新路径:** `30-scripts\13-SECURITY\scripts\SCRIPT_Nightly_SecurityAudit_v1.0.ps1`
- **状态:** ⚠️ 需要管理员权限
- **命令:**
```powershell
# 以管理员身份运行 PowerShell
$action = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"D:\OpenClaw\workspace\30-scripts\13-SECURITY\scripts\SCRIPT_Nightly_SecurityAudit_v1.0.ps1`""
Set-ScheduledTask -TaskName "OpenClaw-Nightly-Security-Audit" -Action $action
```

### 4. OpenClaw-Arxiv-Collect
- **路径:** `arxiv-daily` 技能 (独立目录)
- **状态:** ✅ 无需更新 (路径未变)
- **说明:** arXiv 收集器在 `npm-global\node_modules\openclaw\skills\arxiv-daily\` 独立目录，不受 30-scripts 重组影响

### 5. OpenClaw-Arxiv-Collector
- **旧路径:** `arxiv-workflow.ps1`
- **新路径:** 需确认文件位置
- **状态:** ⚠️ 需检查
- **命令:**
```powershell
# 检查文件是否存在
Test-Path "D:\OpenClaw\workspace\arxiv-workflow.ps1"

# 如果不存在，可能需要更新为新的收集器路径
```

---

## 📋 手动更新步骤

### 方法 1: 任务计划程序 GUI
1. 按 `Win+R` 输入 `taskschd.msc`
2. 找到对应任务
3. 右键 → 属性 → 操作 → 编辑
4. 更新路径为新路径
5. 确定保存

### 方法 2: PowerShell (管理员)
```powershell
# 以管理员身份运行 PowerShell

# 更新 OpenClaw-Nightly-Security-Audit
$action = New-ScheduledTaskAction -Execute "pwsh.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"D:\OpenClaw\workspace\30-scripts\13-SECURITY\scripts\SCRIPT_Nightly_SecurityAudit_v1.0.ps1`""
Set-ScheduledTask -TaskName "OpenClaw-Nightly-Security-Audit" -Action $action

# 验证更新
Get-ScheduledTask -TaskName "OpenClaw-Nightly-Security-Audit" | Select-Object -ExpandProperty Actions
```

---

## ✅ 验证方法

### 验证所有任务路径
```powershell
$tasks = @("DailyBrief-Feishu", "nightly-security-audit", "OpenClaw-Nightly-Security-Audit", "OpenClaw-Arxiv-Collect", "OpenClaw-Arxiv-Collector")
foreach($t in $tasks) {
    Write-Host "`n=== $t ===" -ForegroundColor Cyan
    Get-ScheduledTask -TaskName $t | Select-Object -ExpandProperty Actions | Format-List
}
```

### 手动触发测试
```powershell
# 测试 DailyBrief
Start-ScheduledTask -TaskName "DailyBrief-Feishu"

# 测试安全审计
Start-ScheduledTask -TaskName "nightly-security-audit"

# 查看任务历史
Get-ScheduledTaskInfo -TaskName "DailyBrief-Feishu" | Select-Object LastRunTime, LastTaskResult
```

---

## 📊 更新统计

| 任务 | 旧路径 | 新路径 | 状态 |
|------|--------|--------|------|
| DailyBrief-Feishu | 30-scripts\daily-brief.py | 02-DAILY-BRIEF\core\daily-brief.py | ✅ |
| nightly-security-audit | nightly-security-audit.ps1 | 13-SECURITY\scripts\SCRIPT_*.ps1 | ✅ |
| OpenClaw-Nightly-Security-Audit | nightly-security-audit.ps1 | 13-SECURITY\scripts\SCRIPT_*.ps1 | ⚠️ 需管理员 |
| OpenClaw-Arxiv-Collect | arxiv-daily (独立) | arxiv-daily (独立) | ✅ 无需更新 |
| OpenClaw-Arxiv-Collector | arxiv-workflow.ps1 | 待确认 | ⚠️ 需检查 |

---

## 🎯 下一步

1. ✅ DailyBrief-Feishu - 已更新
2. ✅ nightly-security-audit - 已更新
3. ⏳ OpenClaw-Nightly-Security-Audit - 需管理员权限
4. ✅ OpenClaw-Arxiv-Collect - 无需更新
5. ⏳ OpenClaw-Arxiv-Collector - 需检查文件位置

---

*更新完成 | 2026-03-11 19:10*
