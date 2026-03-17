#!/usr/bin/env pwsh
# 快速文件搜索
# 用法：.\search.ps1 -Keyword "关键词" [-Type "MAT_PAP"]

param(
    [string]$Keyword,
    [string]$Type,
    [string]$Path = "D:\OpenClaw\workspace"
)

if (-not $Keyword) {
    Write-Host "用法：.\search.ps1 -Keyword `"关键词`" [-Type `"MAT_PAP`"]" -ForegroundColor Yellow
    exit
}

$Filter = if ($Type) { "${Type}_*.md" } else { "*.md" }

Write-Host "搜索：$Keyword (类型：$Filter)" -ForegroundColor Cyan
$results = Select-String -Path $Path -Filter $Filter -Pattern $Keyword -Recurse -ErrorAction SilentlyContinue

if ($results) {
    Write-Host "找到 $($results.Count) 个结果:" -ForegroundColor Green
    $results | Select-Object -First 20 | ForEach-Object {
        Write-Host "  $($_.Path):$($_.LineNumber)" -ForegroundColor White
    }
    if ($results.Count -gt 20) {
        Write-Host "  ... 还有 $($results.Count - 20) 个结果" -ForegroundColor Gray
    }
} else {
    Write-Host "未找到结果" -ForegroundColor Yellow
}
