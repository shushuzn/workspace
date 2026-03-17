# AI Research OS - 命令行工具封装

**版本:** v1.0  
**创建时间:** 2026-03-05 12:38  
**用途:** 简化常用命令

---

## 📦 安装

将以下脚本保存为 `D:\OpenClaw\workspace\ai-research.ps1`

---

## 🚀 使用方式

### 1. 信息收集

```powershell
# 收集 arXiv 论文
.\ai-research.ps1 collect arxiv

# 收集 Twitter
.\ai-research.ps1 collect twitter

# 收集所有源
.\ai-research.ps1 collect all
```

### 2. 数据处理

```powershell
# 下载 PDF
.\ai-research.ps1 process pdf

# 填充 P-Note
.\ai-research.ps1 process pnote
```

### 3. AI 分析

```powershell
# 论文评分
.\ai-research.ps1 analyze score

# 趋势预测
.\ai-research.ps1 analyze trend

# 合作者推荐
.\ai-research.ps1 analyze collab
```

### 4. 系统工具

```powershell
# 系统监控
.\ai-research.ps1 system monitor

# 质量检查
.\ai-research.ps1 system quality

# 性能优化
.\ai-research.ps1 system optimize

# 生成报告
.\ai-research.ps1 system report
```

### 5. 快捷命令

```powershell
# 查看今日状态
.\ai-research.ps1 status

# 查看帮助
.\ai-research.ps1 help
```

---

## 📝 脚本内容

```powershell
#!/usr/bin/env pwsh
# AI Research OS 命令行工具

param(
    [Parameter(Position=0)]
    [string]$Command = "help",
    
    [Parameter(Position=1)]
    [string]$SubCommand = ""
)

$SCRIPT_DIR = Split-Path $MyInvocation.MyCommand.Path
Set-Location $SCRIPT_DIR

switch ($Command) {
    "collect" {
        switch ($SubCommand) {
            "arxiv" { python scripts/arxiv-collector-v2.py }
            "twitter" { python scripts/twitter-watcher.py }
            "hn" { python scripts/hn-watcher.py }
            "reddit" { python scripts/reddit-watcher-mock.py }
            "all" {
                python scripts/arxiv-collector-v2.py
                python scripts/twitter-watcher.py
                python scripts/hn-watcher.py
                python scripts/reddit-watcher-mock.py
            }
        }
    }
    "process" {
        switch ($SubCommand) {
            "pdf" { python scripts/pdf-downloader.py }
            "pnote" { python scripts/pnote-auto-fill.py }
        }
    }
    "analyze" {
        switch ($SubCommand) {
            "score" { python scripts/paper-quality-scorer.py }
            "trend" { python scripts/tech-trend-predictor.py }
            "collab" { python scripts/collaboration-recommender.py }
        }
    }
    "system" {
        switch ($SubCommand) {
            "monitor" { python scripts/task-monitor.py }
            "quality" { python scripts/data-quality-checker.py }
            "optimize" { python scripts/performance-optimizer.py }
            "report" { python scripts/auto-report-generator.py }
        }
    }
    "status" {
        Write-Host "=== AI Research OS Status ==="
        Write-Host "ArXiv Papers: $((Get-ChildItem 'D:\obsidian\Vault\Arxiv\daily\2026\03\2026-03-05' -Recurse -Filter '*.md').Count)"
        Write-Host "System: Running"
    }
    "help" {
        Write-Host "AI Research OS - Command Line Tool"
        Write-Host ""
        Write-Host "Usage: .\ai-research.ps1 <command> [subcommand]"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  collect <arxiv|twitter|hn|reddit|all>  - 信息收集"
        Write-Host "  process <pdf|pnote>                    - 数据处理"
        Write-Host "  analyze <score|trend|collab>           - AI 分析"
        Write-Host "  system <monitor|quality|optimize|report> - 系统工具"
        Write-Host "  status                                  - 查看状态"
        Write-Host "  help                                    - 查看帮助"
    }
}
```

---

## 🎯 使用示例

```powershell
# 查看所有帮助
.\ai-research.ps1 help

# 收集 arXiv 论文
.\ai-research.ps1 collect arxiv

# 运行系统监控
.\ai-research.ps1 system monitor

# 查看状态
.\ai-research.ps1 status
```

---

*最后更新：2026-03-05 12:38*
