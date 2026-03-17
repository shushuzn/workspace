# 配置每日简报定时任务
# 每工作日 8:00 AM 自动运行并发送到 Feishu

$TaskName = "DailyBrief-Feishu"
$ScriptPath = "D:\OpenClaw\workspace\30-scripts\daily-brief.py"
$TriggerTime = "08:00"

Write-Host "📅 配置每日简报定时任务" -ForegroundColor Cyan
Write-Host "  任务名称：$TaskName"
Write-Host "  脚本路径：$ScriptPath"
Write-Host "  触发时间：每工作日 $TriggerTime"

# 创建任务 (需要管理员权限)
$action = New-ScheduledTaskAction -Execute "py" -Argument "`"$ScriptPath`" --send" -WorkingDirectory "D:\OpenClaw\workspace"
$trigger = New-ScheduledTaskTrigger -Daily -At $TriggerTime -DaysOfWeek 1,2,3,4,5
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force
    Write-Host "`n✅ 定时任务创建成功！" -ForegroundColor Green
    Write-Host "  查看任务：Get-ScheduledTask -TaskName `"$TaskName`""
    Write-Host "  手动触发：Start-ScheduledTask -TaskName `"$TaskName`""
    Write-Host "  删除任务：Unregister-ScheduledTask -TaskName `"$TaskName`" -Confirm:`$false"
} catch {
    Write-Host "`n⚠️ 创建失败 (可能需要管理员权限)" -ForegroundColor Yellow
    Write-Host "  请以管理员身份运行 PowerShell 后重试"
    Write-Host "`n  或手动运行脚本测试："
    Write-Host "  py `"$ScriptPath`" --send"
}
