# CPU 限制配置

**创建时间:** 2026-03-05 01:40  
**目标:** 严格控制 CPU 占用，避免系统过载

---

## Docker 资源限制

### 已停止的服务
- [x] memsys-elasticsearch (1.8GB 内存，~0.36% CPU)
- [x] evermemos-app (如运行)

### 运行中的容器限制
| 容器 | CPU 限制 | 内存限制 | 状态 |
|------|---------|---------|------|
| memsys-mongodb | 25% | 512MB | ✅ healthy |
| memsys-redis | 10% | 128MB | ✅ healthy |
| memsys-milvus-standalone | 50% | 2GB | ✅ healthy |
| memsys-milvus-minio | 10% | 256MB | ✅ healthy |
| memsys-milvus-etcd | 10% | 128MB | ⚠️ unhealthy |

**总计:** ~105% CPU (多核平均), ~3GB 内存

---

## 进程优先级限制

### 高 CPU 占用进程处理
| 进程 | 操作 | 优先级 |
|------|------|--------|
| com.docker.backend | 限制 CPU | BelowNormal |
| Docker Desktop | 限制 CPU | BelowNormal |
| node (n8n) | 停止/限制 | Low |
| msedgewebview2 | 不干预 | Normal |

---

## PowerShell 限制脚本

```powershell
# 设置 Docker Desktop 进程优先级
Get-Process "Docker Desktop" | ForEach-Object { $_.PriorityClass = "BelowNormal" }
Get-Process "com.docker.backend" | ForEach-Object { $_.PriorityClass = "BelowNormal" }

# 限制 node 进程 CPU (如运行 n8n)
Get-Process node | Where-Object {$_.CPU -gt 50} | ForEach-Object {
    $_.PriorityClass = "Low"
}
```

---

## 定时任务 CPU 限制

### arXiv 收集
- 最大 CPU: 50%
- 最大并发：1 个领域/秒
- 延迟：100ms/请求

### 批量解析
- 最大子代理数：2 (原 4)
- 单论文 CPU 限制：25%
- 内存限制：1GB/代理

### 知识蒸馏
- 仅在低负载时运行
- CPU 阈值：<30%
- 时间窗口：02:00-06:00

---

## 监控命令

```powershell
# 实时查看 CPU 占用
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, Id

# Docker 容器资源
docker stats --no-stream

# 停止高占用进程
Stop-Process -Name "process_name" -Force
```

---

## 自动限制脚本

保存为 `scripts/cpu-limiter.ps1`:

```powershell
# CPU 自动限制脚本
$threshold = 80  # CPU 阈值 %
$checkInterval = 60  # 检查间隔 (秒)

while ($true) {
    $cpuLoad = (Get-Counter '\Processor(_Total)\% Processor Time').CounterSamples.CookedValue
    
    if ($cpuLoad -gt $threshold) {
        Write-Host "[$(Get-Date)] CPU 过高：$cpuLoad%"
        
        # 降低 Docker 进程优先级
        Get-Process "Docker Desktop" -ErrorAction SilentlyContinue | 
            ForEach-Object { $_.PriorityClass = "BelowNormal" }
        
        # 记录日志
        Add-Content -Path "logs/cpu-throttle.log" -Value "$(Get-Date): CPU $cpuLoad% - throttled"
    }
    
    Start-Sleep -Seconds $checkInterval
}
```

---

## 当前状态 (01:42)

**Docker 容器 CPU:** ~11.68% (总计)  
**Docker 容器内存:** ~2.8GB  
**系统负载:** 正常  

**已执行优化:**
- [x] 停止 Elasticsearch (-1.8GB 内存)
- [x] 停止高占用 node 进程
- [x] 设置 Docker Desktop 优先级 → BelowNormal
- [x] 设置 com.docker.backend 优先级 → BelowNormal
- [x] 创建 cpu-limiter.ps1 自动监控脚本
- [ ] 配置 n8n 工作流 CPU 限制

**监控脚本:** `D:\OpenClaw\workspace\scripts\cpu-limiter.ps1`
- 阈值：70%
- 检查间隔：30 秒
- 日志：`logs/cpu-throttle.log`

---

*最后更新：2026-03-05 01:42*
