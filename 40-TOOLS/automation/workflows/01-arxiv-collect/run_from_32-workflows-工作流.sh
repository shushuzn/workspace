#!/bin/bash
# ArXiv 收集工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "ArXiv Paper Collection Workflow"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 运行收集脚本
echo "[1/1] Running ArXiv collector..."
python scripts/materials/materials-collector.py

echo ""
echo "========================================"
echo "Collection Complete!"
echo "========================================"
