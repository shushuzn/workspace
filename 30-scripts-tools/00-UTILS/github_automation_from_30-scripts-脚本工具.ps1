# GitHub Automation Tool
# 通用 GitHub 自动化工具
# Date: 2026-03-07
# Author: Claw (@OpenClaw)
# Version: v0.1.0

param(
    [Parameter(Mandatory=$false, Position=0)]
    [ValidateSet("pr", "release", "issue", "branch", "tag", "help")]
    [string]$Action = "help",
    
    [Parameter(Mandatory=$false)]
    [string]$Repo,
    
    [Parameter(Mandatory=$false)]
    [string]$Branch,
    
    [Parameter(Mandatory=$false)]
    [string]$Title,
    
    [Parameter(Mandatory=$false)]
    [string]$Body,
    
    [Parameter(Mandatory=$false)]
    [string]$Base = "main",
    
    [Parameter(Mandatory=$false)]
    [string]$Tag,
    
    [Parameter(Mandatory=$false)]
    [string]$Notes
)

# 帮助信息
function Show-Help {
    Write-Host "==============================================" -ForegroundColor Cyan
    Write-Host "GitHub Automation Tool v0.1.0" -ForegroundColor Cyan
    Write-Host "==============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\github_automation.ps1 -Action <action> [options]"
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Yellow
    Write-Host "  pr      - Create pull request"
    Write-Host "  release - Create release"
    Write-Host "  issue   - Create issue"
    Write-Host "  branch  - Create branch"
    Write-Host "  tag     - Create tag"
    Write-Host "  help    - Show this help"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  # Create PR"
    Write-Host "  .\github_automation.ps1 -Action pr -Repo org/repo -Branch feature/xxx -Title 'feat: xxx' -Body 'description'"
    Write-Host ""
    Write-Host "  # Create Release"
    Write-Host "  .\github_automation.ps1 -Action release -Tag v1.0.0 -Notes 'Release notes'"
    Write-Host ""
    Write-Host "  # Create Issue"
    Write-Host "  .\github_automation.ps1 -Action issue -Title 'Bug: xxx' -Body 'Description'"
    Write-Host ""
}

# 检查 GitHub CLI
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: GitHub CLI not found. Please install from https://cli.github.com/" -ForegroundColor Red
    exit 1
}

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "GitHub Automation Tool" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

if ($Action -eq "help") {
    Show-Help
    exit 0
}

switch ($Action) {
    "pr" {
        Write-Host "[Action] Create Pull Request" -ForegroundColor Yellow
        
        if (-not $Branch -or -not $Title) {
            Write-Host "ERROR: -Branch and -Title required for PR" -ForegroundColor Red
            exit 1
        }
        
        # 创建 PR
        $cmd = "gh pr create --title '$Title' --base '$Base' --head '$Branch'"
        
        if ($Body) {
            $cmd += " --body '$Body'"
        }
        
        if ($Repo) {
            $cmd += " --repo '$Repo'"
        }
        
        Write-Host "Running: $cmd" -ForegroundColor Gray
        Invoke-Expression $cmd
        
        Write-Host "✅ PR created!" -ForegroundColor Green
    }
    
    "release" {
        Write-Host "[Action] Create Release" -ForegroundColor Yellow
        
        if (-not $Tag) {
            Write-Host "ERROR: -Tag required for release" -ForegroundColor Red
            exit 1
        }
        
        $cmd = "gh release create '$Tag'"
        
        if ($Notes) {
            $cmd += " --notes '$Notes'"
        }
        
        if ($Repo) {
            $cmd += " --repo '$Repo'"
        }
        
        Write-Host "Running: $cmd" -ForegroundColor Gray
        Invoke-Expression $cmd
        
        Write-Host "✅ Release created!" -ForegroundColor Green
    }
    
    "issue" {
        Write-Host "[Action] Create Issue" -ForegroundColor Yellow
        
        if (-not $Title) {
            Write-Host "ERROR: -Title required for issue" -ForegroundColor Red
            exit 1
        }
        
        $cmd = "gh issue create --title '$Title'"
        
        if ($Body) {
            $cmd += " --body '$Body'"
        }
        
        if ($Repo) {
            $cmd += " --repo '$Repo'"
        }
        
        Write-Host "Running: $cmd" -ForegroundColor Gray
        Invoke-Expression $cmd
        
        Write-Host "✅ Issue created!" -ForegroundColor Green
    }
    
    "branch" {
        Write-Host "[Action] Create Branch" -ForegroundColor Yellow
        
        if (-not $Branch) {
            Write-Host "ERROR: -Branch required" -ForegroundColor Red
            exit 1
        }
        
        git checkout -b $Branch
        git push -u origin $Branch
        
        Write-Host "✅ Branch created and pushed!" -ForegroundColor Green
    }
    
    "tag" {
        Write-Host "[Action] Create Tag" -ForegroundColor Yellow
        
        if (-not $Tag) {
            Write-Host "ERROR: -Tag required" -ForegroundColor Red
            exit 1
        }
        
        git tag $Tag
        git push origin $Tag
        
        Write-Host "✅ Tag created and pushed!" -ForegroundColor Green
    }
    
    default {
        Write-Host "ERROR: Unknown action '$Action'" -ForegroundColor Red
        Show-Help
        exit 1
    }
}

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Complete!" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
