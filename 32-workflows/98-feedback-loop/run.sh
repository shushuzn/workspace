#!/bin/bash
# 反馈循环工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "Feedback Loop System"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 创建反馈目录
mkdir -p feedback

# 运行反馈系统
echo "[1/1] Running feedback loop..."
python scripts/feedback/feedback-loop.py

echo ""
echo "========================================"
echo "Feedback Loop Complete"
echo "========================================"
echo ""
echo "Records: feedback/"
