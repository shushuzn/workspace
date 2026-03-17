#!/bin/bash
# 代码质量检查脚本

set -e

echo "========================================"
echo "代码质量检查"
echo "========================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0

# flake8 (代码风格检查)
echo "运行 flake8 (代码风格检查)..."
if flake8 scripts/ --count --select=E9,F63,F7,F82 --show-source --statistics; then
    echo -e "${GREEN}✓ flake8 通过${NC}"
else
    echo -e "${RED}✗ flake8 失败${NC}"
    ERRORS=$((ERRORS + 1))
fi

# mypy (类型检查)
echo "运行 mypy (类型检查)..."
if mypy scripts/ --ignore-missing-imports; then
    echo -e "${GREEN}✓ mypy 通过${NC}"
else
    echo -e "${YELLOW}⚠ mypy 有警告${NC}"
    # mypy 警告不视为错误
fi

# black (代码格式化检查)
echo "运行 black (代码格式化检查)..."
if black scripts/ --check; then
    echo -e "${GREEN}✓ black 通过${NC}"
else
    echo -e "${YELLOW}⚠ black 需要格式化${NC}"
    echo "运行 'black scripts/' 进行格式化"
fi

# pylint (代码质量分析)
echo "运行 pylint (代码质量分析)..."
if pylint scripts/ --fail-under=8.0; then
    echo -e "${GREEN}✓ pylint 通过 (评分 > 8.0)${NC}"
else
    echo -e "${YELLOW}⚠ pylint 评分 < 8.0${NC}"
fi

echo ""
echo "========================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}代码质量检查通过！${NC}"
else
    echo -e "${RED}代码质量检查失败！${NC}"
    exit 1
fi
echo "========================================"
