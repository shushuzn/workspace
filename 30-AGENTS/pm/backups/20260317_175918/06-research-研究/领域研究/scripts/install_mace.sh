#!/bin/bash
# MACE-MP-0 安装脚本
# 创建时间：2026-03-06 00:20

echo "========================================"
echo "MACE-MP-0 安装脚本"
echo "========================================"

# 1. 检查 Python 版本
echo ""
echo "[1/5] 检查 Python 环境..."
python --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python not found!"
    exit 1
fi

# 2. 安装 PyTorch (如果未安装)
echo ""
echo "[2/5] 检查/安装 PyTorch..."
python -c "import torch" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing PyTorch..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
else
    echo "PyTorch already installed."
    python -c "import torch; print(f'PyTorch {torch.__version__}')"
fi

# 3. 安装 MACE 依赖
echo ""
echo "[3/5] 安装 MACE 依赖..."
pip install e3nn torch_geometric opt_einsum

# 4. 安装 MACE
echo ""
echo "[4/5] 安装 MACE..."
pip install mace-torch

# 5. 下载预训练模型
echo ""
echo "[5/5] 下载 MACE-MP-0 模型..."
mkdir -p research/models/mace
cd research/models/mace

# 检查模型是否已存在
if [ -f "mace-mp-0.model" ]; then
    echo "Model already exists."
else
    echo "Downloading MACE-MP-0 model (~200MB)..."
    wget https://github.com/ACEsuit/mace/raw/main/models/mace-mp-0.model
    if [ $? -ne 0 ]; then
        echo "Download failed, trying alternative URL..."
        wget https://huggingface.co/mace-models/mace-mp/resolve/main/mace-mp-0.model
    fi
fi

# 验证安装
echo ""
echo "========================================"
echo "验证安装..."
echo "========================================"
python -c "
from mace.calculators import MACECalculator
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'MACE: installed')
print('Installation complete!')
"

echo ""
echo "========================================"
echo "[OK] MACE-MP-0 安装完成！"
echo "========================================"
echo ""
echo "模型位置：research/models/mace/mace-mp-0.model"
echo ""
echo "使用示例:"
echo "  python research/scripts/mace_test.py"
echo ""
