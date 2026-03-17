#!/bin/bash
# 报告生成工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "Research Report Generation Workflow"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 运行报告生成脚本
echo "[1/1] Running report generator..."
python scripts/materials/generate-report.py

echo ""
echo "========================================"
echo "Report Generated!"
echo "========================================"
