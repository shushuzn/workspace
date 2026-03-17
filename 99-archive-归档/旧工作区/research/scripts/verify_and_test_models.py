#!/usr/bin/env python3
"""
验证 MACE 和 CHGNet 模型并测试迁移学习
"""
import torch
from pathlib import Path

print("=" * 70)
print("验证 MACE 和 CHGNet 模型")
print("=" * 70)

# ============================================================================
# 1. 验证 MACE-MP
# ============================================================================
print("\n[1/3] 验证 MACE-MP...")

try:
    from mace.calculators import mace_mp
    from ase.build import bulk
    
    # 加载 MACE-MP 模型
    print("  加载 MACE-MP 模型...")
    mace_calc = mace_mp(model="small", device="cpu")
    print("  [OK] MACE-MP 加载成功")
    
    # 测试：计算石墨能量
    print("  测试：计算石墨能量...")
    graphite = bulk('C', 'hex', a=2.46, c=6.71)
    graphite.calc = mace_calc
    energy = graphite.get_potential_energy()
    forces = graphite.get_forces()
    
    print(f"  [OK] 石墨能量：{energy:.4f} eV")
    print(f"  [OK] 每原子能量：{energy/len(graphite):.4f} eV/atom")
    print(f"  [OK] 最大力：{max(abs(forces.flatten())):.4f} eV/A")
    
    # 与 DFT 对比
    dft_ref = -9.17  # MP DFT 参考值
    error = abs(energy/len(graphite) - dft_ref) * 1000
    print(f"\n  与 DFT 对比:")
    print(f"    DFT 参考：{dft_ref:.4f} eV/atom")
    print(f"    MACE-MP: {energy/len(graphite):.4f} eV/atom")
    print(f"    误差：{error:.1f} meV/atom")
    
    if error < 10:
        print(f"    [TOP] 精度优秀！(<10 meV/atom)")
    elif error < 50:
        print(f"    [OK] 精度良好！(<50 meV/atom)")
    else:
        print(f"    [WARN] 误差较大")
    
    mace_available = True
    
except Exception as e:
    print(f"  [ERROR] MACE 验证失败：{e}")
    mace_available = False

# ============================================================================
# 2. 验证 CHGNet
# ============================================================================
print("\n[2/3] 验证 CHGNet...")

try:
    import matgl
    from matgl.ext.ase import PESCalculator
    from ase.build import molecule
    
    # 尝试不同的 CHGNet 模型名称
    model_names = [
        "CHGNet-MP-2024.2.13-PBE",
        "CHGNet-MP-2023.12.9-PBE",
        "CHGNet-0.3.0",
    ]
    
    chgnet_model = None
    for model_name in model_names:
        try:
            print(f"  尝试加载：{model_name}...")
            chgnet_model = matgl.load_model(model_name)
            print(f"  [OK] 加载成功：{model_name}")
            break
        except Exception as e:
            print(f"  [WARN] {model_name} 失败：{e}")
    
    if chgnet_model:
        # 测试：计算 C60 能量
        print("  测试：计算 C60 能量...")
        c60 = molecule('C60')
        c60.calc = PESCalculator(chgnet_model)
        energy = c60.get_potential_energy()
        
        print(f"  [OK] C60 能量：{energy:.4f} eV")
        print(f"  [OK] 每原子能量：{energy/len(c60):.4f} eV/atom")
        
        chgnet_available = True
    else:
        print("  [ERROR] 所有 CHGNet 模型都失败")
        print("  [INFO] 请手动下载模型")
        chgnet_available = False
    
except Exception as e:
    print(f"  [ERROR] CHGNet 验证失败：{e}")
    chgnet_available = False

# ============================================================================
# 3. 生成验证报告
# ============================================================================
print("\n[3/3] 生成验证报告...")

import json
from datetime import datetime

report = {
    'timestamp': datetime.now().isoformat(),
    'mace_mp': {
        'available': mace_available,
        'model_path': 'C:\\Users\\***\\.cache\\mace\\20231210mace128L0_energy_epoch249model',
        'test_energy_per_atom': energy/len(graphite) if mace_available else None,
        'error_vs_dft_meV': error if mace_available else None
    },
    'chgnet': {
        'available': chgnet_available,
        'test_energy_per_atom': energy/len(c60) if chgnet_available else None
    },
    'next_steps': [
        '运行 MACE 迁移学习微调',
        '运行 CHGNet 迁移学习微调',
        '集成预测 (GP + MACE + CHGNet)'
    ]
}

output_path = Path("research/models/model_verification_report.json")
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"  [OK] 验证报告已保存：{output_path}")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 70)
print("验证完成！")
print("=" * 70)

print(f"\n模型状态:")
print(f"  MACE-MP: {'[OK] 可用' if mace_available else '[ERROR] 不可用'}")
print(f"  CHGNet: {'[OK] 可用' if chgnet_available else '[WARN] 部分可用'}")

if mace_available:
    print(f"\n[OK] MACE-MP 已就绪！可以开始迁移学习！")
    print(f"下一步：python research/scripts/mace_finetune.py")
else:
    print(f"\n[WARN] MACE-MP 有问题，请检查安装")

if chgnet_available:
    print(f"[OK] CHGNet 已就绪！可以开始迁移学习！")
    print(f"下一步：python research/scripts/chgnet_finetune.py")
else:
    print(f"[WARN] CHGNet 需要手动下载模型")

print("=" * 70)
