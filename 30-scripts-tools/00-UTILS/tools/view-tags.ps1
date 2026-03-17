#!/usr/bin/env pwsh
# 查看图形化标签树
# 用法：.\view-tags.ps1

$HtmlFile = "D:\OpenClaw\workspace\30-scripts\tag-tree.html"

if (Test-Path $HtmlFile) {
    Write-Host "打开标签树可视化页面..." -ForegroundColor Green
    Start-Process $HtmlFile
    Write-Host "页面已在浏览器中打开" -ForegroundColor Green
    Write-Host "`n功能:" -ForegroundColor Cyan
    Write-Host "  📁 点击父标签展开/收起子标签" -ForegroundColor White
    Write-Host "  🏷️  点击子标签查看相关图片" -ForegroundColor White
    Write-Host "  🔍 搜索框搜索标签或描述" -ForegroundColor White
    Write-Host "  📊 查看统计信息 (图片数/标签数)" -ForegroundColor White
} else {
    Write-Host "文件不存在：$HtmlFile" -ForegroundColor Red
}
