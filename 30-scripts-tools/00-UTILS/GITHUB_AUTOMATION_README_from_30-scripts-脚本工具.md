# GitHub Automation Tool

**通用 GitHub 自动化工具**

Date: 2026-03-07  
Author: Claw (@OpenClaw)  
Version: v0.1.0

---

## Overview

A universal GitHub automation tool for common GitHub operations:
- Pull Request creation
- Release creation
- Issue creation
- Branch management
- Tag management

**Efficiency Gain:** Automate repetitive GitHub tasks

---

## Requirements

- PowerShell 5.1+
- GitHub CLI (gh) - https://cli.github.com/

---

## Installation

```powershell
# No installation required
# Just clone or download the script
```

---

## Quick Start

### Help

```powershell
.\github_automation.ps1 -Help
```

### Create Pull Request

```powershell
.\github_automation.ps1 `
    -Action pr `
    -Repo crestalnetwork/intentkit `
    -Branch feature/belief-probe-integration `
    -Title "feat: Add belief probe early exit integration" `
    -Body "Description of changes" `
    -Base main
```

### Create Release

```powershell
.\github_automation.ps1 `
    -Action release `
    -Tag v1.0.0 `
    -Notes "Release notes here"
```

### Create Issue

```powershell
.\github_automation.ps1 `
    -Action issue `
    -Title "Bug: Something is wrong" `
    -Body "Description of the issue"
```

---

## Commands

### PR (Pull Request)

**Action:** `pr`

**Required:**
- `-Branch` - Source branch
- `-Title` - PR title

**Optional:**
- `-Body` - PR description
- `-Base` - Target branch (default: main)
- `-Repo` - Repository (default: current)

**Example:**
```powershell
.\github_automation.ps1 -Action pr -Branch feature/xxx -Title "feat: xxx"
```

---

### Release

**Action:** `release`

**Required:**
- `-Tag` - Release tag (e.g., v1.0.0)

**Optional:**
- `-Notes` - Release notes
- `-Repo` - Repository

**Example:**
```powershell
.\github_automation.ps1 -Action release -Tag v1.0.0 -Notes "Initial release"
```

---

### Issue

**Action:** `issue`

**Required:**
- `-Title` - Issue title

**Optional:**
- `-Body` - Issue description
- `-Repo` - Repository

**Example:**
```powershell
.\github_automation.ps1 -Action issue -Title "Bug: xxx" -Body "Description"
```

---

### Branch

**Action:** `branch`

**Required:**
- `-Branch` - Branch name

**Example:**
```powershell
.\github_automation.ps1 -Action branch -Branch feature/xxx
```

---

### Tag

**Action:** `tag`

**Required:**
- `-Tag` - Tag name

**Example:**
```powershell
.\github_automation.ps1 -Action tag -Tag v1.0.0
```

---

## Use Cases

### 1. PR Submission Workflow

```powershell
# 1. Create branch
.\github_automation.ps1 -Action branch -Branch feature/my-feature

# 2. Make changes...
# git add .
# git commit -m "feat: my feature"

# 3. Push and create PR
.\github_automation.ps1 `
    -Action pr `
    -Branch feature/my-feature `
    -Title "feat: Add my feature" `
    -Body "Description of changes"
```

---

### 2. Release Workflow

```powershell
# 1. Create tag
.\github_automation.ps1 -Action tag -Tag v1.0.0

# 2. Create release
.\github_automation.ps1 `
    -Action release `
    -Tag v1.0.0 `
    -Notes "## Changes`n- Feature 1`n- Feature 2"
```

---

### 3. Issue Template

```powershell
# Create bug report
.\github_automation.ps1 `
    -Action issue `
    -Title "Bug: Feature not working" `
    -Body @"
**Describe the bug**
Description here

**To Reproduce**
Steps to reproduce

**Expected behavior**
What should happen

**Environment:**
- OS: Windows
- Version: 1.0.0
"@
```

---

## Advanced Usage

### Batch PR Creation

```powershell
$branches = @("feature/1", "feature/2", "feature/3")

foreach ($branch in $branches) {
    .\github_automation.ps1 `
        -Action pr `
        -Branch $branch `
        -Title "feat: $branch"
}
```

### Automated Release

```powershell
$version = "1.0.0"
$changelog = Get-Content CHANGELOG.md -Raw

.\github_automation.ps1 `
    -Action release `
    -Tag "v$version" `
    -Notes $changelog
```

---

## Troubleshooting

### GitHub CLI Not Found

```
ERROR: GitHub CLI not found
```

**Solution:** Install from https://cli.github.com/

### Authentication Required

```
To get started, first login to github.com:
```

**Solution:** Run `gh auth login`

---

## License

MIT License

---

*Claw @ OpenClaw*
