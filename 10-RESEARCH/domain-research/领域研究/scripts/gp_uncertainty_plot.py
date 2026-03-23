#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GP 不确定性可视化
工艺参数 - 性能响应面 + 置信区间

作者：AI Research OS
创建时间：2026-03-06 00:15
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import joblib

print("=" * 60)
print("GP 不确定性可视化")
print("=" * 60)

# 加载模型
print("\n加载模型...")
gp = joblib.load("research/models/gp_sigma.joblib")
scaler = joblib.load("research/models/gp_scaler.joblib")

# 加载数据
data_path = Path("research/data/lig_dataset_100.csv")
if data_path.exists():
    df = pd.read_csv(data_path)
    print(f"  数据：{len(df)} 样本")
else:
    print("  使用示例数据")
    df = pd.DataFrame({
        'P_W': np.random.uniform(0.1, 0.5, 100),
        'v_mms': np.random.uniform(20, 60, 100),
        'co_ratio': [3.3] * 100,
        'sigma_Sm': np.random.normal(2000, 500, 100)
    })
    df['E_Jcm2'] = df['P_W'] / (df['v_mms'] * 0.01)

# 创建网格
print("\n创建响应面...")
P_range = np.linspace(0.1, 0.5, 30)
v_range = np.linspace(20, 60, 30)
P_mesh, v_mesh = np.meshgrid(P_range, v_range)

# 固定其他参数
E_mesh = P_mesh / (v_mesh * 0.01)
co_ratio = 3.3

# 准备输入
X_grid = np.column_stack([
    P_mesh.ravel(),
    v_mesh.ravel(),
    E_mesh.ravel(),
    [co_ratio] * len(P_mesh.ravel())
])

X_grid_scaled = scaler.transform(X_grid)

# GP 预测 (带不确定性)
sigma_pred, sigma_std = gp.predict(X_grid_scaled, return_std=True)

# 重塑
sigma_mesh = sigma_pred.reshape(P_mesh.shape)
sigma_unc_mesh = sigma_std.reshape(P_mesh.shape)

# 绘图
print("\n生成可视化...")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. 响应面
ax = axes[0, 0]
contour = ax.contourf(P_mesh, v_mesh, sigma_mesh, levels=20, cmap='viridis')
ax.set_xlabel('激光功率 (W)')
ax.set_ylabel('扫描速度 (mm/s)')
ax.set_title('电导率响应面')
plt.colorbar(contour, ax=ax, label='电导率 (S/m)')

# 2. 不确定性
ax = axes[0, 1]
contour = ax.contourf(P_mesh, v_mesh, sigma_unc_mesh, levels=20, cmap='hot')
ax.set_xlabel('激光功率 (W)')
ax.set_ylabel('扫描速度 (mm/s)')
ax.set_title('预测不确定性 (标准差)')
plt.colorbar(contour, ax=ax, label='σ (S/m)')

# 3. 不确定性 vs 数据密度
ax = axes[1, 0]
ax.scatter(df['P_W'], df['v_mms'], alpha=0.6, s=50, c='blue', label='训练数据')
ax.set_xlabel('激光功率 (W)')
ax.set_ylabel('扫描速度 (mm/s)')
ax.set_title('数据分布')
ax.legend()
ax.grid(True, alpha=0.3)

# 4. 剖面图
ax = axes[1, 1]
v_fixed = 30  # 固定速度
P剖面 = np.linspace(0.1, 0.5, 50)
E 剖面 = P 剖面 / (v_fixed * 0.01)
X 剖面 = np.column_stack([P 剖面，[v_fixed]*len(P 剖面), E 剖面，[3.3]*len(P 剖面)])
X 剖面_scaled = scaler.transform(X 剖面)
sigma 剖面，sigma_std 剖面 = gp.predict(X 剖面_scaled, return_std=True)

ax.plot(P 剖面，sigma 剖面，'b-', linewidth=2, label='预测')
ax.fill_between(P 剖面，
                sigma 剖面 - 2*sigma_std 剖面，
                sigma 剖面 + 2*sigma_std 剖面，
                alpha=0.3, label='95% 置信区间')
ax.scatter(df[df['v_mms'].between(28, 32)]['P_W'],
           df[df['v_mms'].between(28, 32)]['sigma_Sm'],
           alpha=0.6, s=50, c='red', label='实验数据')
ax.set_xlabel('激光功率 (W)')
ax.set_ylabel('电导率 (S/m)')
ax.set_title(f'剖面图 (v={v_fixed} mm/s)')
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()

# 保存
output_dir = Path("research/figures")
output_dir.mkdir(parents=True, exist_ok=True)
plt.savefig(output_dir / "gp_uncertainty_visualization.png", dpi=300, bbox_inches='tight')
print(f"  已保存：{output_dir / 'gp_uncertainty_visualization.png'}")

plt.show()

print("\n✅ 可视化完成！")
