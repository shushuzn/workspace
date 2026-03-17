#!/bin/bash
# API 服务工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "API Gateway Service"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 创建日志目录
mkdir -p logs

# 启动 API 服务
echo "Starting API gateway..."
echo "Server running on http://localhost:5000"
echo ""
echo "Endpoints:"
echo "  GET /api/v1/health     - Health check"
echo "  GET /api/v1/papers     - Get papers data"
echo "  GET /api/v1/trends     - Get trends data"
echo "  GET /api/v1/clusters   - Get clusters data"
echo "  GET /api/v1/graph      - Get knowledge graph"
echo "  GET /api/v1/metrics    - Get monitoring metrics"
echo "  GET /api/v1/alerts     - Get alerts"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"

python scripts/api/api-gateway.py
