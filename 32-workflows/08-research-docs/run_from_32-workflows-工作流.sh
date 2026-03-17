#!/bin/bash
# 研究文档自动化工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "Research Documentation Automation"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 运行文档生成器
echo "[1/4] Generating weekly report..."
python scripts/research/research-doc-generator.py

echo ""
echo "[2/4] Syncing arXiv papers..."
python scripts/research/sync-arxiv-papers.py

echo ""
echo "[3/4] Updating research progress..."
python scripts/research/update-progress.py

echo ""
echo "[4/4] Generating statistics..."
python scripts/research/generate-stats.py

echo ""
echo "========================================"
echo "Research Documentation Complete!"
echo "========================================"
