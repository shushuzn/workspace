#!/bin/bash
# 趋势分析工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "Materials Trend Analysis Workflow"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 运行分析脚本
echo "[1/1] Running trend analysis..."
python scripts/materials/materials-deep-research.py

echo ""
echo "========================================"
echo "Analysis Complete!"
echo "========================================"
