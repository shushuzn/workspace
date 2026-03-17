# OpenClaw 定时任务配置脚本
# 配置两个定时任务：
# 1. 每日 2am - arxiv 论文自动收集
# 2. 每日 3am - 夜间安全审计

$ScriptDir = "C:\Users\华为\.openclaw\workspace"
$TaskPrefix = "OpenClaw"

Write-Host "========================================"
Write-Host "OpenClaw 定时任务配置"
Write-Host "========================================"
Write-Host ""

# 任务 1: arxiv 论文收集 (每日 2am)
Write-Host "[1/2] 配置 arxiv 收集任务 (每日 2am)..."
$taskName = "$TaskPrefix-Arxiv-Collector"
$scriptPath = "$ScriptDir\arxiv-workflow.ps1"

# 检查任务是否存在
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "      任务已存在，跳过" -ForegroundColor Yellow
} else {
    # 创建触发器 (每日 2am)
    $trigger = New-ScheduledTaskTrigger -Daily -At 2am
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    # 注册任务
    Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action $action -Settings $settings -Force
    Write-Host "      [OK] 任务已创建" -ForegroundColor Green
}

# 任务 2: 夜间安全审计 (每日 3am)
Write-Host "[2/2] 配置安全审计任务 (每日 3am)..."
$taskName = "$TaskPrefix-Security-Audit"
$scriptPath = "$ScriptDir\nightly-security-audit.ps1"

# 检查任务是否存在
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "      任务已存在，跳过" -ForegroundColor Yellow
} else {
    # 创建触发器 (每日 3am)
    $trigger = New-ScheduledTaskTrigger -Daily -At 3am
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    # 注册任务
    Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action $action -Settings $settings -Force
    Write-Host "      [OK] 任务已创建" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================"
Write-Host "配置完成"
Write-Host "========================================"
Write-Host ""
Write-Host "已配置任务:"
Get-ScheduledTask -TaskName "$TaskPrefix-*" | Select-Object TaskName, State | Format-Table
