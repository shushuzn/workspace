#!/usr/bin/env pwsh
# AI Research OS 命令行工具
# 用法：.\ai-research.ps1 <command> [subcommand]

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
        $arxivCount = (Get-ChildItem "D:\obsidian\Vault\Arxiv\daily\2026\03\2026-03-05" -Recurse -Filter "*.md" -ErrorAction SilentlyContinue).Count
        Write-Host "ArXiv Papers: $arxivCount"
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
