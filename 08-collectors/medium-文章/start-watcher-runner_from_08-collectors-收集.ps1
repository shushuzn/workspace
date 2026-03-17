# Medium Watcher 后台运行器 v2.0
# 修复编码问题，支持 Markdown 日志

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$scriptPath = "D:\obsidian\Vault\Medium\medium-watcher-auto.py"
$logPath = "D:\obsidian\Vault\Medium\watcher-runner.md"

function Write-MarkdownLog {
    param($msg, $level = "info")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $icon = switch ($level) {
        "error" { "❌" }
        "success" { "✅" }
        "info" { "ℹ️" }
        "start" { "🚀" }
        "wait" { "⏳" }
        default { "📝" }
    }
    
    $entry = "- **[$timestamp]** $icon $msg`n"
    
    if (-not (Test-Path $logPath)) {
        $header = @"
---
created: 2026-03-01
type: system-log
tags: [medium-watcher, runner, log]
---

# Medium Watcher 后台运行日志

## 运行状态

| 指标 | 值 |
|------|-----|
| **状态** | ✅ 运行中 |
| **启动时间** | $(Get-Date -Format "yyyy-MM-dd HH:mm:ss") |
| **脚本路径** | $scriptPath |

---

## 运行记录

"@
        Set-Content -Path $logPath -Value $header -Encoding UTF8
    }
    
    Add-Content -Path $logPath -Value $entry -Encoding UTF8
}

Write-MarkdownLog "Medium Watcher v2.0 启动" "start"
Write-MarkdownLog "脚本：$scriptPath" "info"

$runCount = 0
while ($true) {
    $runCount++
    Write-MarkdownLog "第 $runCount 次运行" "start"
    
    try {
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = "python"
        $psi.Arguments = $scriptPath
        $psi.WorkingDirectory = "D:\obsidian\Vault\Medium"
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.UseShellExecute = $false
        $psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
        $psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
        
        $process = [System.Diagnostics.Process]::Start($psi)
        $output = $process.StandardOutput.ReadToEnd()
        $error = $process.StandardError.ReadToEnd()
        $process.WaitForExit()
        
        if ($output) {
            Write-MarkdownLog "输出：$output" "success"
        }
        if ($error) {
            Write-MarkdownLog "错误：$error" "error"
        }
    } catch {
        Write-MarkdownLog "异常：$_" "error"
    }
    
    Write-MarkdownLog "等待 5 分钟..." "wait"
    Start-Sleep -Seconds 300
}
