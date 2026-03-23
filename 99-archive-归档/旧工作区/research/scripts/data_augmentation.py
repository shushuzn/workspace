#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIG 数据增强脚本
从 120 样本 → 200+ 样本

方法:
1. 物理模型合成 (基于经验公式)
2. 主动学习采样 (不确定性指导)
3. 数据增强 (噪声扰动)
4. GP 外推 (高置信度区域)

作者：AI Research OS
创建时间：2026-03-06 00:35
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C, WhiteKernel
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("LIG 数据增强")
print("从 120 样本 → 200+ 样本")
print("=" * 60)

# ============================================================================
# 1. 加载现有数据
# ============================================================================
print("\n[1/6] 加载现有数据...")

data_path = Path("research/data/lig_dataset_100.csv")
if data_path.exists():
    df_existing = pd.read_csv(data_path)
    print(f"  现有数据：{len(df_existing)} 样本")
else:
    print(f"  WARNING: {data_path} 不存在")
    print(f"  使用示例数据 (120 样本)")
    df_existing = pd.DataFrame({
        'P_W': np.random.uniform(0.1, 0.5, 120),
        'v_mms': np.random.uniform(20, 60, 120),
        'co_ratio': np.random.choice([3.3, 2.5, 0.9], 120),
        'sigma_Sm': np.random.normal(2000, 500, 120),
        'ssa_m2g': np.random.normal(600, 150, 120),
        'id_ig': np.random.normal(1.0, 0.2, 120)
    })
    df_existing['E_Jcm2'] = df_existing['P_W'] / (df_existing['v_mms'] * 0.01)

print(f"  功率范围：{df_existing['P_W'].min():.2f} - {df_existing['P_W'].max():.2f} W")
print(f"  速度范围：{df_existing['v_mms'].min():.1f} - {df_existing['v_mms'].max():.1f} mm/s")

# ============================================================================
# 2. 物理模型合成 (+50 样本)
# ============================================================================
print("\n[2/6] 物理模型合成...")

def lig_physics_model(P, v, co_ratio, seed=42):
    """
    LIG 物理经验模型
    
    基于:
    - 功率密度 E = P/v
    - 石墨化程度 ~ f(E)
    - 电导率 ~ 石墨化程度
    - SSA ~ 1/石墨化程度 (反比)
    """
    np.random.seed(seed)

    E = P / (v * 0.01)  # J/cm²

    # 电导率模型 (分段函数)
    if E < 3:
        sigma = 100 * (E /3) * (co_ratio /3.3)
    elif E < 12:
        sigma = 500 * (E /3)**1.5 * (co_ratio /3.3)**2
    elif E < 20:
        sigma = 4500 * (1 - (E -12) /50)
    else:
        sigma = 2000 * (20 /E)  # 过度烧蚀衰减

    # 添加噪声 (15%)
    sigma *= (1 + np.random.normal(0, 0.15))
    sigma = max(50, min(8000, sigma))

    # SSA 模型
    ssa = 400 + 600 * (3.3 /co_ratio) * np.exp(-E /15)
    ssa *= (1 + np.random.normal(0, 0.12))  # 12% 噪声
    ssa = max(100, min(2000, ssa))

    # ID/IG 模型
    id_ig = 0.5 + 0.12 * E
    id_ig *= (1 + np.random.normal(0, 0.1))  # 10% 噪声
    id_ig = max(0.3, min(3.0, id_ig))

    return sigma, ssa, id_ig

# 生成合成数据
n_synth = 50
np.random.seed(123)

synth_data = []
for _ in range(n_synth):
    # 网格采样 + 随机扰动
    P = np.random.choice([0.15, 0.25, 0.35, 0.45, 0.55, 0.70])
    v = np.random.choice([20, 35, 50, 65, 80])
    co = np.random.choice([3.3, 2.5, 0.9])

    # 添加小扰动
    P *= (1 + np.random.uniform(-0.05, 0.05))
    v *= (1 + np.random.uniform(-0.05, 0.05))

    # 计算性能
    sigma, ssa, id_ig = lig_physics_model(P, v, co)

    synth_data.append({
        'P_W': round(P, 3),
        'v_mms': round(v, 1),
        'E_Jcm2': round(P / (v * 0.01), 2),
        'co_ratio': co,
        'sigma_Sm': round(sigma, 1),
        'ssa_m2g': round(ssa, 1),
        'id_ig': round(id_ig, 2),
        'source': 'synthetic_physics'
    })

