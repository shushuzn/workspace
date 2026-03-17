# 运行 GP 模型重训练脚本
Write-Host "GP 模型重训练 - 200 样本" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$scriptPath = "scripts\gp_retrain_200samples.py"
$content = Get-Content $scriptPath -Raw -Encoding utf8

# 替换路径
$content = $content -replace 'research/data/', 'data/'

# 保存到临时文件
$tempScript = "scripts\gp_retrain_200samples_temp.py"
Set-Content -Path $tempScript -Value $content -Encoding utf8

# 运行
Write-Host "运行脚本..." -ForegroundColor Yellow
py $tempScript

# 清理
Remove-Item $tempScript -Force

Write-Host "完成!" -ForegroundColor Green
