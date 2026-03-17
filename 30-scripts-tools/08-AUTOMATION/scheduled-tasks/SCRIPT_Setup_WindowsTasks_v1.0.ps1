# OpenClaw Windows 定时任务配置脚本
# 资源占用最少方案

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "OpenClaw Windows 定时任务配置" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$principal = New-ScheduledTaskPrincipal -UserId "huawei" -LogonType Interactive -RunLevel Highest

# 1. arXiv 收集 (每日 2AM)
Write-Host "[1/6] 配置 arXiv 收集 (每日 2AM)..." -ForegroundColor Yellow
$action = New-ScheduledTaskAction -Execute "py" `
  -Argument "D:\npm-global\node_modules\openclaw\skills\arxiv-daily\scripts\arxiv-daily.py --categories cs.AI,cs.LG,cs.CL --output D:\OpenClaw\workspace\Medium\Raw\ --days 1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "OpenClaw-Arxiv-Collect" `
  -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
Write-Host "  ✅ 完成" -ForegroundColor Green

# 2. Medium 收集 (每日 4AM)
Write-Host "[2/6] 配置 Medium 收集 (每日 4AM)..." -ForegroundColor Yellow
$action = New-ScheduledTaskAction -Execute "py" `
  -Argument "D:\npm-global\node_modules\openclaw\skills\medium-watcher\scripts\medium-watcher.py --tags ai,llm,mcp --output D:\OpenClaw\workspace\Medium\Raw\ --min-score 3"
$trigger = New-ScheduledTaskTrigger -Daily -At 4am
Register-ScheduledTask -TaskName "OpenClaw-Medium-Watcher" `
  -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
Write-Host "  ✅ 完成" -ForegroundColor Green

# 3. Git 自动提交 (每 2 小时)
Write-Host "[3/6] 配置 Git 自动提交 (每 2 小时)..." -ForegroundColor Yellow
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"cd D:\obsidian\Vault; `$changed = git status --porcelain; if (`$changed) { git add -A; git commit -m `'[auto]'`; git push } else { Write-Host `'No changes`' }`""
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Hours 2) `
  -RepetitionDuration ([TimeSpan]::MaxValue)
Register-ScheduledTask -TaskName "OpenClaw-Git-AutoCommit" `
  -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
Write-Host "  ✅ 完成" -ForegroundColor Green

# 4. 文件归档 (每日 5AM)
Write-Host "[4/6] 配置文件归档 (每日 5AM)..." -ForegroundColor Yellow
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-Command `"Get-ChildItem -Path `'D:\OpenClaw\workspace\Medium\Raw`' -Filter *.md | Where-Object { `$_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Move-Item -Destination `'D:\OpenClaw\workspace\Medium\Archive`' -Force`""
$trigger = New-ScheduledTaskTrigger -Daily -At 5am
Register-ScheduledTask -TaskName "OpenClaw-File-Archive" `
  -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
Write-Host "  ✅ 完成" -ForegroundColor Green

# 5. 日志清理 (每日 0AM)
Write-Host "[5/6] 配置日志清理 (每日 0AM)..." -ForegroundColor Yellow
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-Command `"Get-ChildItem -Path `'D:\npm-global\node_modules\openclaw\tmp\openclaw`' -Filter *.log | Where-Object { `$_.LastWriteTime -lt (Get-Date).AddDays(-7) } | Remove-Item -Force`""
$trigger = New-ScheduledTaskTrigger -Daily -At 0am
Register-ScheduledTask -TaskName "OpenClaw-Log-Cleanup" `
  -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
Write-Host "  ✅ 完成" -ForegroundColor Green

# 6. 缓存清理 (每周日 6AM)
Write-Host "[6/6] 配置缓存清理 (每周日 6AM)..." -ForegroundColor Yellow
$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-Command `"Get-ChildItem -Path `'D:\OpenClaw\workspace`' -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 6am
Register-ScheduledTask -TaskName "OpenClaw-Cache-Cleanup" `
  -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
Write-Host "  ✅ 完成" -ForegroundColor Green

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "配置完成!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "已配置任务:" -ForegroundColor Yellow
Get-ScheduledTask -TaskName "OpenClaw-*" | Select-Object TaskName, State | Format-Table -AutoSize
Write-Host ""
Write-Host "提示:" -ForegroundColor Yellow
Write-Host "  - 查看任务：Get-ScheduledTask -TaskName `"OpenClaw-*`""
Write-Host "  - 删除任务：Unregister-ScheduledTask -TaskName '任务名' -Confirm:false"
Write-Host ""
