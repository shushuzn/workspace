# Weekly Critic Review - 每周批判者审查脚本
# 功能：每周日 5AM 自动执行批判者 v5.0 审查
# 创建：2026-03-13 (Critic v5.0 fix-005)
# 用法：以管理员权限安装定时任务

$workspace = "D:\OpenClaw\workspace"
$logFile = "$workspace\91-logs-日志\critic-review-$(Get-Date -Format 'yyyyMMdd').log"
$outputFile = "$workspace\30-scripts-脚本工具\WEEKLY-CRITIC-REVIEW-$(Get-Date -Format 'yyyyMMdd').md"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Weekly Critic v5.0 Review" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查工作日志
Write-Host "[1/5] Checking work logs..." -ForegroundColor Yellow
$today = Get-Date -Format 'yyyy-MM-dd'
$logPath = "$workspace\13-memory-记忆系统\$today.md"

if (Test-Path $logPath) {
    Write-Host "  + Today's log exists: $today.md" -ForegroundColor Green
    $logContent = Get-Content $logPath -Raw
    $completedTasks = ([regex]::Matches($logContent, '\[x\]')).Count
    Write-Host "  + Completed tasks: $completedTasks" -ForegroundColor Green
}
else {
    Write-Host "  - Today's log missing!" -ForegroundColor Red
}

# 2. 检查任务状态
Write-Host ""
Write-Host "[2/5] Checking task status..." -ForegroundColor Yellow
$heartbeatPath = "$workspace\13-memory-记忆系统\heartbeat-state.json"

if (Test-Path $heartbeatPath) {
    $heartbeat = Get-Content $heartbeatPath -Raw | ConvertFrom-Json
    $pendingCount = ($heartbeat.todo | Where-Object { $_.status -eq 'pending' }).Count
    $completedCount = ($heartbeat.todo | Where-Object { $_.status -eq 'completed' }).Count
    Write-Host "  + Pending tasks: $pendingCount" -ForegroundColor $(if($pendingCount -gt 5){"Red"}else{"Green"})
    Write-Host "  + Completed tasks: $completedCount" -ForegroundColor Green
}
else {
    Write-Host "  - heartbeat-state.json missing!" -ForegroundColor Red
}

# 3. 检查文档覆盖率
Write-Host ""
Write-Host "[3/5] Checking documentation coverage..." -ForegroundColor Yellow
$readmePath = "$workspace\30-scripts-脚本工具\README.md"

if (Test-Path $readmePath) {
    $readmeContent = Get-Content $readmePath -Raw
    if ($readmeContent -match '100%') {
        Write-Host "  + Documentation coverage: 100%" -ForegroundColor Green
    }
    else {
        Write-Host "  - Documentation coverage < 100%" -ForegroundColor Yellow
    }
}
else {
    Write-Host "  - README.md missing!" -ForegroundColor Red
}

# 4. 检查定时任务
Write-Host ""
Write-Host "[4/5] Checking scheduled tasks..." -ForegroundColor Yellow
$taskNames = @("OpenClaw-Heartbeat", "OpenClaw-Domain-Ranking", "OpenClaw-Daily-Log", "LIG-Risk-Monitor")
$installedCount = 0

foreach ($taskName in $taskNames) {
    try {
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction Stop
        if ($task.State -eq "Ready") {
            Write-Host "  + $taskName: Ready" -ForegroundColor Green
            $installedCount++
        }
    }
    catch {
        Write-Host "  - $taskName: Not installed" -ForegroundColor Red
    }
}

Write-Host "  Installed: $installedCount / $($taskNames.Count)" -ForegroundColor $(if($installedCount -eq $taskNames.Count){"Green"}else{"Yellow"})

# 5. 生成审查报告
Write-Host ""
Write-Host "[5/5] Generating review report..." -ForegroundColor Yellow

$report = @"
# Weekly Critic v5.0 Review / 每周批判者审查

**Date:** $(Get-Date -Format 'yyyy-MM-dd HH:mm')  
**Week:** $(Get-Date -UFormat %V) of $(Get-Date -Year)

---

## 📊 Week Summary / 本周总结

### Task Completion / 任务完成
- Completed: $completedCount tasks
- Pending: $pendingCount tasks
- Work Log: $(if(Test-Path $logPath){"✅"}else{"❌"})

### Documentation / 文档
- Coverage: $(if($readmeContent -match '100%'){"100% ✅"}else{"<100% ⚠️"})
- README: $(if(Test-Path $readmePath){"✅"}else{"❌"})

### Automation / 自动化
- Scheduled Tasks: $installedCount / $($taskNames.Count)
- Status: $(if($installedCount -eq $taskNames.Count){"✅"}else{"⚠️"})

---

## 🔴 Critical Issues / 致命问题

$(if($pendingCount -gt 10){"1. Too many pending tasks (>10)"}else{"None"})
$(if(-not (Test-Path $logPath)){"1. Work log missing"}else{"None"})

---

## ⚠️ Major Issues / 严重问题

$(if($installedCount -lt $taskNames.Count){"1. Scheduled tasks not fully installed"}else{"None"})
$(if(-not ($readmeContent -match '100%')){"1. Documentation coverage < 100%"}else{"None"})

---

## 📈 Critic Score / 批判者评分

| Category | Score | Notes |
|----------|-------|-------|
| Task Execution | $(if($completedCount -gt 5){"9/10"}else{"6/10"}) | $completedCount completed |
| Documentation | $(if($readmeContent -match '100%'){"10/10"}else{"7/10"}) | Coverage |
| Automation | $(if($installedCount -eq $taskNames.Count){"10/10"}else{"5/10"}) | $installedCount/$($taskNames.Count) |
| **Total** | **$(if($completedCount -gt 5 -and $readmeContent -match '100%' -and $installedCount -eq $taskNames.Count){"9/10"}else{"7/10"})** | |

---

## 🎯 Next Week Goals / 下周目标

1. [ ] [Goal 1]
2. [ ] [Goal 2]
3. [ ] [Goal 3]

---

*Generated:* $(Get-Date -Format 'yyyy-MM-dd HH:mm')  
*Next Review:* $(Get-Date -AddDays 7 -Format 'yyyy-MM-dd')
"@

$report | Out-File -FilePath $outputFile -Encoding UTF8
Write-Host "  + Report saved: $outputFile" -ForegroundColor Green

# 记录日志
"$(Get-Date -Format 'o') - Weekly critic review completed" | Out-File $logFile -Append
"$(Get-Date -Format 'o') - Score: $(if($completedCount -gt 5 -and $readmeContent -match '100%' -and $installedCount -eq $taskNames.Count){"9/10"}else{"7/10"})" | Out-File $logFile -Append

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Weekly Review Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
