#!/bin/bash
# 监控与告警工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "Monitoring & Alerting System"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 创建监控目录
mkdir -p monitoring

# 运行监控系统
echo "[1/1] Running monitoring system..."
python scripts/monitoring/monitoring-system.py

echo ""
echo "========================================"
echo "Monitoring Complete"
echo "========================================"
echo ""
echo "Metrics: monitoring/metrics.json"
echo "Alerts:  monitoring/alerts.json"
