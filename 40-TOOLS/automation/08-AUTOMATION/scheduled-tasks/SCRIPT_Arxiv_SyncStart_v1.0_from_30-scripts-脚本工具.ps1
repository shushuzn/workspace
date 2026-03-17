# arxiv-sync 快速启动脚本
# 用法：.\arxiv-sync-start.ps1 [模式]

param(
    [ValidateSet("init", "daily", "weekly", "monthly", "full")]
    [string]$Mode = "daily",
    
    [switch]$DryRun
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SetupScript = Join-Path $ScriptDir "arxiv-sync-setup.ps1"

Write-Host "`n╔══════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  arxiv-sync 快速启动                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════╝" -ForegroundColor Cyan

if (!(Test-Path $SetupScript)) {
    Write-Host "✗ 错误：找不到 arxiv-sync-setup.ps1" -ForegroundColor Red
    Write-Host "  请确保两个脚本在同一目录" -ForegroundColor Gray
    exit 1
}

$commonArgs = @{
    "VaultPath" = "D:\obsidian\Vault"
    "SyncRoot" = "arxiv"
}

if ($DryRun) {
    $commonArgs["DryRun"] = $true
}

switch ($Mode) {
    "init" {
        Write-Host "模式：初始化完整结构" -ForegroundColor Yellow
        & $SetupScript @commonArgs -Init
    }
    
    "daily" {
        Write-Host "模式：创建今日目录" -ForegroundColor Yellow
        & $SetupScript @commonArgs -CreateDaily
    }
    
    "weekly" {
        Write-Host "模式：创建周汇总" -ForegroundColor Yellow
        & $SetupScript @commonArgs -CreateWeekly
    }
    
    "monthly" {
        Write-Host "模式：创建月汇总" -ForegroundColor Yellow
        & $SetupScript @commonArgs -CreateMonthly
    }
    
    "full" {
        Write-Host "模式：完整初始化 + 今日目录" -ForegroundColor Yellow
        & $SetupScript @commonArgs -Init -CreateDaily
    }
}

Write-Host "`n✓ 完成" -ForegroundColor Green
