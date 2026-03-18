# Heartbeat 完成标记
# 用途：AI 完成动作后运行，更新状态 + 释放锁

param(
    [string]$Action,  # ANALYZE_CURRENT / ANALYZE_NEXT / SEARCH_NEW / NO_ACTION
    [string]$Result   # complete / failed / partial
)

$statePath = Join-Path $PSScriptRoot "..\13-memory\heartbeat-state.json"
$state = Get-Content $statePath | ConvertFrom-Json

if ($Result -eq "complete") {
    if ($Action -eq "ANALYZE_CURRENT" -or $Action -eq "ANALYZE_NEXT") {
        # 标记当前文章为完成
        $state.currentArticle.status = "complete"
        $state.currentArticle.completedAt = (Get-Date -Format "o")
        
        # 移到已完成列表
        $state.completed += @{
            title = $state.currentArticle.title
            id = $state.currentArticle.id
            completedAt = $state.currentArticle.completedAt
        }
        
        # 清空 currentArticle
        $state.currentArticle = $null
    }
}

# 释放锁
$state.heartbeatLock.acquired = $false
$state.heartbeatLock.releasedAt = (Get-Date -Format "o")
$state.heartbeatLock.actionTaken = $null

$state | ConvertTo-Json -Depth 10 | Out-File $statePath -Encoding utf8

Write-Host "OK: State updated, lock released"
