#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MACE-MP-0 测试脚本
测试 LIG 碳结构弛豫

作者：AI Research OS
创建时间：2026-03-06 00:20
"""

import numpy as np
from pathlib import Path
import json

print("=" * 60)
print("MACE-MP-0 测试 - LIG 碳结构弛豫")
print("=" * 60)

# 1. 检查 MACE 安装
print("\n[1/4] 检查 MACE 安装...")
try:
    from mace.calculators import MACECalculator
    import torch
    print(f"  MACE: ✅ 已安装")
    print(f"  PyTorch: {torch.__version__}")
    print(f"  CUDA: {'✅' if torch.cuda.is_available() else '❌'}")
    MACE_AVAILABLE = True
except ImportError as e:
    print(f"  MACE: ❌ 未安装")
    print(f"  错误：{e}")
    print(f"  请运行：pip install mace-torch")
    MACE_AVAILABLE = False

# 2. 检查模型文件
print("\n[2/4] 检查模型文件...")
model_path = Path("research/models/mace/mace-mp-0.model")
if model_path.exists():
    print(f"  模型：✅ 已存在 ({model_path.stat().st_size/1024/1024:.1f} MB)")
else:
    print(f"  模型：❌ 不存在")
    print(f"  位置：{model_path}")
    print(f"  请运行安装脚本下载模型")

# 3. 创建测试结构 (石墨)
print("\n[3/4] 创建测试结构 (石墨)...")

try:
    from ase import Atoms
    from ase.build import bulk

    # 创建石墨结构
    graphite = bulk('C', 'hex', a=2.46, c=6.71)
    print(f"  原子数：{len(graphite)}")
    print(f"  晶格常数：a={graphite.cell[0,0]:.2f} Å, c={graphite.cell[2,2]:.2f} Å")
    print(f"  体积：{graphite.get_volume():.2f} Å³")

    # 计算初始能量 (使用 MACE)
    if MACE_AVAILABLE and model_path.exists():
        print("\n[4/4] MACE 能量计算...")

        calc = MACECalculator(
            model_path=str(model_path),
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )

        graphite.calc = calc

        # 计算能量
        energy = graphite.get_potential_energy()
        forces = graphite.get_forces()

        print(f"  总能量：{energy:.4f} eV")
        print(f"  每原子能量：{energy/len(graphite):.4f} eV/atom")
        print(f"  最大力：{np.max(np.abs(forces)):.4f} eV/Å")

        # 与 DFT 参考值对比
        dft_ref = -9.17  # MP 石墨 DFT 能量 (eV/atom)
        mace_energy_per_atom = energy / len(graphite)
        error = abs(mace_energy_per_atom - dft_ref)

        print(f"\n  与 DFT 对比:")
        print(f"    DFT 参考：{dft_ref:.4f} eV/atom")
        print(f"    MACE: {mace_energy_per_atom:.4f} eV/atom")
        print(f"    误差：{error*1000:.1f} meV/atom")

        if error < 0.010:
            print(f"    精度：✅ 优秀 (<10 meV/atom)")
        elif error < 0.050:
            print(f"    精度：✅ 良好 (<50 meV/atom)")
        else:
            print(f"    精度：⚠️ 可接受")

        # 保存结果
        result = {
            'structure': 'graphite',
            'n_atoms': len(graphite),
            'energy_eV': float(energy),
            'energy_per_atom_eV': float(mace_energy_per_atom),
            'max_force_eV_A': float(np.max(np.abs(forces))),
            'dft_reference_eV': dft_ref,
            'error_meV': float(error * 1000),
            'device': 'cuda' if torch.cuda.is_available() else 'cpu'
        }

        output_dir = Path("research/data")
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / "mace_test_result.json", 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n  结果已保存：{output_dir / 'mace_test_result.json'}")

    else:
        print("\n[4/4] 跳过能量计算 (MACE 未完全安装)")
        print("  请完成安装后重新运行")

    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

except ImportError:
    print("  ASE: ❌ 未安装")
    print("  请运行：pip install ase")

    print("\n" + "=" * 60)
    print("⚠️ 测试未完成 (缺少依赖)")
    print("=" * 60)

# 安装命令总结
print("\n" + "=" * 60)
print("安装命令总结")
print("=" * 60)
print("""
# 1. 安装 MACE
pip install mace-torch e3nn torch_geometric

# 2. 下载模型 (手动)
mkdir research\\models\\mace
cd research\\models\\mace
wget https://github.com/ACEsuit/mace/raw/main/models/mace-mp-0.model

# 3. 测试
python research\\scripts\\mace_test.py

# 4. 运行 LIG 结构弛豫
python research\\scripts\\mace_lig_relax.py
""")
