#!/usr/bin/env python3
"""
使用 pip 安装方式获取 MACE 和 CHGNet 模型
"""
import subprocess
import sys
from pathlib import Path

print("=" * 70)
print("使用 pip 安装 MACE 和 CHGNet")
print("=" * 70)

# 1. 安装 mace-torch
print("\n[1/3] 安装 mace-torch...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mace-torch", "-q"])
    print("  [OK] mace-torch 安装成功")
except Exception as e:
    print(f"  [ERROR] mace-torch 安装失败：{e}")

# 2. 安装 matgl (包含 CHGNet)
print("\n[2/3] 安装 matgl...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matgl", "-q"])
    print("  [OK] matgl 安装成功")
except Exception as e:
    print(f"  [ERROR] matgl 安装失败：{e}")

# 3. 验证安装
print("\n[3/3] 验证安装...")
try:
    from mace.calculators import mace_mp
    print("  [OK] MACE 导入成功")
    
    # 尝试加载模型
    try:
        calc = mace_mp(model="small", device="cpu")
        print("  [OK] MACE-MP 模型加载成功")
    except Exception as e:
        print(f"  [WARN] MACE 模型加载失败：{e}")
        print(f"  [INFO] 首次运行会自动下载模型")
except Exception as e:
    print(f"  [ERROR] MACE 导入失败：{e}")

try:
    import matgl
    print("  [OK] CHGNet (matgl) 导入成功")
    
    # 尝试加载模型
    try:
        model = matgl.load_model("CHGNet-MP-2024.2.13-PBE")
        print("  [OK] CHGNet-MP 模型加载成功")
    except Exception as e:
        print(f"  [WARN] CHGNet 模型加载失败：{e}")
        print(f"  [INFO] 首次运行会自动下载模型")
except Exception as e:
    print(f"  [ERROR] CHGNet 导入失败：{e}")

print("\n" + "=" * 70)
print("[OK] 安装完成！")
print("=" * 70)
print("\n下一步:")
print("  1. 运行迁移学习微调")
print("  2. 集成预测")
print("=" * 70)
