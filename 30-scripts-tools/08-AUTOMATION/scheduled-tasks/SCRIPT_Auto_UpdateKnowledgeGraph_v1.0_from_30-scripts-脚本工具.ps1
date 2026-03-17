# 知识图谱自动更新脚本
# 每日 6AM 执行

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "知识图谱自动更新" -ForegroundColor Cyan
Write-Host "执行时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 1. 构建知识图谱
Write-Host "[1/5] 构建知识图谱..." -ForegroundColor Yellow
py D:\npm-global\node_modules\openclaw\skills\knowledge-graph\scripts\kg-builder.py `
  --input D:\OpenClaw\workspace\memory `
  --input D:\OpenClaw\workspace\Medium `
  --output D:\OpenClaw\workspace\knowledge-graph\auto\graph `
  --format all

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 完成" -ForegroundColor Green
} else {
    Write-Host "  ✗ 失败" -ForegroundColor Red
}
Write-Host ""

# 2. 提取摘要
Write-Host "[2/5] 提取论文摘要..." -ForegroundColor Yellow
py D:\OpenClaw\workspace\knowledge-graph\extract-summaries.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 完成" -ForegroundColor Green
} else {
    Write-Host "  ✗ 失败" -ForegroundColor Red
}
Write-Host ""

# 3. 增强关系
Write-Host "[3/5] 增强关系..." -ForegroundColor Yellow
py D:\OpenClaw\workspace\knowledge-graph\enhance-relations.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 完成" -ForegroundColor Green
} else {
    Write-Host "  ✗ 失败" -ForegroundColor Red
}
Write-Host ""

# 4. 合并图谱
Write-Host "[4/5] 合并增强图谱..." -ForegroundColor Yellow
py D:\OpenClaw\workspace\knowledge-graph\merge-and-enhance.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ 完成" -ForegroundColor Green
} else {
    Write-Host "  ✗ 失败" -ForegroundColor Red
}
Write-Host ""

# 5. Git 提交
Write-Host "[5/5] Git 提交..." -ForegroundColor Yellow
cd D:\obsidian\Vault
$changes = git status --porcelain

if ($changes) {
    git add knowledge-graph/
    git commit -m "[auto] 知识图谱更新 $(Get-Date -Format 'yyyy-MM-dd')"
    git push
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ 已提交并推送" -ForegroundColor Green
    } else {
        Write-Host "  ✗ 推送失败" -ForegroundColor Red
    }
} else {
    Write-Host "  ℹ 无变更，跳过提交" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "知识图谱更新完成！" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
