# OpenClaw System Health Check Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OpenClaw System Health Check" -ForegroundColor Cyan
Write-Host "  Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Disk Space
Write-Host "[1/6] Checking disk space..." -ForegroundColor Yellow
$disk = Get-PSDrive C
$usage = [math]::Round($disk.Used / ($disk.Used + $disk.Free) * 100, 1)
if ($usage -gt 90) {
    Write-Host "  [!] WARNING: C: drive usage $usage%" -ForegroundColor Red
} elseif ($usage -gt 85) {
    Write-Host "  [!] CAUTION: C: drive usage $usage%" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] C: drive usage: $usage%" -ForegroundColor Green
}
Write-Host ""

# 2. Scheduled Tasks
Write-Host "[2/6] Checking scheduled tasks..." -ForegroundColor Yellow
$tasks = @("arxiv-collector", "batch-processor", "nightly-security-audit", "medium-watcher", "memory-distiller", "github-sync", "citation-tracker")
foreach ($task in $tasks) {
    $result = schtasks /query /tn $task 2>&1
    if ($result -match "Ready") {
        Write-Host "  [OK] $task" -ForegroundColor Green
    } else {
        Write-Host "  [!] $task (not found)" -ForegroundColor Red
    }
}
Write-Host ""

# 3. Git Status
Write-Host "[3/6] Checking Git status..." -ForegroundColor Yellow
Set-Location "D:\OpenClaw\workspace"
$gitStatus = git status --porcelain 2>&1
if ([string]::IsNullOrWhiteSpace($gitStatus)) {
    Write-Host "  [OK] Git working tree clean" -ForegroundColor Green
} else {
    $lines = ($gitStatus -split "`n").Count
    Write-Host "  [!] $lines uncommitted changes" -ForegroundColor Yellow
}
Write-Host ""

# 4. Memory Files
Write-Host "[4/6] Checking memory files..." -ForegroundColor Yellow
$memoryFiles = Get-ChildItem "D:\OpenClaw\workspace\memory" -Filter "*.md" | Where-Object { $_.LastWriteTime -gt (Get-Date).AddDays(-2) }
Write-Host "  [OK] Files updated in 2 days: $($memoryFiles.Count)" -ForegroundColor Green
Write-Host ""

# 5. Skills Directory
Write-Host "[5/6] Checking skills directory..." -ForegroundColor Yellow
$skillPath = "D:\npm-global\node_modules\openclaw\skills"
if (Test-Path $skillPath) {
    $skillCount = (Get-ChildItem $skillPath -Directory).Count
    Write-Host "  [OK] Skills count: $skillCount" -ForegroundColor Green
} else {
    Write-Host "  [!] Skills directory not found" -ForegroundColor Red
}
Write-Host ""

# 6. Logs Directory
Write-Host "[6/6] Checking logs directory..." -ForegroundColor Yellow
$logPath = "D:\OpenClaw\workspace\logs\tasks"
if (Test-Path $logPath) {
    Write-Host "  [OK] Logs directory exists" -ForegroundColor Green
} else {
    Write-Host "  [!] Logs directory not created" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Health Check Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
