# Install Go Tools Automation Script

Write-Host "=== Installing blogwatcher ===" -ForegroundColor Cyan

# Check if Go is installed
Write-Host "Checking Go..." -ForegroundColor Yellow
$goVersion = go version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Go not found! Please install from: https://go.dev/dl/" -ForegroundColor Red
    exit 1
}
Write-Host "Go installed: $goVersion" -ForegroundColor Green

# Install blogwatcher
Write-Host "Installing blogwatcher..." -ForegroundColor Yellow
go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest

# Verify
Write-Host "Verifying blogwatcher..." -ForegroundColor Yellow
blogwatcher --version

# Add subscriptions
Write-Host "Adding blog subscriptions..." -ForegroundColor Yellow
blogwatcher add "Andrej Karpathy" https://karpathy.ai/feed.xml
blogwatcher add "OpenAI Blog" https://openai.com/blog/rss/
blogwatcher add "Anthropic" https://www.anthropic.com/news/rss

# Test scan
Write-Host "Testing scan..." -ForegroundColor Yellow
blogwatcher scan

Write-Host "=== Installation Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Configure Google API Key for summarize" -ForegroundColor White
Write-Host "2. Download summarize from: https://github.com/steipete/summarize/releases" -ForegroundColor White
Write-Host "3. Add to PATH: $env:USERPROFILE\bin" -ForegroundColor White
