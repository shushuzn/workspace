#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MACE LIG 碳结构弛豫
模拟 LIG (激光诱导石墨烯) 的无序碳结构

作者：AI Research OS
创建时间：2026-03-06 00:25
"""

import numpy as np
from pathlib import Path
import json

print("=" * 60)
print("MACE LIG 碳结构弛豫")
print("=" * 60)

# 检查依赖
print("\n[1/5] 检查依赖...")
try:
    from mace.calculators import MACECalculator
    from ase import Atoms
    from ase.optimize import BFGS, FIRE
    from ase.md.velocitydistribution import MaxwellBoltzmannDistribution
    from ase.md.verlet import VelocityVerlet
    from ase import units
    import torch
    print("  ✅ 所有依赖已安装")
except ImportError as e:
    print(f"  ❌ 缺少依赖：{e}")
    print("  请运行：pip install mace-torch ase")
    exit(1)

# 加载模型
print("\n[2/5] 加载 MACE-MP-0 模型...")
model_path = Path("research/models/mace/mace-mp-0.model")
if not model_path.exists():
    print(f"  ❌ 模型不存在：{model_path}")
    print("  请先下载模型")
    exit(1)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"  模型：{model_path}")
print(f"  设备：{device}")

calc = MACECalculator(model_path=str(model_path), device=device)
print("  ✅ 模型加载成功")

# 创建 LIG 模型结构 (无序碳)
print("\n[3/5] 创建 LIG 模型结构...")

def create_lig_model(n_atoms=50, density=2.0):
    """
    创建 LIG 无序碳结构模型
    
    参数:
        n_atoms: 原子数
        density: 密度 (g/cm³), LIG 通常 1.5-2.2 g/cm³
    """
    from ase.build import bulk

    # 从石墨开始
    graphite = bulk('C', 'hex', a=2.46, c=6.71)

    # 扩大超胞
    supercell = graphite * (3, 3, 2)  # 72 原子

    # 引入无序 (模拟激光处理)
    positions = supercell.get_positions()

    # 随机位移 (模拟缺陷)
    np.random.seed(42)
    displacement = np.random.normal(0, 0.3, positions.shape)  # 0.3 Å 标准差
    positions += displacement

    supercell.set_positions(positions)

    # 调整密度
    current_volume = supercell.get_volume()
    n_atoms = len(supercell)
    target_volume = n_atoms * 12.01 / (density * 6.022) * 10  # 转换为 Å³

    scale = (target_volume / current_volume) ** (1/3)
    supercell.set_cell(supercell.get_cell() * scale, scale_atoms=True)

    return supercell

# 创建 LIG 结构
lig_structure = create_lig_model(n_atoms=72, density=2.0)
print(f"  原子数：{len(lig_structure)}")
print(f"  密度：2.0 g/cm³")
print(f"  体积：{lig_structure.get_volume():.2f} Å³")
print(f"  初始结构：无序碳 (模拟 LIG)")

# 设置计算器
lig_structure.calc = calc

# 计算初始能量/力
initial_energy = lig_structure.get_potential_energy()
initial_forces = lig_structure.get_forces()
max_initial_force = np.max(np.abs(initial_forces))

print(f"\n  初始能量：{initial_energy:.4f} eV")
print(f"  初始最大力：{max_initial_force:.4f} eV/Å")

# 结构弛豫
print("\n[4/5] MACE 结构弛豫...")
print("  优化器：FIRE")
print("  收敛标准：fmax < 0.05 eV/Å")

opt = FIRE(lig_structure, trajectory='research/data/lig_relax.traj')
opt.run(fmax=0.05, steps=200)

# 弛豫后分析
final_energy = lig_structure.get_potential_energy()
final_forces = lig_structure.get_forces()
max_final_force = np.max(np.abs(final_forces))

energy_change = final_energy - initial_energy

print(f"\n  弛豫完成！")
print(f"  最终能量：{final_energy:.4f} eV")
print(f"  能量变化：{energy_change:.4f} eV ({energy_change/len(lig_structure)*1000:.1f} meV/atom)")
print(f"  最终最大力：{max_final_force:.4f} eV/Å")

# 结构分析
print("\n[5/5] 结构分析...")

# 键长分析
from ase.geometry import get_distances

positions = lig_structure.get_positions()
cell = lig_structure.get_cell()
pbc = lig_structure.get_pbc()

# 计算所有 C-C 距离
distances = []
for i in range(len(lig_structure)):
    for j in range(i+1, len(lig_structure)):
        d = get_distances(positions[i:i+1], positions[j:j+1], cell, pbc)[0][0]
        if d < 2.5:  # 只考虑近邻
            distances.append(d)

distances = np.array(distances)
print(f"  C-C 键数：{len(distances)}")
print(f"  平均键长：{np.mean(distances):.3f} Å")
print(f"  键长范围：{np.min(distances):.3f} - {np.max(distances):.3f} Å")

# 与石墨对比
graphite_cc = 1.42  # 石墨 C-C 键长
print(f"\n  参考 (石墨): {graphite_cc:.3f} Å")
print(f"  差异：{np.mean(distances) - graphite_cc:+.3f} Å")

# 保存结果
result = {
    'structure': 'LIG_disordered_carbon',
    'n_atoms': len(lig_structure),
    'density_g_cm3': 2.0,
    'initial_energy_eV': float(initial_energy),
    'final_energy_eV': float(final_energy),
    'energy_change_eV': float(energy_change),
    'energy_change_meV_per_atom': float(energy_change / len(lig_structure) * 1000),
    'max_initial_force_eV_A': float(max_initial_force),
    'max_final_force_eV_A': float(max_final_force),
    'mean_cc_bond_length_A': float(np.mean(distances)),
    'min_cc_bond_A': float(np.min(distances)),
    'max_cc_bond_A': float(np.max(distances)),
    'graphite_reference_A': graphite_cc,
    'device': device,
    'relaxation_steps': opt.get_number_of_steps()
}

output_dir = Path("research/data")
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "mace_lig_relax_result.json", 'w') as f:
    json.dump(result, f, indent=2)

# 保存弛豫后结构
from ase.io import write
write(output_dir / "lig_relaxed_structure.xyz", lig_structure)

print(f"\n  结果已保存:")
print(f"    {output_dir / 'mace_lig_relax_result.json'}")
print(f"    {output_dir / 'lig_relaxed_structure.xyz'}")
print(f"    {output_dir / 'lig_relax.traj'} (弛豫轨迹)")

print("\n" + "=" * 60)
print("✅ LIG 结构弛豫完成！")
print("=" * 60)

# 下一步建议
print("\n下一步建议:")
print("  1. 使用 CGCNN 预测电导率")
print("  2. 运行 MD 模拟研究热稳定性")
print("  3. 引入缺陷 (空位/掺杂) 研究 ID/IG")
print("  4. 与实验拉曼光谱对比")
