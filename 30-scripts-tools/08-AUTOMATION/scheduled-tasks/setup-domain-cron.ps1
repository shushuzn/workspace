# 学科学术段位系统 - 定时任务设置脚本
# 每周日 5AM 自动运行数据收集 + 报告生成

$TaskName = "Domain-Ranking-Weekly"
$ScriptPath = "D:\OpenClaw\workspace\30-scripts\domain-ranking-weekly.ps1"
$WorkingDir = "D:\OpenClaw\workspace"

Write-Host "[INFO] 设置学科学术段位系统定时任务..." -ForegroundColor Cyan

# 创建主脚本
$scriptContent = @'
# 学科学术段位系统 - 每周自动更新
# 执行时间：每周日 5AM

$ErrorActionPreference = "Stop"
$Workspace = "D:\OpenClaw\workspace"
$LogPath = "$Workspace\21-reports\domain-ranking-weekly.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logLine = "[$timestamp] $Message"
    Add-Content -Path $LogPath -Value $logLine -Encoding UTF8
    Write-Host $logLine
}

try {
    Write-Log "[START] 开始每周域名排名更新"
    
    # 1. 运行数据收集器
    Write-Log "[STEP 1] 收集 LIG 领域数据..."
    & py "$Workspace\40-arxiv\lig-domain-collector-v2.py" LIG 2>&1 | ForEach-Object { Write-Log $_ }
    
    # 2. 生成段位评估
    Write-Log "[STEP 2] 生成段位评估..."
    & py "$Workspace\30-scripts\domain_ranker_v2.py" --evaluate LIG 2>&1 | ForEach-Object { Write-Log $_ }
    
    # 3. 生成 HTML 报告
    Write-Log "[STEP 3] 生成 HTML 可视化报告..."
    & py "$Workspace\30-scripts\domain_ranking_report.py" LIG 2>&1 | ForEach-Object { Write-Log $_ }
    
    # 4. 清理旧文件 (保留最近 10 个)
    Write-Log "[STEP 4] 清理旧报告..."
    $reports = Get-ChildItem "$Workspace\21-reports\LIG-domain-data-*.json" | Sort-Object LastWriteTime -Descending
    if ($reports.Count -gt 10) {
        $reports | Select-Object -Skip 10 | Remove-Item
        Write-Log "[CLEAN] 已清理旧数据文件"
    }
    
    $htmlReports = Get-ChildItem "$Workspace\21-reports\LIG-domain-ranking-*.html" | Sort-Object LastWriteTime -Descending
    if ($htmlReports.Count -gt 5) {
        $htmlReports | Select-Object -Skip 5 | Remove-Item
        Write-Log "[CLEAN] 已清理旧 HTML 报告"
    }
    
    Write-Log "[DONE] 每周更新完成"
}
catch {
    Write-Log "[ERROR] $_"
    exit 1
}
'@

# 写入脚本文件
Set-Content -Path $ScriptPath -Value $scriptContent -Encoding UTF8
Write-Host "[OK] 脚本已创建：$ScriptPath" -ForegroundColor Green

# 创建定时任务 (每周日 5AM)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 5am
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-NoProfile -WindowStyle Hidden -File `"$ScriptPath`""
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 注册任务
try {
    Register-ScheduledTask -TaskName $TaskName `
        -Principal $principal `
        -Trigger $trigger `
        -Action $action `
        -Settings $settings `
        -Description "学科学术段位系统 - 每周自动数据收集和报告生成" `
        -Force
    
    Write-Host "[OK] 定时任务已注册：$TaskName" -ForegroundColor Green
    Write-Host "[INFO] 执行时间：每周日 5:00 AM" -ForegroundColor Yellow
    
    # 显示任务信息
    Write-Host "`n[INFO] 任务详情:" -ForegroundColor Cyan
    Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, NextRunTime | Format-List
}
catch {
    Write-Host "[ERROR] 创建定时任务失败：$_" -ForegroundColor Red
    Write-Host "[INFO] 请确保以管理员权限运行此脚本" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n[OK] 设置完成！" -ForegroundColor Green
Write-Host "[INFO] 手动运行测试：& '$ScriptPath'" -ForegroundColor Cyan
