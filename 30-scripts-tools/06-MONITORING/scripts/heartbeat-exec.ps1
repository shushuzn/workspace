# Heartbeat 执行器 - 直接执行模式
# 用途：脚本决定下一步，AI 直接执行并输出结果

param([string]$Mode = "check")

$statePath = Join-Path $PSScriptRoot "..\13-memory\heartbeat-state.json"
$state = Get-Content $statePath | ConvertFrom-Json

# 检查锁
if ($state.heartbeatLock.acquired) {
    Write-Host "LOCKED"
    exit 1
}

# 获取锁
$state.heartbeatLock.acquired = $true
$state.heartbeatLock.acquiredAt = (Get-Date -Format "o")

# 判断下一步（只返回一个指令）
if ($state.currentArticle.status -eq "analyzing") {
    $action = "ANALYZE_CURRENT"
    $title = $state.currentArticle.title
    $id = $state.currentArticle.id
} elseif ($state.queue.Count -gt 0) {
    $action = "ANALYZE_NEXT"
    $title = $state.queue[0].title
    $id = $state.queue[0].id
    # 移动第一篇到 currentArticle
    $state.currentArticle = $state.queue[0]
    $state.currentArticle.status = "analyzing"
    $state.currentArticle.startedAt = (Get-Date -Format "o")
    $state.queue = $state.queue[1..($state.queue.Count-1)]
} elseif ($state.discovered.Count -gt 0) {
    $action = "SEARCH_NEW"
    $title = ""
    $id = ""
} else {
    $action = "NO_ACTION"
    $title = ""
    $id = ""
}

# 记录动作
$state.heartbeatLock.actionTaken = $action
$state | ConvertTo-Json -Depth 10 | Out-File $statePath -Encoding utf8

# 输出指令（AI 直接执行并输出实际结果）
Write-Host "ACTION=$action"
Write-Host "TITLE=$title"
Write-Host "ID=$id"
Write-Host ""
Write-Host "规则：直接执行，输出实际结果，不要只输出 CONTINUE:"
Write-Host "如有必要，在末尾附加 STATUS: RUNNING"