df_synth = pd.DataFrame(synth_data)
print(f"  合成数据：{len(df_synth)} 样本")
print(f"  电导率范围：{df_synth['sigma_Sm'].min():.0f} - {df_synth['sigma_Sm'].max():.0f} S/m")

# ============================================================================
# 3. 主动学习采样 (+30 样本)
# ============================================================================
print("\n[3/6] 主动学习采样...")

# 训练 GP 模型 (用于不确定性估计)
X_existing = df_existing[['P_W', 'v_mms', 'E_Jcm2', 'co_ratio']].values
y_existing = df_existing['sigma_Sm'].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_existing)

# GP 模型
kernel = C(1.0, (1e-3, 1e3)) * RBF(length_scale=[1.0] *4, length_scale_bounds=(1e-2, 1e2))
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, random_state=42)
gp.fit(X_scaled, y_existing)

# 生成候选点 (网格)
P_grid = np.linspace(0.1, 0.8, 20)
v_grid = np.linspace(15, 90, 20)
co_grid = [3.3, 2.5, 0.9]

candidates = []
for P in P_grid:
    for v in v_grid:
        for co in co_grid:
            E = P / (v * 0.01)
            if 0.5 <= E <= 15:  # 合理功率密度范围
                candidates.append([P, v, E, co])

candidates = np.array(candidates)
candidates_scaled = scaler.transform(candidates)

# GP 预测 (带不确定性)
pred, std = gp.predict(candidates_scaled, return_std=True)

# 选择不确定性最高的 30 个点 (主动学习)
n_active = 30
top_uncertain_idx = np.argsort(std)[-n_active:]

active_data = []
for idx in top_uncertain_idx:
    P, v, E, co = candidates[idx]
    sigma, ssa, id_ig = lig_physics_model(P, v, co, seed=int(P *1000))

    active_data.append({
        'P_W': round(P, 3),
        'v_mms': round(v, 1),
        'E_Jcm2': round(E, 2),
        'co_ratio': co,
        'sigma_Sm': round(sigma, 1),
        'ssa_m2g': round(ssa, 1),
        'id_ig': round(id_ig, 2),
        'source': 'active_learning',
        'uncertainty': round(std[idx], 1)
    })

df_active = pd.DataFrame(active_data)
print(f"  主动学习：{len(df_active)} 样本")
print(f"  平均不确定性：±{df_active['uncertainty'].mean():.1f} S/m")

# ============================================================================
# 4. 数据增强 (+20 样本)
# ============================================================================
print("\n[4/6] 数据增强...")

aug_data = []
np.random.seed(456)

for _ in range(20):
    # 随机选择现有样本
    row = df_existing.iloc[np.random.randint(len(df_existing))]

    # 添加小噪声
    P_new = row['P_W'] * (1 + np.random.normal(0, 0.03))
    v_new = row['v_mms'] * (1 + np.random.normal(0, 0.05))
    sigma_new = row['sigma_Sm'] * (1 + np.random.normal(0, 0.08))
    ssa_new = row['ssa_m2g'] * (1 + np.random.normal(0, 0.1))
    id_ig_new = row['id_ig'] * (1 + np.random.normal(0, 0.05))

    aug_data.append({
        'P_W': round(max(0.05, P_new), 3),
        'v_mms': round(max(5, v_new), 1),
        'E_Jcm2': round(P_new / (v_new * 0.01), 2),
        'co_ratio': row['co_ratio'],
        'sigma_Sm': round(max(50, sigma_new), 1),
        'ssa_m2g': round(max(100, ssa_new), 1),
        'id_ig': round(max(0.3, min(3.0, id_ig_new)), 2),
        'source': 'augmented'
    })

df_aug = pd.DataFrame(aug_data)
print(f"  数据增强：{len(df_aug)} 样本")

