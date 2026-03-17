# CLI 使用文档

**版本:** v2.0  
**创建时间:** 2026-03-05 18:40  

---

## 📋 安装

### 方法 1: 直接运行

```bash
python scripts/arxiv_ops_cli.py --help
```

### 方法 2: 安装为命令行工具

```bash
# 安装依赖
pip install click requests

# 创建软链接 (Linux/Mac)
ln -s $(pwd)/scripts/arxiv_ops_cli.py /usr/local/bin/arxiv-ops

# Windows (PowerShell)
New-Item -ItemType SymbolicLink -Path "C:\ProgramData\arxiv-ops.py" -Target "$(pwd)\scripts\arxiv_ops_cli.py"
```

---

## 🚀 快速开始

### 查看帮助

```bash
arxiv-ops --help
```

### 健康检查

```bash
arxiv-ops health
```

输出:
```
✓ 系统健康 (版本：2.0.0)
```

### 查看系统状态

```bash
arxiv-ops status
```

输出:
```
系统状态:
========================================
  健康状态： ✓ 2.0.0
  API 请求： 1234
  CPU: 35.2%
  内存：65.8%
========================================
```

### 查看系统指标

```bash
# 文本格式
arxiv-ops metrics

# JSON 格式
arxiv-ops metrics --format json
```

输出:
```
系统指标:
  API 请求数：1234
  API 错误数：5
  CPU 使用率：35.2%
  内存使用率：65.8%
```

### 查看告警

```bash
# 查看所有告警
arxiv-ops alerts

# 查看警告级别告警
arxiv-ops alerts --severity warning

# 限制显示数量
arxiv-ops alerts --limit 5
```

输出:
```
告警列表 (共 3 条):
[WARNING] high_cpu: cpu_usage=85.5
[ERROR] high_memory: memory_usage=92.3
[CRITICAL] high_error_rate: error_rate=8.5
```

### 查看质量报告

```bash
arxiv-ops quality
```

### 查看日志

```bash
arxiv-ops logs
```

输出:
```
日志文件:
  - api-gateway.log
  - quality-control.log
  - monitoring-enhanced.log

最新日志 (monitoring-enhanced.log):
2026-03-05 18:40:00 - INFO - Starting monitoring
2026-03-05 18:40:01 - INFO - CPU usage: 35.2%
...
```

### 配置管理

```bash
# 显示所有配置
arxiv-ops config show

# 获取配置项
arxiv-ops config get security.api_key

# 设置配置项
arxiv-ops config set security.api_key new-key
```

### 触发论文收集

```bash
# 收集今日论文
arxiv-ops collect

# 收集指定日期论文
arxiv-ops collect --date 2026-03-05

# 异步执行
arxiv-ops collect --async
```

---

## 📖 命令参考

### 系统命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `health` | 健康检查 | `arxiv-ops health` |
| `status` | 系统状态 | `arxiv-ops status` |
| `metrics` | 系统指标 | `arxiv-ops metrics --format json` |
| `alerts` | 查看告警 | `arxiv-ops alerts --severity warning` |
| `logs` | 查看日志 | `arxiv-ops logs` |

### 质量命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `quality` | 质量报告 | `arxiv-ops quality` |

### 收集命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `collect` | 触发收集 | `arxiv-ops collect --date 2026-03-05` |

### 配置命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `config show` | 显示配置 | `arxiv-ops config show` |
| `config get` | 获取配置 | `arxiv-ops config get key` |
| `config set` | 设置配置 | `arxiv-ops config set key value` |

---

## 🔧 高级用法

### 脚本集成

```bash
#!/bin/bash
# 健康检查脚本

if ! arxiv-ops health > /dev/null; then
    echo "系统异常！"
    # 发送告警
    exit 1
fi

echo "系统正常"
```

### 监控集成

```bash
# Prometheus Exporter
arxiv-ops metrics --format json | jq '.gauges' > /var/lib/prometheus/node-exporter/arxiv-ops.prom
```

---

*最后更新：2026-03-05 18:40*
