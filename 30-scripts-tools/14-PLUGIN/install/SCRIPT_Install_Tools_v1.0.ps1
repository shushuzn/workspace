# 自动化安装脚本 - Go + blogwatcher + summarize

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  自动化安装 Go + blogwatcher + summarize" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 Go 是否已安装
Write-Host "[1/6] 检查 Go 安装状态..." -ForegroundColor Yellow
try {
    $goVersion = go version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Go 已安装：$goVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Go 未安装" -ForegroundColor Red
        Write-Host ""
        Write-Host "请手动安装 Go:" -ForegroundColor Yellow
        Write-Host "1. 访问：https://go.dev/dl/" -ForegroundColor White
        Write-Host "2. 下载并运行：go-1.22.x.windows-amd64.msi" -ForegroundColor White
        Write-Host "3. 安装完成后重新运行此脚本" -ForegroundColor White
        Write-Host ""
        Write-Host "按任意键继续..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
} catch {
    Write-Host "❌ Go 未安装，请先安装 Go" -ForegroundColor Red
    exit 1
}

# 2. 安装 blogwatcher
Write-Host ""
Write-Host "[2/6] 安装 blogwatcher..." -ForegroundColor Yellow
go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ blogwatcher 安装成功" -ForegroundColor Green
} else {
    Write-Host "❌ blogwatcher 安装失败" -ForegroundColor Red
    Write-Host "尝试手动设置 GOPATH..." -ForegroundColor Yellow
    $env:GOPATH = "$env:USERPROFILE\go"
    $env:Path += ";$env:GOPATH\bin"
    go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest
}

# 3. 验证 blogwatcher
Write-Host ""
Write-Host "[3/6] 验证 blogwatcher..." -ForegroundColor Yellow
try {
    $blogwatcherVersion = blogwatcher --version 2>&1
    Write-Host "✅ blogwatcher 已安装" -ForegroundColor Green
} catch {
    Write-Host "❌ blogwatcher 未找到，可能在 GOPATH\bin" -ForegroundColor Yellow
    Write-Host "请确保 `$env:GOPATH\bin 已添加到 PATH" -ForegroundColor Yellow
}

# 4. 初始化 blogwatcher 订阅源
Write-Host ""
Write-Host "[4/6] 初始化 blogwatcher 订阅源..." -ForegroundColor Yellow
blogwatcher add "Andrej Karpathy" https://karpathy.ai/feed.xml 2>&1 | Out-Null
blogwatcher add "Simon Willison" https://simonwillison.net/atom/everything/ 2>&1 | Out-Null
blogwatcher add "OpenAI Blog" https://openai.com/blog/rss/ 2>&1 | Out-Null
blogwatcher add "Anthropic" https://www.anthropic.com/news/rss 2>&1 | Out-Null
Write-Host "✅ 已添加 4 个订阅源" -ForegroundColor Green

# 5. 测试 blogwatcher 扫描
Write-Host ""
Write-Host "[5/6] 测试 blogwatcher 扫描..." -ForegroundColor Yellow
Write-Host "(首次扫描可能需要几分钟)" -ForegroundColor Gray
blogwatcher scan
Write-Host "✅ blogwatcher 扫描完成" -ForegroundColor Green

# 6. summarize 安装指引
Write-Host ""
Write-Host "[6/6] summarize 安装指引..." -ForegroundColor Yellow
Write-Host ""
Write-Host "summarize 需要手动下载:" -ForegroundColor Cyan
Write-Host "1. 访问：https://github.com/steipete/summarize/releases" -ForegroundColor White
Write-Host "2. 下载最新的 summarize-windows-amd64.exe" -ForegroundColor White
Write-Host "3. 重命名为 summarize.exe 并放到:" -ForegroundColor White
Write-Host "   $env:USERPROFILE\bin\summarize.exe" -ForegroundColor Gray
Write-Host ""
Write-Host "或者运行以下命令自动下载:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  New-Item -ItemType Directory -Force -Path `"$env:USERPROFILE\bin`"" -ForegroundColor Gray
Write-Host "  Invoke-WebRequest -Uri `"https://github.com/steipete/summarize/releases/latest/download/summarize-windows-amd64.exe`" -OutFile `"$env:USERPROFILE\bin\summarize.exe`"" -ForegroundColor Gray
Write-Host "  `$env:Path += `";$env:USERPROFILE\bin`"" -ForegroundColor Gray
Write-Host "  [Environment]::SetEnvironmentVariable(`"Path`", `$env:Path, `"User`")" -ForegroundColor Gray
Write-Host ""

# 询问是否自动下载 summarize
Write-Host "是否自动下载 summarize? (Y/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host "正在下载 summarize..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\bin" | Out-Null
    try {
        Invoke-WebRequest -Uri "https://github.com/steipete/summarize/releases/latest/download/summarize-windows-amd64.exe" -OutFile "$env:USERPROFILE\bin\summarize.exe" -UseBasicParsing
        Write-Host "✅ summarize 下载成功" -ForegroundColor Green
        
        # 添加到 PATH
        $env:Path += ";$env:USERPROFILE\bin"
        [Environment]::SetEnvironmentVariable("Path", $env:Path, "User")
        Write-Host "✅ 已添加到 PATH" -ForegroundColor Green
        Write-Host "⚠️  请关闭并重新打开 PowerShell 以应用 PATH 更改" -ForegroundColor Yellow
    } catch {
        Write-Host "❌ 下载失败，请手动下载" -ForegroundColor Red
        Write-Host "错误：$_" -ForegroundColor Red
    }
}

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  安装完成!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "下一步:" -ForegroundColor Yellow
Write-Host "1. 配置 Google API Key:" -ForegroundColor White
Write-Host "   [Environment]::SetEnvironmentVariable(`"GOOGLE_API_KEY`", `"你的 API Key`", `"User`")" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 获取 API Key: https://makersuite.google.com/app/apikey" -ForegroundColor White
Write-Host ""
Write-Host "3. 测试 summarize (重新打开 PowerShell 后):" -ForegroundColor White
Write-Host "   summarize `"https://karpathy.ai/`" --model google/gemini-3-flash-preview" -ForegroundColor Gray
Write-Host ""
Write-Host "4. 查看 blogwatcher 文章:" -ForegroundColor White
Write-Host "   blogwatcher articles" -ForegroundColor Gray
Write-Host ""
