# 数据收集脚本 - 一键运行所有收集任务

Set-Location "D:\OpenClaw\workspace\scripts"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  数据收集脚本 - 一键运行" -ForegroundColor Cyan
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0

# 1. X/Twitter 监听
Write-Host "📱 收集 X/Twitter..." -ForegroundColor Cyan
try {
    py x-twitter-monitor.py
    Write-Host "✅ X/Twitter 完成" -ForegroundColor Green
} catch {
    Write-Host "❌ X/Twitter 失败：$_" -ForegroundColor Red
    $ErrorCount++
}
Write-Host ""

# 2. Reddit 监控
Write-Host "📢 收集 Reddit..." -ForegroundColor Cyan
try {
    py reddit-monitor.py
    Write-Host "✅ Reddit 完成" -ForegroundColor Green
} catch {
    Write-Host "❌ Reddit 失败：$_" -ForegroundColor Red
    $ErrorCount++
}
Write-Host ""

# 3. HackerNews 收集
Write-Host "📰 收集 HackerNews..." -ForegroundColor Cyan
try {
    py hackernews-collector.py
    Write-Host "✅ HackerNews 完成" -ForegroundColor Green
} catch {
    Write-Host "❌ HackerNews 失败：$_" -ForegroundColor Red
    $ErrorCount++
}
Write-Host ""

# 4. Medium 收集
Write-Host "📝 收集 Medium..." -ForegroundColor Cyan
try {
    py medium-rss-collector-jina.py
    Write-Host "✅ Medium 完成" -ForegroundColor Green
} catch {
    Write-Host "❌ Medium 失败：$_" -ForegroundColor Red
    $ErrorCount++
}
Write-Host ""

# 5. 生成周报
Write-Host "📊 生成周报..." -ForegroundColor Cyan
try {
    py report-generator.py weekly
    Write-Host "✅ 报告生成完成" -ForegroundColor Green
} catch {
    Write-Host "❌ 报告生成失败：$_" -ForegroundColor Red
    $ErrorCount++
}
Write-Host ""

# 总结
Write-Host "========================================" -ForegroundColor Cyan
if ($ErrorCount -eq 0) {
    Write-Host "  ✅ 全部完成！" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ 完成，$ErrorCount 个任务失败" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
