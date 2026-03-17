#!/bin/bash
# 数据湖工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "Data Lake Management"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 创建数据湖目录
mkdir -p data-lake/{raw,processed,curated,analytics}

# 运行数据湖管理
echo "[1/1] Running data lake manager..."
python scripts/data-lake/data-lake-manager.py

echo ""
echo "========================================"
echo "Data Lake Management Complete"
echo "========================================"
echo ""
echo "Data Lake: data-lake/"
