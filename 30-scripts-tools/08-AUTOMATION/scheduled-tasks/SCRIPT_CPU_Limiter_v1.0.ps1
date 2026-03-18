# CPU 自动限制脚本
# 用法：.\cpu-limiter.ps1

$threshold = 70  # CPU 阈值 %
$checkInterval = 30  # 检查间隔 (秒)
$logFile = "D:\OpenClaw\workspace\logs\cpu-throttle.log"

Write-Host "=== CPU 限制监控启动 ==="
Write-Host "阈值：$threshold% | 间隔：${checkInterval}s"
Write-Host "日志：$logFile"
Write-Host ""

# 创建日志目录
$logDir = Split-Path $logFile -Parent
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

while ($true) {
    try {
        $cpuLoad = [math]::Round((Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue, 2)
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        
        if ($cpuLoad -gt $threshold) {
            $msg = "[$timestamp] ⚠️ CPU 过高：$cpuLoad% - 执行限制"
            Write-Host $msg -ForegroundColor Yellow
            Add-Content -Path $logFile -Value $msg
            
            # 降低 Docker 进程优先级
            Get-Process "Docker Desktop" -ErrorAction SilentlyContinue | ForEach-Object {
                $_.PriorityClass = "BelowNormal"
                Write-Host "  → Docker Desktop 优先级：BelowNormal"
            }
            
            Get-Process "com.docker.backend" -ErrorAction SilentlyContinue | ForEach-Object {
                $_.PriorityClass = "BelowNormal"
                Write-Host "  → com.docker.backend 优先级：BelowNormal"
            }
            
            # 限制 node 进程
            Get-Process node -ErrorAction SilentlyContinue | Where-Object {$_.CPU -gt 50} | ForEach-Object {
                $_.PriorityClass = "Low"
                Write-Host "  → node ($($_.Id)) 优先级：Low"
            }
        }
        else {
            Write-Host "[$timestamp] ✓ CPU 正常：$cpuLoad%" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "[$timestamp] 错误：$($_.Exception.Message)" -ForegroundColor Red
        Add-Content -Path $logFile -Value "[$timestamp] ERROR: $($_.Exception.Message)"
    }
    
    Start-Sleep -Seconds $checkInterval
}
