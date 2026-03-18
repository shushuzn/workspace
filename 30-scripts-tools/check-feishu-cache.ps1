# 飞书缓存清理工具

Write-Host "============================================================"
Write-Host "  飞书 (Feishu/Lark) 缓存清理工具"
Write-Host "============================================================"
Write-Host ""

$paths = @(
    "C:\Users\$env:USERNAME\AppData\Roaming\Lark",
    "C:\Users\$env:USERNAME\AppData\Local\Lark",
    "C:\Users\$env:USERNAME\AppData\Roaming\feishu",
    "C:\Users\$env:USERNAME\AppData\Local\feishu"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -File | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        Write-Host "[FOUND] $path"
        Write-Host "        Size: $sizeMB MB"
        Write-Host ""
    }
}

Write-Host "============================================================"
Write-Host "  常见缓存位置:"
Write-Host "============================================================"
Write-Host "  1. 文件缓存：AppData\Roaming\Lark\Cache"
Write-Host "  2. 日志文件：AppData\Roaming\Lark\logs"
Write-Host "  3. 临时文件：AppData\Local\Temp\Lark*"
Write-Host ""
Write-Host "  建议清理:"
Write-Host "  - Cache 文件夹 (可安全删除)"
Write-Host "  - logs 文件夹 (保留最近 7 天)"
Write-Host "  - Temp 文件 (可安全删除)"
Write-Host "============================================================"
