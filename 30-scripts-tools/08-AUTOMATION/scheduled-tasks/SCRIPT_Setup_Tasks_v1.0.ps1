# OpenClaw 定时任务自动注册脚本
# 使用 Windows 任务计划程序

Set-Location "D:\OpenClaw\workspace\scripts"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OpenClaw 定时任务注册" -ForegroundColor Cyan
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 任务配置
$tasks = @(
    @{
        Name = "OpenClaw-Daily-Collect"
        Description = "每日收集 Arxiv/Medium/Twitter/Reddit/HackerNews"
        Time = "09:00"
        Command = "py"
        Args = "collect-all.ps1"
    },
    @{
        Name = "OpenClaw-Weekly-Report"
        Description = "生成研究周报"
        Time = "10:00"
        DayOfWeek = "Monday"
        Command = "py"
        Args = "report-generator.py weekly"
    },
    @{
        Name = "OpenClaw-Auto-Tag"
        Description = "自动为新笔记打标签"
        Time = "11:00"
        DayOfWeek = "Wednesday"
        Command = "py"
        Args = "auto-tagger.py --dir all --limit 50"
    }
)

# 注册任务
foreach ($task in $tasks) {
    Write-Host "📝 注册任务：$($task.Name)" -ForegroundColor Cyan
    
    # 检查任务是否已存在
    $existing = Get-ScheduledTask -TaskName $task.Name -ErrorAction SilentlyContinue
    
    if ($existing) {
        Write-Host "  ⚠️ 任务已存在，跳过" -ForegroundColor Yellow
        continue
    }
    
    # 创建触发器
    if ($task.DayOfWeek) {
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $task.DayOfWeek -At $task.Time
    } else {
        $trigger = New-ScheduledTaskTrigger -Daily -At $task.Time
    }
    
    # 创建操作
    $action = New-ScheduledTaskAction -Execute $task.Command -Argument $task.Args -WorkingDirectory "D:\OpenClaw\workspace\scripts"
    
    # 设置 Principal（使用当前用户）
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
    
    # 创建设置
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    
    # 注册任务
    try {
        Register-ScheduledTask -TaskName $task.Name `
            -Trigger $trigger `
            -Action $action `
            -Principal $principal `
            -Settings $settings `
            -Description $task.Description `
            -ErrorAction Stop
        
        Write-Host "  ✅ 任务注册成功" -ForegroundColor Green
        Write-Host "     触发器：$($task.DayOfWeek ? "$($task.DayOfWeek) $task.Time" : "每天 $task.Time")" -ForegroundColor Gray
    } catch {
        Write-Host "  ❌ 任务注册失败：$_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "查看已注册任务:" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTask | Where-Object {$_.TaskName -like 'OpenClaw*'}" -ForegroundColor Gray
Write-Host ""
Write-Host "删除所有任务:" -ForegroundColor Cyan
Write-Host "  .\setup-tasks.ps1 -Unregister" -ForegroundColor Gray
Write-Host ""
