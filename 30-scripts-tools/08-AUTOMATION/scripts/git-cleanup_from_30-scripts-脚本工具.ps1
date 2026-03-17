# Git 仓库清理脚本
# 定期运行以清理临时文件和大文件

param(
    [switch]$DryRun,
    [switch]$Verbose
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Git 仓库清理脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$Stats = @{
    FilesDeleted = 0
    SpaceFreed = 0
    DirectoriesCleaned = 0
}

# 1. 清理 Python 缓存
Write-Host "[1/6] 清理 Python 缓存..." -ForegroundColor Yellow
$pycache = Get-ChildItem -Recurse -Directory -Force | Where-Object { $_.Name -eq '__pycache__' }
foreach ($dir in $pycache) {
    if ($DryRun) {
        Write-Host "  [DRY RUN] Would delete: $($dir.FullName)" -ForegroundColor Gray
    } else {
        Remove-Item $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
        if ($Verbose) { Write-Host "  Deleted: $($dir.FullName)" -ForegroundColor Green }
    }
    $Stats.FilesDeleted++
}

# 2. 清理临时文件
Write-Host "[2/6] 清理临时文件..." -ForegroundColor Yellow
$tempPatterns = @('*.pyc', '*.pyo', '*.pyd', '*.so', '*.egg', '*~', '*.swp', '*.swo')
foreach ($pattern in $tempPatterns) {
    $files = Get-ChildItem -Recurse -Filter $pattern -Force -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete: $($file.FullName)" -ForegroundColor Gray
        } else {
            Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
            if ($Verbose) { Write-Host "  Deleted: $($file.FullName)" -ForegroundColor Green }
        }
        $Stats.FilesDeleted++
    }
}

# 3. 清理构建目录
Write-Host "[3/6] 清理构建目录..." -ForegroundColor Yellow
$buildDirs = @('dist', 'build', '.eggs')
foreach ($dirName in $buildDirs) {
    $dirs = Get-ChildItem -Recurse -Directory -Force | Where-Object { $_.Name -eq $dirName }
    foreach ($dir in $dirs) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete: $($dir.FullName)" -ForegroundColor Gray
        } else {
            Remove-Item $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
            if ($Verbose) { Write-Host "  Deleted: $($dir.FullName)" -ForegroundColor Green }
        }
        $Stats.DirectoriesCleaned++
    }
}

# 4. 清理日志文件
Write-Host "[4/6] 清理日志文件..." -ForegroundColor Yellow
$logFiles = Get-ChildItem -Recurse -Filter '*.log' -Force -ErrorAction SilentlyContinue
foreach ($file in $logFiles) {
    if ($file.Length -gt 10MB) {
        if ($DryRun) {
            Write-Host "  [DRY RUN] Would delete: $($file.FullName) ($([math]::Round($file.Length/1MB, 2)) MB)" -ForegroundColor Gray
        } else {
            Remove-Item $file.FullName -Force -ErrorAction SilentlyContinue
            if ($Verbose) { Write-Host "  Deleted: $($file.FullName)" -ForegroundColor Green }
        }
        $Stats.FilesDeleted++
        $Stats.SpaceFreed += $file.Length
    }
}

# 5. 查找大文件 (>50MB)
Write-Host "[5/6] 查找大文件 (>50MB)..." -ForegroundColor Yellow
$largeFiles = Get-ChildItem -Recurse -File | Where-Object { $_.Length -gt 50MB } | Sort-Object Length -Descending
if ($largeFiles.Count -gt 0) {
    Write-Host "  发现 $($largeFiles.Count) 个大文件:" -ForegroundColor Yellow
    foreach ($file in $largeFiles | Select-Object -First 10) {
        Write-Host "    $($file.FullName) ($([math]::Round($file.Length/1MB, 2)) MB)" -ForegroundColor Red
    }
    if ($largeFiles.Count -gt 10) {
        Write-Host "    ... 还有 $($largeFiles.Count - 10) 个文件" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  建议：使用 Git LFS 管理这些文件" -ForegroundColor Cyan
} else {
    Write-Host "  ✓ 未发现 >50MB 的大文件" -ForegroundColor Green
}

# 6. Git 垃圾回收
Write-Host "[6/6] Git 垃圾回收..." -ForegroundColor Yellow
if ($DryRun) {
    Write-Host "  [DRY RUN] Would run: git gc --prune=now" -ForegroundColor Gray
} else {
    git gc --prune=now 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
}

# 统计
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "清理完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  删除文件数：$($Stats.FilesDeleted)" -ForegroundColor White
Write-Host "  清理目录数：$($Stats.DirectoriesCleaned)" -ForegroundColor White
Write-Host "  释放空间：$([math]::Round($Stats.SpaceFreed/1MB, 2)) MB" -ForegroundColor White
Write-Host ""

if (-not $DryRun) {
    Write-Host "下一步:" -ForegroundColor Yellow
    Write-Host "  1. git add -A" -ForegroundColor White
    Write-Host "  2. git commit -m 'chore: cleanup temporary files'" -ForegroundColor White
    Write-Host "  3. git push origin master" -ForegroundColor White
}
