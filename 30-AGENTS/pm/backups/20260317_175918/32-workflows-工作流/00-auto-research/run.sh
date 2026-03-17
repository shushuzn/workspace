#!/bin/bash
# 自动化研究工作流运行脚本 (完整版)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "Automated Materials Research Workflow"
echo "========================================"
echo ""

START_TIME=$(date +%s)

# 进入工作区
cd "$WORKSPACE_DIR"

# Step 1: ArXiv 收集
echo "[Step 1/5] Collecting ArXiv papers..."
bash workflows/arxiv-collect/run.sh
echo ""

# Step 2: 趋势分析
echo "[Step 2/5] Analyzing research trends..."
bash workflows/trend-analysis/run.sh
echo ""

# Step 3: 报告生成
echo "[Step 3/5] Generating research report..."
bash workflows/report-gen/run.sh
echo ""

# Step 4: 知识图谱更新
echo "[Step 4/5] Updating knowledge graph..."
bash workflows/knowledge-graph/run.sh
echo ""

# Step 5: Git 提交
echo "[Step 5/5] Committing changes to Git..."
bash workflows/git-commit/run.sh
echo ""

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "========================================"
echo "Workflow Completed in ${DURATION} seconds!"
echo "========================================"
