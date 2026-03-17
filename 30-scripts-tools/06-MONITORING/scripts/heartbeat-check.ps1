# Heartbeat 执行前检查脚本
# 用途：确保每次 heartbeat 只执行一个动作

param([switch]$AcquireLock, [switch]$ReleaseLock)

$statePath = Join-Path $PSScriptRoot "..\13-memory\heartbeat-state.json"
$state = Get-Content $statePath | ConvertFrom-Json

if ($AcquireLock) {
    if ($state.heartbeatLock.acquired) {
        Write-Host "[ERROR] 锁已被占用 - 上次 action: $($state.heartbeatLock.actionTaken)" -ForegroundColor Red
        Write-Host "[ERROR] 请先释放锁再继续" -ForegroundColor Red
        exit 1
    }
    $state.heartbeatLock.acquired = $true
    $state.heartbeatLock.acquiredAt = (Get-Date -Format "o")
    $state | ConvertTo-Json -Depth 10 | Out-File $statePath -Encoding utf8
    Write-Host "[OK] 锁已获取 - 可以执行本次 heartbeat" -ForegroundColor Green
    exit 0
}

if ($ReleaseLock) {
    $state.heartbeatLock.acquired = $false
    $state.heartbeatLock.releasedAt = (Get-Date -Format "o")
    $state | ConvertTo-Json -Depth 10 | Out-File $statePath -Encoding utf8
    Write-Host "[OK] 锁已释放 - 等待下次 heartbeat 触发" -ForegroundColor Green
    exit 0
}

# 默认：检查状态
Write-Host "=== Heartbeat 状态检查 ===" -ForegroundColor Cyan
Write-Host "当前文章：$($state.currentArticle.title)" -ForegroundColor Yellow
Write-Host "状态：$($state.currentArticle.status)" -ForegroundColor Yellow
Write-Host "队列：$($state.queue.Count) 篇" -ForegroundColor Yellow
Write-Host "已完成：$($state.completed.Count) 篇" -ForegroundColor Yellow
Write-Host "锁状态：$(if ($state.heartbeatLock.acquired) { '已锁定' } else { '未锁定' })" -ForegroundColor Yellow
Write-Host ""

if ($state.currentArticle.status -eq "analyzing") {
    Write-Host "下一步：CONTINUE: analyze current article" -ForegroundColor Green
} elseif ($state.queue.Count -gt 0) {
    Write-Host "下一步：CONTINUE: analyze next queued article" -ForegroundColor Green
} elseif ($state.discovered.Count -gt 0) {
    Write-Host "下一步：CONTINUE: search for new articles" -ForegroundColor Green
} else {
    Write-Host "下一步：NO_ACTION" -ForegroundColor Green
}
