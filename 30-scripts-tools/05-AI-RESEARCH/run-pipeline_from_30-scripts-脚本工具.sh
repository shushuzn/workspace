#!/bin/bash
# 论文分析流水线运行脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "Paper Analysis Pipeline"
echo "========================================"
echo ""

# 进入工作区
cd "$WORKSPACE_DIR"

echo "Running Level 1: Paper Collection..."
bash workflows/arxiv-collect/run.sh
echo ""

echo "Running Level 2: Paper Classification..."
python scripts/analysis/paper-classifier.py
echo ""

echo "Running Level 3: Trend Analysis..."
python scripts/analysis/trend-analyzer.py
echo ""

echo "Running Level 4: Topic Clustering..."
python scripts/analysis/topic-clusterer.py
echo ""

echo "========================================"
echo "Paper Analysis Pipeline Complete!"
echo "========================================"