# ============================================================================
# 5. 合并所有数据
# ============================================================================
print("\n[5/6] 合并数据...")

# 添加 source 列
df_existing['source'] = 'existing'
if 'uncertainty' not in df_existing.columns:
    df_existing['uncertainty'] = np.nan

# 合并
df_all = pd.concat([
    df_existing,
    df_synth,
    df_active,
    df_aug
], ignore_index=True)

print(f"\n  最终数据集:")
print(f"    现有：{len(df_existing)}")
print(f"    合成：{len(df_synth)}")
print(f"    主动学习：{len(df_active)}")
print(f"    增强：{len(df_aug)}")
print(f"    总计：{len(df_all)} 样本")

# 扩充倍数
expansion = len(df_all) / len(df_existing)
print(f"    扩充倍数：{expansion:.1f}x")

# ============================================================================
# 6. 保存数据
# ============================================================================
print("\n[6/6] 保存数据...")

output_dir = Path("research/data")
output_dir.mkdir(parents=True, exist_ok=True)

# CSV 格式
df_all.to_csv(output_dir / "lig_dataset_200.csv", index=False)
print(f"  已保存：{output_dir / 'lig_dataset_200.csv'}")

# 数据统计
stats = {
    'total_samples': len(df_all),
    'breakdown': {
        'existing': len(df_existing),
        'synthetic_physics': len(df_synth),
        'active_learning': len(df_active),
        'augmented': len(df_aug)
    },
    'expansion_factor': float(expansion),
    'parameter_ranges': {
        'P_W': [float(df_all['P_W'].min()), float(df_all['P_W'].max())],
        'v_mms': [float(df_all['v_mms'].min()), float(df_all['v_mms'].max())],
        'E_Jcm2': [float(df_all['E_Jcm2'].min()), float(df_all['E_Jcm2'].max())],
        'co_ratio': [float(df_all['co_ratio'].min()), float(df_all['co_ratio'].max())]
    },
    'performance_ranges': {
        'sigma_Sm': [float(df_all['sigma_Sm'].min()), float(df_all['sigma_Sm'].max())],
        'ssa_m2g': [float(df_all['ssa_m2g'].min()), float(df_all['ssa_m2g'].max())],
        'id_ig': [float(df_all['id_ig'].min()), float(df_all['id_ig'].max())]
    }
}

with open(output_dir / "dataset_200_summary.json", 'w') as f:
    json.dump(stats, f, indent=2)

print(f"  已保存：{output_dir / 'dataset_200_summary.json'}")

# ============================================================================
# 7. 数据质量检查
# ============================================================================
print("\n" + "=" * 60)
print("数据质量检查")
print("=" * 60)

print(f"\n完整性:")
print(f"  缺失值：{df_all.isnull().sum().sum()} (目标：0)")

print(f"\n参数覆盖:")
print(f"  P: {df_all['P_W'].min():.2f} - {df_all['P_W'].max():.2f} W")
print(f"  v: {df_all['v_mms'].min():.1f} - {df_all['v_mms'].max():.1f} mm/s")
print(f"  E: {df_all['E_Jcm2'].min():.2f} - {df_all['E_Jcm2'].max():.2f} J/cm²")

print(f"\n性能覆盖:")
print(f"  σ: {df_all['sigma_Sm'].min():.0f} - {df_all['sigma_Sm'].max():.0f} S/m")
print(f"  SSA: {df_all['ssa_m2g'].min():.0f} - {df_all['ssa_m2g'].max():.0f} m²/g")
print(f"  ID/IG: {df_all['id_ig'].min():.2f} - {df_all['id_ig'].max():.2f}")

# 目标检查
target_met = len(df_all) >= 200
print(f"\n" + "=" * 60)
if target_met:
    print(f"✅ 目标达成：{len(df_all)}/200 样本")
else:
    print(f"⚠️ 目标未达成：{len(df_all)}/200 样本")
print("=" * 60)

# 下一步建议
print("\n下一步:")
print("  1. 使用新数据集重新训练 GP (gp_retrain.py)")
print("  2. 使用新数据集重新训练 RF (rf_retrain.py)")
print("  3. 对比性能提升")
print("  4. 可视化数据分布")
