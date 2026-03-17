# Heartbeat Trigger Script
# 每 30 分钟触发一次 heartbeat 检查

$workspace = "D:\OpenClaw\workspace"
$logFile = "$workspace\91-logs-日志\heartbeat-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"

try {
    # 记录触发时间
    "$(Get-Date -Format 'o') - Heartbeat triggered" | Out-File $logFile -Append
    
    # 检查是否有未完成的任务
    $heartbeatState = Get-Content "$workspace\13-memory-记忆系统\heartbeat-state.json" -Raw | ConvertFrom-Json
    
    # 如果有 pending 任务，记录状态
    $pendingCount = ($heartbeatState.todo | Where-Object { $_.status -eq 'pending' }).Count
    "$(Get-Date -Format 'o') - Pending tasks: $pendingCount" | Out-File $logFile -Append
    
    Write-Host "Heartbeat check completed - $pendingCount pending tasks" -ForegroundColor Green
}
catch {
    "$(Get-Date -Format 'o') - ERROR: $_" | Out-File $logFile -Append
    Write-Host "Heartbeat check failed: $_" -ForegroundColor Red
}
