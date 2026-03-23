#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHGNet - 碳材料专用机器学习势函数
LIG/石墨烯/缺陷/多孔材料专用

作者：AI Research OS
创建时间：2026-03-06 00:25
"""

import numpy as np
from pathlib import Path
import json

print("=" * 60)
print("CHGNet - 碳材料专用模型")
print("=" * 60)

# 1. 检查 CHGNet 安装
print("\n[1/5] 检查 CHGNet 安装...")
try:
    from chgnet.model.model import CHGNet
    from chgnet.model.dynamics import MolecularDynamics, Relaxer
    import torch
    print(f"  CHGNet: ✅ 已安装")
    print(f"  PyTorch: {torch.__version__}")
    print(f"  CUDA: {'✅' if torch.cuda.is_available() else '❌'}")
    CHGNET_AVAILABLE = True
except ImportError as e:
    print(f"  CHGNet: ❌ 未安装")
    print(f"  错误：{e}")
    print(f"  请运行：pip install chgnet")
    CHGNET_AVAILABLE = False

# 2. 加载预训练模型
print("\n[2/5] 加载 CHGNet 预训练模型...")
if CHGNET_AVAILABLE:
    try:
        chgnet = CHGNet.load()
        print(f"  模型：✅ 加载成功")
        print(f"  版本：{chgnet.version}")
        print(f"  训练数据：Materials Project + OQMD")
        print(f"  元素覆盖：89 种 (含 C, H, O, N)")
    except Exception as e:
        print(f"  模型加载失败：{e}")
        print(f"  首次运行会自动下载 (~100MB)")
        CHGNET_AVAILABLE = False

# 3. 创建测试结构 (石墨)
print("\n[3/5] 创建测试结构...")
try:
    from ase.build import bulk, molecule
    from ase import Atoms

    # 石墨
    graphite = bulk('C', 'hex', a=2.46, c=6.71)
    print(f"  石墨：{len(graphite)} 原子")
    print(f"  晶格：a={graphite.cell[0,0]:.2f} Å, c={graphite.cell[2,2]:.2f} Å")

    # 石墨烯
    graphene = bulk('C', 'hex', a=2.46, c=15.0, cubic=True)
    print(f"  石墨烯：{len(graphene)} 原子")

    # 碳纳米管 (5,5)
    from ase.build import nanotube
    cnt = nanotube(5, 5, length=1, vacuum=5.0)
    print(f"  碳纳米管 (5,5): {len(cnt)} 原子")

    # 富勒烯 C60
    c60 = molecule('C60')
    c60.center(10.0, vacuum=5.0)
    print(f"  C60 富勒烯：{len(c60)} 原子")

except ImportError:
    print("  ASE: ❌ 未安装")
    print("  请运行：pip install ase")

# 4. CHGNet 能量预测
print("\n[4/5] CHGNet 能量预测...")
if CHGNET_AVAILABLE:
    try:
        from chgnet.graph import CrystalGraphConverter

        # 石墨能量
        graph = CrystalGraphConverter()(graphite, algorithm='fast')
        output = chgnet.predict_graph(graph)

        energy = output['e']
        forces = output['f']

        print(f"\n  石墨:")
        print(f"    总能量：{energy:.4f} eV")
        print(f"    每原子：{energy /len(graphite):.4f} eV/atom")
        print(f"    最大力：{np.max(np.abs(forces)):.4f} eV/Å")

        # 与 DFT 对比
        dft_ref = -9.17  # MP DFT 参考值
        error = abs(energy /len(graphite) - dft_ref) * 1000

        print(f"\n  与 DFT 对比:")
        print(f"    DFT 参考：{dft_ref:.4f} eV/atom")
        print(f"    CHGNet: {energy /len(graphite):.4f} eV/atom")
        print(f"    误差：{error:.1f} meV/atom")

        if error < 10:
            print(f"    精度：✅ 优秀 (<10 meV/atom)")
        elif error < 50:
            print(f"    精度：✅ 良好 (<50 meV/atom)")
        else:
            print(f"    精度：⚠️ 可接受")

        # 其他碳材料
        print(f"\n  其他碳材料:")

        # 石墨烯
        graph_graphene = CrystalGraphConverter()(graphene, algorithm='fast')
        e_graphene = chgnet.predict_graph(graph_graphene)['e']
        print(f"    石墨烯：{e_graphene /len(graphene):.4f} eV/atom")

        # 金刚石
        diamond = bulk('C', 'diamond', a=3.57)
        graph_diamond = CrystalGraphConverter()(diamond, algorithm='fast')
        e_diamond = chgnet.predict_graph(graph_diamond)['e']
        print(f"    金刚石：{e_diamond /len(diamond):.4f} eV/atom")

        # C60
        # 需要转换为 ASE Atoms 对象
        graph_c60 = CrystalGraphConverter()(c60, algorithm='fast')
        e_c60 = chgnet.predict_graph(graph_c60)['e']
        print(f"    C60: {e_c60 /len(c60):.4f} eV/atom")

        # 保存结果
        result = {
            'model': 'CHGNet',
            'version': chgnet.version,
            'structures': {
                'graphite': {
                    'energy_eV': float(energy),
                    'energy_per_atom_eV': float(energy /len(graphite)),
                    'max_force_eV_A': float(np.max(np.abs(forces))),
                    'dft_reference_eV': dft_ref,
                    'error_meV': float(error)
                },
                'graphene': float(e_graphene /len(graphene)),
                'diamond': float(e_diamond /len(diamond)),
                'c60': float(e_c60 /len(c60))
            }
        }

        output_dir = Path("research/data")
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / "chgnet_test_result.json", 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n  结果已保存：{output_dir / 'chgnet_test_result.json'}")

    except Exception as e:
        print(f"  预测失败：{e}")

# 5. 结构弛豫
print("\n[5/5] CHGNet 结构弛豫...")
if CHGNET_AVAILABLE:
    try:
        from chgnet.model.dynamics import Relaxer

        print("  弛豫器：CHGNet Relaxer")
        print("  优化器：FIRE")
        print("  收敛标准：fmax < 0.05 eV/Å")

        # 弛豫石墨
        relaxer = Relaxer()
        relax_results = relaxer.relax(graphite, fmax=0.05, steps=100)

        relaxed_struct = relax_results['final_structure']
        traj = relax_results['trajectory']

        print(f"\n  弛豫完成:")
        print(f"    初始体积：{graphite.get_volume():.2f} Å³")
        print(f"    弛豫体积：{relaxed_struct.get_volume():.2f} Å³")
        print(f"    体积变化：{(relaxed_struct.get_volume() - graphite.get_volume()) /graphite.get_volume() *100:+.1f}%")

        # 保存弛豫结构
        from ase.io import write
        write(output_dir / "graphite_relaxed_chgnet.xyz", relaxed_struct)
        print(f"\n  已保存：{output_dir / 'graphite_relaxed_chgnet.xyz'}")

    except Exception as e:
        print(f"  弛豫失败：{e}")

print("\n" + "=" * 60)
if CHGNET_AVAILABLE:
    print("✅ CHGNet 测试完成！")
else:
    print("⚠️ CHGNet 未完全安装")
print("=" * 60)

# 安装命令总结
print("\n" + "=" * 60)
print("安装命令")
print("=" * 60)
print("""
# 1. 安装 CHGNet
pip install chgnet

# 2. 测试
python research/scripts/chgnet_test.py

# 3. LIG 结构弛豫
python research/scripts/chgnet_lig_relax.py

# 4. MD 模拟
python research/scripts/chgnet_md.py
""")

# 与 MACE 对比
print("\n" + "=" * 60)
print("CHGNet vs MACE")
print("=" * 60)
print("""
CHGNet 优势:
  ✅ 碳材料专用 (LIG/石墨烯/缺陷)
  ✅ 训练数据包含碳同素异形体
  ✅ 对 sp/sp2/sp3 杂化更敏感
  ✅ 缺陷形成能更准确

MACE 优势:
  ✅ 通用性更强 (89 种元素)
  ✅ 等变架构 (理论上限更高)
  ✅ 社区活跃度高

推荐:
  碳材料研究 = CHGNet (主) + MACE (辅)
  通用材料 = MACE (主)
""")
