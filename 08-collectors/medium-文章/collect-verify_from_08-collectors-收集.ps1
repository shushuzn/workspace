# Medium 收集 + 验证 一体化脚本
# POET-X 优化 #2: 任务合并 (5 步→2 步)

param([string]$Date = (Get-Date -Format "yyyy-MM-dd"))

Write-Host "Medium Collect + Verify: $Date" -ForegroundColor Cyan

$OutputDir = "D:\OpenClaw\workspace\41-medium\archive\$Date"
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# 模拟收集（实际应调用 Medium API）
$papers = @(
    @{Title="Example Paper 1"; Id="example-001"},
    @{Title="Example Paper 2"; Id="example-002"}
)

$validCount = 0
$invalidCount = 0

foreach ($paper in $papers) {
    $notePath = Join-Path $OutputDir "$($paper.Id).md"
    
    # 收集 + 验证 一体化
    if (Test-Path $notePath) {
        $content = Get-Content $notePath -Raw
        
        # 验证：检查 frontmatter 和正文
        $hasTitle = $content -match "^---[\s\S]*?title:"
        $hasBody = $content -match "## Core"
        
        if ($hasTitle -and $hasBody) {
            Write-Host "  [OK] $($paper.Title)" -ForegroundColor Green
            $validCount++
        } else {
            Write-Host "  [Invalid] $($paper.Title) - missing content" -ForegroundColor Yellow
            $invalidCount++
        }
    } else {
        Write-Host "  [Missing] $($paper.Title)" -ForegroundColor Red
        $invalidCount++
    }
}

Write-Host "Valid: $validCount, Invalid: $invalidCount" -ForegroundColor Green
