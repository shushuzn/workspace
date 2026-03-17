# Medium 目录清理脚本 - 阶段 1
# 执行时间：2026-03-03
# 功能：归档待分析的 RSS 空壳文件

$ErrorActionPreference = "Stop"
$sourcePath = "D:\obsidian\Vault\Medium"
$archivePath = "D:\obsidian\Vault\Medium\archive\2026-03"

Write-Host "=== Medium 目录清理脚本 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 统计当前状态
Write-Host "[1/4] 统计当前文件..." -ForegroundColor Yellow
$allFiles = Get-ChildItem -Path $sourcePath -File
$pendingFiles = Get-ChildItem -Path $sourcePath -Filter "20260302-*.md" | Where-Object { $_.Length -lt 350 }
$pnoteFiles = Get-ChildItem -Path $sourcePath -Filter "P-*.md"
$analyzedFiles = Get-ChildItem -Path $sourcePath -Filter "2026-*.md"

Write-Host "  总文件数：$($allFiles.Count)" -ForegroundColor Gray
Write-Host "  待分析空壳文件：$($pendingFiles.Count)" -ForegroundColor Gray
Write-Host "  P-Note 论文解析：$($pnoteFiles.Count)" -ForegroundColor Gray
Write-Host "  已分析文章：$($analyzedFiles.Count)" -ForegroundColor Gray
Write-Host ""

# 2. 创建归档目录
Write-Host "[2/4] 创建归档目录..." -ForegroundColor Yellow
if (!(Test-Path $archivePath)) {
    New-Item -Path $archivePath -ItemType Directory -Force | Out-Null
    Write-Host "  已创建：$archivePath" -ForegroundColor Green
} else {
    Write-Host "  目录已存在：$archivePath" -ForegroundColor Gray
}
Write-Host ""

# 3. 移动文件
Write-Host "[3/4] 移动待分析文件到归档..." -ForegroundColor Yellow
if ($pendingFiles.Count -gt 0) {
    $movedCount = 0
    foreach ($file in $pendingFiles) {
        Move-Item -Path $file.FullName -Destination $archivePath -Force
        $movedCount++
    }
    Write-Host "  已移动：$movedCount 个文件" -ForegroundColor Green
} else {
    Write-Host "  无待移动文件" -ForegroundColor Gray
}
Write-Host ""

# 4. 验证结果
Write-Host "[4/4] 验证清理结果..." -ForegroundColor Yellow
$remainingFiles = Get-ChildItem -Path $sourcePath -File
$archivedFiles = Get-ChildItem -Path $archivePath -File

Write-Host "  主目录剩余文件：$($remainingFiles.Count)" -ForegroundColor Green
Write-Host "  归档目录文件：$($archivedFiles.Count)" -ForegroundColor Green
Write-Host ""

# 5. 显示主目录剩余文件
Write-Host "=== 主目录剩余文件 ===" -ForegroundColor Cyan
$remainingFiles | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize

Write-Host ""
Write-Host "=== 清理完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "回滚命令 (如需恢复):" -ForegroundColor Yellow
Write-Host "  Move-Item archivePath\*.md sourcePath" -ForegroundColor Gray
Write-Host ""
