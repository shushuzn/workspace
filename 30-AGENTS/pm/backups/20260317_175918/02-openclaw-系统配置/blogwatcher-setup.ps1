# Setup blogwatcher with correct feed URLs

$blogwatcher = "$env:USERPROFILE\go\bin\blogwatcher.exe"

# Remove existing blogs
Write-Host "Removing old blogs..." -ForegroundColor Yellow
& $blogwatcher remove "Andrej Karpathy" 2>$null
& $blogwatcher remove "OpenAI Blog" 2>$null
& $blogwatcher remove "Anthropic" 2>$null

# Add with correct URLs
Write-Host "Adding blogs with correct URLs..." -ForegroundColor Yellow
& $blogwatcher add "Karpathy" "https://karpathy.ai/feed.xml"
& $blogwatcher add "OpenAI" "https://openai.com/blog/rss/"
& $blogwatcher add "Anthropic-News" "https://www.anthropic.com/news/rss"

# List blogs
Write-Host ""
Write-Host "Current blogs:" -ForegroundColor Cyan
& $blogwatcher blogs

# Scan
Write-Host ""
Write-Host "Scanning for updates..." -ForegroundColor Cyan
& $blogwatcher scan

# Show articles
Write-Host ""
Write-Host "Recent articles:" -ForegroundColor Cyan
& $blogwatcher articles

Write-Host ""
Write-Host "✅ blogwatcher setup complete!" -ForegroundColor Green
