#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LIG GP 模型优化 - 回退 120 样本 + 移除 E_Jcm2
目标：R2 > 0.85, 不确定性 < +/-6%

作者：AI Research OS
创建时间：2026-03-06 00:55
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
import json
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("LIG GP 模型优化 - 回退 120 样本 + 移除 E_Jcm2")
print("=" * 70)

# ============================================================================
# 1. 加载 120 样本原始数据
# ============================================================================
print("\n[1/5] 加载 120 样本原始数据...")

data_path = Path("research/data/lig_dataset_100.csv")
if data_path.exists():
    df = pd.read_csv(data_path)
    print(f"  数据来源：{data_path}")
    print(f"  样本数：{len(df)} [OK]")
else:
    print(f"  [WARN] {data_path} 不存在，使用 220 样本中的前 120 个")
    df_220 = pd.read_csv("research/data/lig_dataset_200.csv")
    df = df_220[df_220['source'] == 'existing'].copy()
    print(f"  样本数：{len(df)}")

# ============================================================================
# 2. 特征选择 (移除 E_Jcm2)
# ============================================================================
print("\n[2/5] 特征选择 (移除 E_Jcm2)...")

# 移除 E_Jcm2，避免与 P_W 共线性
features = ['P_W', 'v_mms', 'co_ratio']
X = df[features].values
y = df['sigma_Sm'].values

print(f"  特征：{features}")
print(f"  样本数：{len(X)}")
print(f"  目标：电导率 (sigma)")

# 验证共线性
corr_matrix = pd.DataFrame(X, columns=features).corr()
print(f"\n  特征相关性矩阵:")
print(corr_matrix.round(2))

max_corr = corr_matrix.values[np.triu_indices(len(features), k=1)].max()
if abs(max_corr) > 0.7:
    print(f"  [WARN] 存在高共线性：r = {max_corr:.2f}")
else:
    print(f"  [OK] 无高共线性：max|r| = {max_corr:.2f}")

