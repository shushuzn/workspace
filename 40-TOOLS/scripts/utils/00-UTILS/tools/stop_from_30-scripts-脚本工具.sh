#!/bin/bash
# 停止部署脚本

set -e

echo "========================================"
echo "停止 AI Research OS 服务"
echo "========================================"

# 停止 API 服务
if [ -f pids/api.pid ]; then
    API_PID=$(cat pids/api.pid)
    echo "停止 API 服务 (PID: $API_PID)..."
    kill $API_PID 2>/dev/null || true
    rm pids/api.pid
    echo "✓ API 服务已停止"
fi

# 停止监控服务
if [ -f pids/monitor.pid ]; then
    MONITOR_PID=$(cat pids/monitor.pid)
    echo "停止监控服务 (PID: $MONITOR_PID)..."
    kill $MONITOR_PID 2>/dev/null || true
    rm pids/monitor.pid
    echo "✓ 监控服务已停止"
fi

echo ""
echo "✓ 所有服务已停止"
