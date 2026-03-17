#!/bin/bash
# Git 提交工作流运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "Git Commit Workflow"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

# 运行 Git 提交脚本
echo "[1/3] Adding files..."
git add -A

echo "[2/3] Committing changes..."
TODAY=$(date +%Y-%m-%d)
git commit -m "🤖 Automated research update $TODAY"

echo "[3/3] Pushing to GitHub..."
git push

echo ""
echo "========================================"
echo "Git Commit Complete!"
echo "========================================"