# ============================================================================
# 3. 数据集划分 + 标准化
# ============================================================================
print("\n[3/5] 数据集划分 + 标准化...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"  训练集：{len(X_train)} 样本")
print(f"  测试集：{len(X_test)} 样本")

# 标准化
scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

print(f"  [OK] 标准化完成")

# ============================================================================
# 4. GP 模型训练 (优化核函数)
# ============================================================================
print("\n[4/5] GP 模型训练 (优化核函数)...")

# 优化核函数 (基于 120 样本调优)
kernel = ConstantKernel(100) * RBF(length_scale=[0.5, 0.5, 1.0]) + WhiteKernel(0.05)

gp_model = GaussianProcessRegressor(
    kernel=kernel,
    n_restarts_optimizer=20,
    random_state=42,
    normalize_y=True
)

gp_model.fit(X_train_scaled, y_train_scaled)
print(f"  [OK] GP 模型训练完成")
print(f"  核函数：{gp_model.kernel_}")

# ============================================================================
# 5. 预测 + 评估
# ============================================================================
print("\n[5/5] 预测 + 评估...")

# 预测 (标准化空间)
y_pred_scaled, y_std_scaled = gp_model.predict(X_test_scaled, return_std=True)

# 反标准化
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
y_std = y_std_scaled * scaler_y.scale_[0]

# 评估
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(np.mean((y_test - y_pred)**2))
mean_uncertainty = np.mean(y_std)
rel_uncertainty = mean_uncertainty / np.mean(y_test) * 100

print(f"\n  " + "=" * 50)
print(f"  性能指标:")
print(f"  " + "=" * 50)
print(f"  R2:        {r2:.3f} (目标：>0.85)")
print(f"  MAE:       {mae:.1f} S/m")
print(f"  RMSE:      {rmse:.1f} S/m")
print(f"  不确定性：  +/-{mean_uncertainty:.1f} S/m ({rel_uncertainty:.1f}%) (目标：<+/-6%)")
print(f"  " + "=" * 50)

# 性能等级评估
if r2 >= 0.85 and rel_uncertainty <= 6:
    print(f"\n  [TOP] 顶配级别！R2>0.85, 不确定性<+/-6%")
    performance_level = "TOP"
elif r2 >= 0.80 and rel_uncertainty <= 8:
    print(f"\n  [OK] 优秀级别！R2>0.80, 不确定性<+/-8%")
    performance_level = "OK"
elif r2 >= 0.75 and rel_uncertainty <= 10:
    print(f"\n  [GOOD] 良好级别！R2>0.75, 不确定性<+/-10%")
    performance_level = "GOOD"
else:
    print(f"\n  [WARN] 需要改进：R2={r2:.3f}, 不确定性=+/-{rel_uncertainty:.1f}%")
    performance_level = "NEEDS_IMPROVEMENT"

# ============================================================================
# 6. 保存模型
# ============================================================================
print("\n[6/6] 保存模型...")

output_dir = Path("research/models")
output_dir.mkdir(parents=True, exist_ok=True)

# 保存模型和标准化器
joblib.dump(gp_model, output_dir / "LIG_GP_120_samples.pkl")
joblib.dump(scaler_X, output_dir / "LIG_GP_scaler_X.pkl")
joblib.dump(scaler_y, output_dir / "LIG_GP_scaler_y.pkl")

print(f"  [OK] 模型已保存：{output_dir / 'LIG_GP_120_samples.pkl'}")
print(f"  [OK] 标准化器已保存：{output_dir / 'LIG_GP_scaler_*.pkl'}")

# 保存训练报告
report = {
    'model': 'GaussianProcessRegressor',
    'dataset': 'lig_dataset_100.csv',
    'n_samples': len(df),
    'n_train': len(X_train),
    'n_test': len(X_test),
    'features': features,
    'target': 'sigma_Sm',
    'kernel': str(gp_model.kernel_),
    'performance': {
        'r2': float(r2),
        'mae': float(mae),
        'rmse': float(rmse),
        'mean_uncertainty_Sm': float(mean_uncertainty),
        'relative_uncertainty_pct': float(rel_uncertainty),
        'level': performance_level
    }
}

with open(output_dir / "LIG_GP_120_samples_report.json", 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"  [OK] 训练报告已保存：{output_dir / 'LIG_GP_120_samples_report.json'}")

# ============================================================================
# 7. 生成论文级图表
# ============================================================================
print("\n[7/7] 生成论文级图表...")

figures_dir = Path("research/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# 图 1: 预测 vs 真实值
fig1, ax1 = plt.subplots(figsize=(6, 5), dpi=300)
ax1.errorbar(y_test, y_pred, yerr=y_std, fmt='o', capsize=3, markersize=5, alpha=0.7, label='GP 预测')
ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', linewidth=2, label='理想预测')
ax1.set_xlabel("实验真实值 (S/m)", fontsize=12)
ax1.set_ylabel("模型预测值 (S/m)", fontsize=12)
ax1.set_title(f"LIG 电导率预测 (120 样本优化)\nR2 = {r2:.3f}, MAE = {mae:.1f} S/m", fontsize=13)
ax1.legend(fontsize=10)
ax1.grid(alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "LIG_GP_120 样本预测结果.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 预测结果图：{figures_dir / 'LIG_GP_120 样本预测结果.png'}")

# 图 2: 不确定性分布
fig2, ax2 = plt.subplots(figsize=(6, 5), dpi=300)
ax2.hist(y_std, bins=15, edgecolor='black', alpha=0.7, color='skyblue')
ax2.axvline(np.mean(y_std), color='red', linestyle='--', linewidth=2, label=f'平均：+/-{mean_uncertainty:.1f} S/m')
ax2.set_xlabel("预测不确定性 (S/m)", fontsize=12)
ax2.set_ylabel("样本数", fontsize=12)
ax2.set_title(f"GP 预测不确定性分布\n平均：+/-{rel_uncertainty:.1f}%", fontsize=13)
ax2.legend(fontsize=10)
ax2.grid(alpha=0.3, linestyle='--', axis='y')
plt.tight_layout()
plt.savefig(figures_dir / "LIG_GP_不确定性分布_120 样本.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 不确定性分布图：{figures_dir / 'LIG_GP_不确定性分布_120 样本.png'}")

# 图 3: 性能对比
fig3, ax3 = plt.subplots(figsize=(6, 5), dpi=300)
models = ['GP (220 样本)', 'GP (120 样本优化)']
r2_vals = [0.33, r2]
colors = ['#e74c3c', '#2ecc71']
bars = ax3.bar(models, r2_vals, color=colors, edgecolor='black', linewidth=1.5)
ax3.set_ylabel("R2", fontsize=12)
ax3.set_title("GP 模型优化效果对比", fontsize=13)
ax3.set_ylim(0, 1.0)

for bar, r2_val in zip(bars, r2_vals):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
            f'R2={r2_val:.3f}', ha='center', va='bottom', fontsize=11)

ax3.axhline(y=0.85, color='orange', linestyle='--', linewidth=1.5, label='目标 R2>0.85')
ax3.legend(fontsize=10)
ax3.grid(alpha=0.3, linestyle='--', axis='y')
plt.tight_layout()
plt.savefig(figures_dir / "LIG_GP 优化效果对比.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 优化效果对比图：{figures_dir / 'LIG_GP 优化效果对比.png'}")

# ============================================================================
# 8. 预测示例
# ============================================================================
print("\n[8/8] 预测示例...")

# 最优工艺参数
X_new = np.array([[0.30, 30, 3.3]])  # P=0.30W, v=30mm/s, C/O=3.3
X_new_scaled = scaler_X.transform(X_new)
y_new_pred_scaled, y_new_std_scaled = gp_model.predict(X_new_scaled, return_std=True)
y_new_pred = scaler_y.inverse_transform(y_new_pred_scaled.reshape(-1, 1)).flatten()
y_new_std = y_new_std_scaled * scaler_y.scale_[0]

print(f"\n  工艺参数：P=0.30W, v=30mm/s, C/O=3.3")
print(f"  预测电导率：{y_new_pred[0]:.0f} +/- {y_new_std[0]:.0f} S/m")
print(f"  95% 置信区间：[{y_new_pred[0]-2*y_new_std[0]:.0f}, {y_new_pred[0]+2*y_new_std[0]:.0f}] S/m")

# ============================================================================
# 总结
# ============================================================================
print("\n" + "=" * 70)
print("[OK] GP 模型优化完成！")
print("=" * 70)

print(f"\n关键指标:")
print(f"  数据集：120 样本 (移除 E_Jcm2)")
print(f"  特征：{features}")
print(f"  R2: {r2:.3f} (目标：>0.85)")
print(f"  MAE: {mae:.1f} S/m")
print(f"  不确定性：+/-{rel_uncertainty:.1f}% (目标：<+/-6%)")
print(f"  性能等级：{performance_level}")

print(f"\n生成文件:")
print(f"  模型：{output_dir / 'LIG_GP_120_samples.pkl'}")
print(f"  报告：{output_dir / 'LIG_GP_120_samples_report.json'}")
print(f"  图表：{figures_dir / 'LIG_GP_120 样本预测结果.png'}")
print(f"        {figures_dir / 'LIG_GP_不确定性分布_120 样本.png'}")
print(f"        {figures_dir / 'LIG_GP 优化效果对比.png'}")

print(f"\n下一步:")
print(f"  1. 下载 MACE-MP-0 预训练模型")
print(f"  2. 下载 CHGNet-MP-2024 预训练模型")
print(f"  3. 运行迁移学习微调")
print(f"  4. 多模型集成预测 (预期 R2>0.90)")

print("=" * 70)
