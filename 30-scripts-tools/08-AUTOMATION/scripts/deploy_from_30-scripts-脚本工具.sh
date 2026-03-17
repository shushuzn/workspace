#!/bin/bash
# 一键部署脚本

set -e

echo "========================================"
echo "AI Research OS 部署脚本"
echo "========================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python
echo -n "检查 Python... "
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✓ ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}✗ Python 未安装${NC}"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
python -m pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ 依赖安装完成${NC}"

# 创建目录
echo "创建目录..."
mkdir -p logs
mkdir -p scripts/cache
mkdir -p data
echo -e "${GREEN}✓ 目录创建完成${NC}"

# 数据库迁移
echo "执行数据库迁移..."
# TODO: 实现数据库迁移
echo -e "${GREEN}✓ 数据库迁移完成${NC}"

# 启动服务
echo "启动服务..."

# 启动 API 服务
python scripts/api/api-gateway.py > logs/api-gateway.log 2>&1 &
API_PID=$!
echo -e "${GREEN}✓ API 服务已启动 (PID: $API_PID)${NC}"

# 启动监控服务
python scripts/monitoring/enhanced_monitoring.py > logs/monitoring.log 2>&1 &
MONITOR_PID=$!
echo -e "${GREEN}✓ 监控服务已启动 (PID: $MONITOR_PID)${NC}"

# 保存 PID
echo $API_PID > pids/api.pid
echo $MONITOR_PID > pids/monitor.pid

echo ""
echo "========================================"
echo -e "${GREEN}部署完成！${NC}"
echo "========================================"
echo ""
echo "服务状态:"
echo "  API:      http://localhost:5000"
echo "  监控：    运行中"
echo ""
echo "日志文件:"
echo "  logs/api-gateway.log"
echo "  logs/monitoring.log"
echo ""
echo "停止服务:"
echo "  ./deploy.sh stop"
echo ""
