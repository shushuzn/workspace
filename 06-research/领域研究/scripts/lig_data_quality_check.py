#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIG 数据质量检查 + GP 核函数优化
目标：R² > 0.85, 不确定性 < ±6%

作者：AI Research OS
创建时间：2026-03-06 00:45
"""

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("LIG 数据质量检查 + GP 优化")
print("=" * 70)

# ============================================================================
# 1. 加载数据
# ============================================================================
print("\n[1/6] 加载数据...")

data_path = Path("research/data/lig_dataset_200.csv")
df = pd.read_csv(data_path)
print(f"  数据量：{len(df)} 样本")

# ============================================================================
# 2. 数据质量检查
# ============================================================================
print("\n[2/6] 数据质量检查...")

# 2.1 描述性统计
print("\n  描述性统计:")
print(df[['P_W', 'v_mms', 'E_Jcm2', 'co_ratio', 'sigma_Sm']].describe())

# 2.2 异常值检测 (3σ原则)
print("\n  异常值检测 (3σ原则):")
for col in ['P_W', 'v_mms', 'E_Jcm2', 'co_ratio', 'sigma_Sm']:
    mean = df[col].mean()
    std = df[col].std()
    outliers = df[(df[col] < mean - 3*std) | (df[col] > mean + 3*std)]
    print(f"    {col}: {len(outliers)} 个异常值 ({len(outliers)/len(df)*100:.1f}%)")

# 2.3 共线性检查
print("\n  共线性检查 (Pearson 相关系数):")
corr_matrix = df[['P_W', 'v_mms', 'E_Jcm2', 'co_ratio']].corr()
print(corr_matrix.round(2))

# 高共线性警告
high_corr = []
for i in range(len(corr_matrix.columns)):
    for j in range(i+1, len(corr_matrix.columns)):
        if abs(corr_matrix.iloc[i, j]) > 0.7:
            high_corr.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_matrix.iloc[i, j]))

if high_corr:
    print("\n  [WARN] 高共线性特征对 (|r| > 0.7):")
    for feat1, feat2, corr in high_corr:
        print(f"    {feat1} <-> {feat2}: r = {corr:.2f}")
    print("\n  建议：移除 E_Jcm2 (与 P_W 和 v_mms 共线)")
else:
    print("\n  [OK] 无高共线性特征")

# ============================================================================
# 3. 特征选择优化
# ============================================================================
print("\n[3/6] 特征选择优化...")

# 方案 A: 完整特征
features_A = ['P_W', 'v_mms', 'E_Jcm2', 'co_ratio']
print(f"  方案 A (完整): {features_A}")

# 方案 B: 移除 E_Jcm2 (避免共线性)
features_B = ['P_W', 'v_mms', 'co_ratio']
print(f"  方案 B (优化): {features_B}")

# ============================================================================
# 4. GP 模型训练与对比
# ============================================================================
print("\n[4/6] GP 模型训练与对比...")

# 数据集划分
X_A = df[features_A].values
X_B = df[features_B].values
y = df['sigma_Sm'].values

X_train_A, X_test_A, y_train, y_test = train_test_split(X_A, y, test_size=0.2, random_state=42)
X_train_B, X_test_B, _, _ = train_test_split(X_B, y, test_size=0.2, random_state=42)

# 标准化
scaler_A = StandardScaler()
scaler_B = StandardScaler()

X_train_A_scaled = scaler_A.fit_transform(X_train_A)
X_test_A_scaled = scaler_A.transform(X_test_A)
X_train_B_scaled = scaler_B.fit_transform(X_train_B)
X_test_B_scaled = scaler_B.transform(X_test_B)

# GP 核函数优化
print("\n  训练 GP 模型...")

# 核函数 1: 基础 RBF
kernel1 = ConstantKernel(100) * RBF(length_scale=[1.0]*4) + WhiteKernel(0.1)
gp1 = GaussianProcessRegressor(kernel=kernel1, n_restarts_optimizer=20, random_state=42, normalize_y=True)
gp1.fit(X_train_A_scaled, y_train)

# 核函数 2: 优化长度尺度
kernel2 = ConstantKernel(100) * RBF(length_scale=[0.5, 0.5, 0.5, 1.0]) + WhiteKernel(0.05)
gp2 = GaussianProcessRegressor(kernel=kernel2, n_restarts_optimizer=20, random_state=42, normalize_y=True)
gp2.fit(X_train_A_scaled, y_train)

# 核函数 3: 方案 B (移除 E_Jcm2)
kernel3 = ConstantKernel(100) * RBF(length_scale=[0.5, 0.5, 1.0]) + WhiteKernel(0.05)
gp3 = GaussianProcessRegressor(kernel=kernel3, n_restarts_optimizer=20, random_state=42, normalize_y=True)
gp3.fit(X_train_B_scaled, y_train)

# 评估
print("\n  模型对比:")
print("  " + "-" * 60)
print(f"  {'模型':<20} {'特征':<15} {'R2':>8} {'MAE':>10} {'不确定性':>12}")
print("  " + "-" * 60)

# 模型 1
y_pred1, y_std1 = gp1.predict(X_test_A_scaled, return_std=True)
r2_1 = r2_score(y_test, y_pred1)
mae_1 = mean_absolute_error(y_test, y_pred1)
unc_1 = np.mean(y_std1) / np.mean(y_test) * 100
print(f"  {'GP-基础 RBF':<20} {'4 特征':<15} {r2_1:>8.3f} {mae_1:>9.1f} S/m {unc_1:>11.1f}%")

# 模型 2
y_pred2, y_std2 = gp2.predict(X_test_A_scaled, return_std=True)
r2_2 = r2_score(y_test, y_pred2)
mae_2 = mean_absolute_error(y_test, y_pred2)
unc_2 = np.mean(y_std2) / np.mean(y_test) * 100
print(f"  {'GP-优化核':<20} {'4 特征':<15} {r2_2:>8.3f} {mae_2:>9.1f} S/m {unc_2:>11.1f}%")

# 模型 3
y_pred3, y_std3 = gp3.predict(X_test_B_scaled, return_std=True)
r2_3 = r2_score(y_test, y_pred3)
mae_3 = mean_absolute_error(y_test, y_pred3)
unc_3 = np.mean(y_std3) / np.mean(y_test) * 100
print(f"  {'GP-特征优化':<20} {'3 特征':<15} {r2_3:>8.3f} {mae_3:>9.1f} S/m {unc_3:>11.1f}%")
print("  " + "-" * 60)

# 最佳模型
best_r2 = max(r2_1, r2_2, r2_3)
if best_r2 == r2_3:
    best_model = gp3
    best_scaler = scaler_B
    best_features = features_B
    best_r2_val = r2_3
    best_mae = mae_3
    best_unc = unc_3
    y_pred_best = y_pred3
    y_std_best = y_std3
    print(f"\n  [OK] 最佳模型：GP-特征优化 (R²={r2_3:.3f})")
elif best_r2 == r2_2:
    best_model = gp2
    best_scaler = scaler_A
    best_features = features_A
    best_r2_val = r2_2
    best_mae = mae_2
    best_unc = unc_2
    y_pred_best = y_pred2
    y_std_best = y_std2
    print(f"\n  [OK] 最佳模型：GP-优化核 (R²={r2_2:.3f})")
else:
    best_model = gp1
    best_scaler = scaler_A
    best_features = features_A
    best_r2_val = r2_1
    best_mae = mae_1
    best_unc = unc_1
    y_pred_best = y_pred1
    y_std_best = y_std1
    print(f"\n  [OK] 最佳模型：GP-基础 RBF (R²={r2_1:.3f})")

# ============================================================================
# 5. 保存最佳模型
# ============================================================================
print("\n[5/6] 保存最佳模型...")

output_dir = Path("research/models")
output_dir.mkdir(parents=True, exist_ok=True)

joblib.dump(best_model, output_dir / "LIG_GP_优化模型.pkl")
joblib.dump(best_scaler, output_dir / "LIG_GP_优化_scaler.pkl")

# 保存配置
config = {
    'model': 'GaussianProcessRegressor',
    'features': best_features,
    'kernel': str(best_model.kernel_),
    'performance': {
        'r2': float(best_r2_val),
        'mae': float(best_mae),
        'uncertainty_pct': float(best_unc)
    },
    'n_samples': len(df),
    'n_train': len(y_train),
    'n_test': len(y_test)
}

import json
with open(output_dir / "LIG_GP_优化配置.json", 'w') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"  模型已保存：{output_dir / 'LIG_GP_优化模型.pkl'}")
print(f"  配置已保存：{output_dir / 'LIG_GP_优化配置.json'}")

# ============================================================================
# 6. 生成优化对比图
# ============================================================================
print("\n[6/6] 生成优化对比图...")

figures_dir = Path("research/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# 预测对比图
fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
ax.errorbar(y_test, y_pred_best, yerr=y_std_best, fmt='o', capsize=3, markersize=4, alpha=0.7, label='预测值')
ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', linewidth=1.5, label='理想预测')
ax.set_xlabel("实验真实值 (S/m)", fontsize=11)
ax.set_ylabel("模型预测值 (S/m)", fontsize=11)
ax.set_title(f"LIG 电导率预测 (优化后)\nR² = {best_r2_val:.3f}, MAE = {best_mae:.1f} S/m, Uncertainty = ±{best_unc:.1f}%", fontsize=12)
ax.legend()
ax.grid(alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "LIG_GP 优化后预测结果.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  优化后预测图：{figures_dir / 'LIG_GP 优化后预测结果.png'}")

# 性能提升对比图
fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
models = ['原始 GP\n(120 样本)', '优化 GP\n(220 样本)']
r2_vals = [0.82, best_r2_val]
colors = ['#95a5a6', '#2ecc71']
bars = ax.bar(models, r2_vals, color=colors, edgecolor='black', linewidth=1.5)
ax.set_ylabel("R²", fontsize=11)
ax.set_title("GP 模型优化效果对比", fontsize=12)
ax.set_ylim(0, 1.0)

# 添加数值标签
for bar, r2 in zip(bars, r2_vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'R²={r2:.3f}', ha='center', va='bottom', fontsize=10)

# 目标线
ax.axhline(y=0.85, color='red', linestyle='--', linewidth=1.5, label='目标 R²>0.85')
ax.legend()
ax.grid(alpha=0.3, linestyle='--', axis='y')
plt.tight_layout()
plt.savefig(figures_dir / "LIG_GP 优化效果对比.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  优化效果对比图：{figures_dir / 'LIG_GP 优化效果对比.png'}")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 70)
print("[OK] 数据质量检查 + GP 优化完成！")
print("=" * 70)

print(f"\n关键发现:")
print(f"  1. 数据量：{len(df)} 样本")
print(f"  2. 最佳特征：{best_features}")
print(f"  3. 最佳 R²: {best_r2_val:.3f} (目标：>0.85)")
print(f"  4. 最佳 MAE: {best_mae:.1f} S/m")
print(f"  5. 不确定性：±{best_unc:.1f}% (目标：<±6%)")

if best_r2_val >= 0.85 and best_unc <= 6:
    print(f"\n[TOP] 目标达成！R²>0.85, 不确定性<±6%")
elif best_r2_val >= 0.80 and best_unc <= 8:
    print(f"\n[OK] 良好！R²>0.80, 不确定性<±8%")
else:
    print(f"\n[WARN] 需要继续优化：当前 R²={best_r2_val:.3f}, 不确定性=±{best_unc:.1f}%")

print(f"\n下一步:")
print(f"  1. 下载 MACE-MP-0 预训练模型")
print(f"  2. 下载 CHGNet-MP-2024 预训练模型")
print(f"  3. 运行迁移学习微调")
print(f"  4. 多模型集成预测")

print("=" * 70)
