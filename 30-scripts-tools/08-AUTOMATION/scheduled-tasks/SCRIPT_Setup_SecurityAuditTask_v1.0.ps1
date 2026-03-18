# OpenClaw Nightly Security Audit - 定时任务安装脚本
# 需要管理员权限运行

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "OpenClaw Nightly Security Audit" -ForegroundColor Cyan
Write-Host "定时任务配置脚本" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$taskName = "OpenClaw-Nightly-Security-Audit"
$scriptPath = "D:\OpenClaw\workspace\nightly-security-audit.ps1"
$taskUser = "huawei"

# 检查脚本是否存在
if (-not (Test-Path $scriptPath)) {
    Write-Host "[ERROR] 脚本不存在：$scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] 脚本路径：$scriptPath" -ForegroundColor Green
Write-Host "[INFO] 任务名称：$taskName" -ForegroundColor Green
Write-Host "[INFO] 执行用户：$taskUser" -ForegroundColor Green
Write-Host ""

# 创建定时任务
$action = New-ScheduledTaskAction -Execute "pwsh.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""

$trigger = New-ScheduledTaskTrigger -Daily -At 3am

$principal = New-ScheduledTaskPrincipal `
    -UserId $taskUser `
    -LogonType Interactive `
    -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Write-Host "[INFO] 创建定时任务..." -ForegroundColor Yellow

try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Force `
        -ErrorAction Stop
    
    Write-Host ""
    Write-Host "[OK] 定时任务创建成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "任务详情:" -ForegroundColor Cyan
    Write-Host "  名称：$taskName"
    Write-Host "  时间：每日凌晨 3:00 AM"
    Write-Host "  脚本：$scriptPath"
    Write-Host ""
    Write-Host "验证命令：" -ForegroundColor Cyan
    Write-Host "  Get-ScheduledTask -TaskName `"$taskName`""
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "[ERROR] 创建失败：$($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "请尝试以下方案：" -ForegroundColor Yellow
    Write-Host "  1. 以管理员身份重新运行此脚本"
    Write-Host "  2. 或手动运行以下命令（管理员 PowerShell）:"
    Write-Host ""
    Write-Host "  schtasks /Create /TN `"$taskName`" /TR `"pwsh.exe -NoProfile -ExecutionPolicy Bypass -File `'$scriptPath`'`" /SC DAILY /ST 03:00 /RU `"$taskUser`" /RL HIGHEST /F"
    Write-Host ""
    exit 1
}
