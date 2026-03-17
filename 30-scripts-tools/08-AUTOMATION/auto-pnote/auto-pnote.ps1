# P-Note 自动化生成器 - PowerShell 包装脚本

param(
    [string]$PMID,
    [string]$ArXiv,
    [string]$PDF,
    [string]$OutputDir = "11-research/",
    [string]$Batch
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "auto-pnote\auto-pnote.py"

# 构建参数
$Args = @()
if ($PMID) { $Args += "--pmid", $PMID }
if ($ArXiv) { $Args += "--arxiv", $ArXiv }
if ($PDF) { $Args += "--pdf", $PDF }
if ($OutputDir) { $Args += "--output-dir", $OutputDir }
if ($Batch) { $Args += "--batch", $Batch }

# 执行 Python 脚本
Write-Host "🚀 启动 P-Note 自动化生成器..." -ForegroundColor Cyan
Write-Host "参数：$($Args -join ' ')" -ForegroundColor Gray
Write-Host ""

try {
    $Result = & python $PythonScript @Args 2>&1
    Write-Host $Result
    
    # 解析结果
    if ($Result -match '"status":\s*"success"') {
        Write-Host ""
        Write-Host "✅ P-Note 生成成功!" -ForegroundColor Green
        Write-Host "质量评分：$(if ($Result -match '"quality_score":\s*(\d+)') { $matches[1] } else { 'N/A' })"
        Write-Host "质量等级：$(if ($Result -match '"quality_level":\s*"([^"]+)"') { $matches[1] } else { 'N/A' })"
        Write-Host ""
        Write-Host "下一步:" -ForegroundColor Yellow
        Write-Host "1. 检查生成的 P-Note 文件"
        Write-Host "2. 进行质量审核 (如需要)"
        Write-Host "3. Git 提交"
    } else {
        Write-Host ""
        Write-Host "❌ P-Note 生成失败" -ForegroundColor Red
        Write-Host "错误信息：$Result"
    }
} catch {
    Write-Host "❌ 执行失败：$_" -ForegroundColor Red
}
