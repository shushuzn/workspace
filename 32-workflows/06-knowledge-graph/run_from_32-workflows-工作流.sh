#!/bin/bash
# 知识图谱更新工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "Knowledge Graph Update Workflow"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 运行知识图谱脚本
echo "[1/1] Running knowledge graph updater..."
python scripts/materials/materials-knowledge-graph.py

echo ""
echo "========================================"
echo "Knowledge Graph Updated!"
echo "========================================"
