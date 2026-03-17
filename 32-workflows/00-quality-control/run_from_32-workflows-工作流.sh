#!/bin/bash
# Level 0: 质量控制工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "Level 0: Quality Control"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 运行质量控制
echo "[1/1] Running quality controller..."
python scripts/level-0/quality-controller.py

# 检查退出码
if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "❌ Quality Gate FAILED"
    echo "========================================"
    echo "Stopping pipeline"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ Quality Gate PASSED"
echo "========================================"
