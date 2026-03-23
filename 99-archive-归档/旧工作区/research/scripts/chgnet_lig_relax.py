#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHGNet LIG 碳结构弛豫
专门针对激光诱导石墨烯 (LIG) 的无序碳结构

作者：AI Research OS
创建时间：2026-03-06 00:30
"""

import numpy as np
from pathlib import Path
import json

print("=" * 60)
print("CHGNet LIG 碳结构弛豫")
print("=" * 60)

# 检查依赖
print("\n[1/5] 检查依赖...")
try:
    from chgnet.model.model import CHGNet
    from chgnet.model.dynamics import Relaxer
    from chgnet.graph import CrystalGraphConverter
    from ase.build import bulk
    import torch
    print("  ✅ 所有依赖已安装")
except ImportError as e:
    print(f"  ❌ 缺少依赖：{e}")
    print("  请运行：pip install chgnet ase")
    exit(1)

# 加载模型
print("\n[2/5] 加载 CHGNet 模型...")
chgnet = CHGNet.load()
print(f"  模型：✅ 加载成功")
print(f"  设备：{'CUDA' if torch.cuda.is_available() else 'CPU'}")

# 创建 LIG 模型结构
print("\n[3/5] 创建 LIG 模型结构...")

def create_lig_disordered_carbon(n_atoms=72, density=2.0, defect_density=0.1):
    """
    创建 LIG 无序碳结构
    
    参数:
        n_atoms: 原子数
        density: 密度 (g/cm³)
        defect_density: 缺陷密度 (空位比例)
    """
    from ase.build import bulk

    # 从石墨开始
    graphite = bulk('C', 'hex', a=2.46, c=6.71)

    # 扩大超胞
    supercell = graphite * (3, 3, 2)  # 72 原子

    # 引入无序 (模拟激光处理)
    positions = supercell.get_positions()
    np.random.seed(42)

    # 1. 随机位移
    displacement = np.random.normal(0, 0.5, positions.shape)  # 0.5 Å 标准差
    positions += displacement

    # 2. 引入空位 (模拟缺陷)
    n_defects = int(len(supercell) * defect_density)
    defect_indices = np.random.choice(len(supercell), n_defects, replace=False)

    # 创建带缺陷的结构
    from ase import Atoms
    atoms_without_defects = supercell.copy()
    for idx in sorted(defect_indices, reverse=True):
        del supercell[idx]

    supercell.set_positions(positions)

    # 调整密度
    current_volume = supercell.get_volume()
    n_atoms = len(supercell)
    target_volume = n_atoms * 12.01 / (density * 6.022) * 10  # Å³

    scale = (target_volume / current_volume) ** (1/3)
    supercell.set_cell(supercell.get_cell() * scale, scale_atoms=True)

    return supercell, n_defects

# 创建 LIG 结构
lig_structure, n_defects = create_lig_disordered_carbon(
    n_atoms=72,
    density=2.0,
    defect_density=0.1  # 10% 空位
)

print(f"  原子数：{len(lig_structure)}")
print(f"  空位数：{n_defects}")
print(f"  密度：2.0 g/cm³")
print(f"  体积：{lig_structure.get_volume():.2f} Å³")
print(f"  结构：无序碳 + 10% 空位 (模拟 LIG)")

# 设置 CHGNet
lig_structure.calc = chgnet

# 计算初始能量
initial_energy = lig_structure.get_potential_energy()
initial_forces = lig_structure.get_forces()
max_initial_force = np.max(np.abs(initial_forces))

print(f"\n  初始能量：{initial_energy:.4f} eV")
print(f"  每原子：{initial_energy/len(lig_structure):.4f} eV/atom")
print(f"  初始最大力：{max_initial_force:.4f} eV/Å")

# CHGNet 结构弛豫
print("\n[4/5] CHGNet 结构弛豫...")
print("  优化器：FIRE")
print("  收敛标准：fmax < 0.05 eV/Å")
print("  最大步数：200")

relaxer = Relaxer()
relax_results = relaxer.relax(lig_structure, fmax=0.05, steps=200)

relaxed_struct = relax_results['final_structure']
traj = relax_results['trajectory']

# 弛豫后分析
final_energy = relaxed_struct.get_potential_energy()
final_forces = relaxed_struct.get_forces()
max_final_force = np.max(np.abs(final_forces))

energy_change = final_energy - initial_energy

print(f"\n  弛豫完成！")
print(f"  最终能量：{final_energy:.4f} eV")
print(f"  每原子：{final_energy/len(relaxed_struct):.4f} eV/atom")
print(f"  能量变化：{energy_change:.4f} eV ({energy_change/len(relaxed_struct)*1000:.1f} meV/atom)")
print(f"  最终最大力：{max_final_force:.4f} eV/Å")
print(f"  弛豫步数：{len(traj)}")

# 结构分析
print("\n[5/5] 结构分析...")

from ase.geometry import get_distances

positions = relaxed_struct.get_positions()
cell = relaxed_struct.get_cell()
pbc = relaxed_struct.get_pbc()

# C-C 键长分析
distances = []
for i in range(len(relaxed_struct)):
    for j in range(i+1, len(relaxed_struct)):
        d = get_distances(positions[i:i+1], positions[j:j+1], cell, pbc)[0][0]
        if d < 2.0:  # 只考虑近邻
            distances.append(d)

distances = np.array(distances)
print(f"  C-C 键数：{len(distances)}")
print(f"  平均键长：{np.mean(distances):.3f} Å")
print(f"  键长范围：{np.min(distances):.3f} - {np.max(distances):.3f} Å")

# 与理想结构对比
graphite_cc = 1.42
diamond_cc = 1.54

print(f"\n  参考:")
print(f"    石墨 (sp2): {graphite_cc:.3f} Å")
print(f"    金刚石 (sp3): {diamond_cc:.3f} Å")
print(f"    LIG (混合): {np.mean(distances):.3f} Å")

# 杂化分析 (简化)
sp2_ratio = np.sum((distances > 1.38) & (distances < 1.46)) / len(distances) * 100
sp3_ratio = np.sum((distances > 1.50) & (distances < 1.58)) / len(distances) * 100
other_ratio = 100 - sp2_ratio - sp3_ratio

print(f"\n  杂化估算:")
print(f"    sp2 (石墨烯): {sp2_ratio:.1f}%")
print(f"    sp3 (金刚石): {sp3_ratio:.1f}%")
print(f"    其他/缺陷：{other_ratio:.1f}%")

# 保存结果
result = {
    'structure': 'LIG_disordered_carbon_10pct_defects',
    'n_atoms_initial': 72,
    'n_atoms_final': len(relaxed_struct),
    'n_defects': n_defects,
    'density_g_cm3': 2.0,
    'initial_energy_eV': float(initial_energy),
    'final_energy_eV': float(final_energy),
    'energy_change_eV': float(energy_change),
    'energy_change_meV_per_atom': float(energy_change / len(relaxed_struct) * 1000),
    'max_initial_force_eV_A': float(max_initial_force),
    'max_final_force_eV_A': float(max_final_force),
    'relaxation_steps': len(traj),
    'mean_cc_bond_A': float(np.mean(distances)),
    'min_cc_bond_A': float(np.min(distances)),
    'max_cc_bond_A': float(np.max(distances)),
    'hybridization': {
        'sp2_pct': float(sp2_ratio),
        'sp3_pct': float(sp3_ratio),
        'other_pct': float(other_ratio)
    },
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}

output_dir = Path("research/data")
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "chgnet_lig_relax_result.json", 'w') as f:
    json.dump(result, f, indent=2)

# 保存结构
from ase.io import write
write(output_dir / "lig_relaxed_chgnet.xyz", relaxed_struct)
write(output_dir / "lig_relax_traj_chgnet.traj", traj)

print(f"\n  结果已保存:")
print(f"    {output_dir / 'chgnet_lig_relax_result.json'}")
print(f"    {output_dir / 'lig_relaxed_chgnet.xyz'}")
print(f"    {output_dir / 'lig_relax_traj_chgnet.traj'}")

print("\n" + "=" * 60)
print("✅ CHGNet LIG 结构弛豫完成！")
print("=" * 60)

# 与 MACE 对比
print("\nCHGNet vs MACE (LIG 碳材料):")
print("  CHGNet:")
print("    ✅ 碳材料专用训练")
print("    ✅ 缺陷/无序结构更准")
print("    ✅ sp2/sp3 杂化敏感")
print("  MACE:")
print("    ✅ 通用性更强")
print("    ✅ 等变架构")
print("  推荐：CHGNet (主) + MACE (验证)")

# 下一步建议
print("\n下一步建议:")
print("  1. 与 MACE 弛豫结果对比")
print("  2. 运行 AIMD 模拟研究热稳定性")
print("  3. 计算拉曼光谱 (与实验 ID/IG 对比)")
print("  4. 使用 CGCNN/GP 预测电导率")
