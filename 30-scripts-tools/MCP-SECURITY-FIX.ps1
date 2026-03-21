# MCP Security Fix Script
# Must run as Administrator for system-wide variables, or User-level for current user

param(
    [string]$GitHubToken = "",
    [string]$YouTubeAPIKey = "",
    [switch]$UserLevel
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MCP Token Security Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ([string]::IsNullOrEmpty($GitHubToken)) {
    Write-Host "`n[1/2] GitHub Token: " -NoNewline -ForegroundColor Yellow
    $GitHubToken = Read-Host
}

if ([string]::IsNullOrEmpty($YouTubeAPIKey)) {
    Write-Host "[2/2] YouTube API Key: " -NoNewline -ForegroundColor Yellow
    $YouTubeAPIKey = Read-Host
}

$level = if ($UserLevel) { "User" } else { "Machine" }

Write-Host "`nSetting environment variables at $level level..." -ForegroundColor Gray

try {
    if (-not [string]::IsNullOrEmpty($GitHubToken)) {
        [System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", $GitHubToken, $level)
        Write-Host "[OK] GITHUB_TOKEN set" -ForegroundColor Green
    }

    if (-not [string]::IsNullOrEmpty($YouTubeAPIKey)) {
        [System.Environment]::SetEnvironmentVariable("YOUTUBE_API_KEY", $YouTubeAPIKey, $level)
        Write-Host "[OK] YOUTUBE_API_KEY set" -ForegroundColor Green
    }

    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Environment variables set successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Restart Trae CN to apply changes"
    Write-Host "2. Update mcp.json to use \`\${GITHUB_TOKEN}\` and \`\${YOUTUBE_API_KEY}\`"
    Write-Host "3. Test MCP servers in Trae CN"
    Write-Host "`nNote: Current session may need to restart PowerShell"
    Write-Host "      to see new environment variables."
}
catch {
    Write-Host "[ERROR] Failed to set environment variables: $_" -ForegroundColor Red
    Write-Host "Try running as Administrator" -ForegroundColor Yellow
}
