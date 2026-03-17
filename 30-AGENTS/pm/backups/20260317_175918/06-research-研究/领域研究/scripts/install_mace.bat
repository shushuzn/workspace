@echo off
REM MACE-MP-0 Windows 安装脚本
REM 创建时间：2026-03-06 00:20

echo ========================================
echo MACE-MP-0 安装脚本 (Windows)
echo ========================================

REM 1. 检查 Python
echo.
echo [1/5] Checking Python environment...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    exit /b 1
)

REM 2. 安装/检查 PyTorch
echo.
echo [2/5] Checking/Installing PyTorch...
python -c "import torch" 2>nul
if errorlevel 1 (
    echo Installing PyTorch...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
) else (
    echo PyTorch already installed.
    python -c "import torch; print(f'PyTorch {torch.__version__}')"
)

REM 3. 安装 MACE 依赖
echo.
echo [3/5] Installing MACE dependencies...
pip install e3nn torch_geometric opt_einsum

REM 4. 安装 MACE
echo.
echo [4/5] Installing MACE...
pip install mace-torch

REM 5. 创建模型目录
echo.
echo [5/5] Setting up model directory...
if not exist "research\models\mace" mkdir research\models\mace

REM 验证安装
echo.
echo ========================================
echo Verifying installation...
echo ========================================
python -c "from mace.calculators import MACECalculator; import torch; print('MACE installed successfully!')"

echo.
echo ========================================
echo [OK] MACE-MP-0 installation complete!
echo ========================================
echo.
echo Model directory: research\models\mace\
echo.
echo Test with:
echo   python research\scripts\mace_test.py
echo.
pause
