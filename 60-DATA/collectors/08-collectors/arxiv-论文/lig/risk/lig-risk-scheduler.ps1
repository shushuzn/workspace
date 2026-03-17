# LIG 风险预警系统 - 定时任务配置
# 每日 7:00 AM 自动运行风险监控

$taskName = "LIG-Risk-Monitor"
$scriptPath = "D:\OpenClaw\workspace\40-arxiv\lig-risk-monitor.py"
$triggerTime = "7:00 AM"

# 检查是否已存在
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "任务已存在，更新中..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# 创建动作
$action = New-ScheduledTaskAction -Execute "py" -Argument $scriptPath -WorkingDirectory "D:\OpenClaw\workspace\40-arxiv"

# 创建触发器（每日 7AM）
$trigger = New-ScheduledTaskTrigger -Daily -At 7am

# 创建设置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# 注册任务
Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "LIG Risk Warning System - Daily monitoring at 7AM" `
    | Out-Null

Write-Host "========================================" -ForegroundColor Green
Write-Host "定时任务创建成功!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Task: LIG-Risk-Monitor"
Write-Host "Schedule: Daily 7:00 AM"
Write-Host "Script: $scriptPath"
Write-Host ""
Write-Host "管理命令:"
Write-Host "  查看状态：Get-ScheduledTask -TaskName $taskName"
Write-Host "  手动运行：Start-ScheduledTask -TaskName $taskName"
Write-Host "  删除任务：Unregister-ScheduledTask -TaskName $taskName -Confirm:`$false"
