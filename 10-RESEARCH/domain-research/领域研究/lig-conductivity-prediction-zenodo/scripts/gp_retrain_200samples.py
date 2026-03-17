#!/usr/bin/env python3
"""
GP 模型重新训练 - 使用 200 样本
预期 R² > 0.80, 不确定性 < ±6%
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import json
import matplotlib.pyplot as plt
from datetime import datetime

print("=" * 70)
print("GP 模型重新训练 - 200 样本")
print("=" * 70)

# ============================================================================
# 1. 加载 200 样本数据
# ============================================================================
print("\n[1/6] 加载 200 样本数据...")

data_path = Path("research/data/lig_dataset_200.csv")
if data_path.exists():
    df = pd.read_csv(data_path)
    print(f"  数据来源：{data_path}")
    print(f"  样本数：{len(df)} [OK]")
else:
    print(f"  [ERROR] 数据文件不存在：{data_path}")
    exit(1)

# 特征选择 (避免共线性：使用 E_Jcm2，不使用 P_W)
features = ['E_Jcm2', 'v_mms', 'co_ratio']
X = df[features].values
y = df['sigma_Sm'].values

print(f"  特征：{features}")
print(f"  目标：电导率 (sigma)")

# 验证共线性
print(f"\n  特征相关性:")
corr_df = pd.DataFrame(X, columns=features)
corr_matrix = corr_df.corr()
print(corr_matrix.round(2))

max_corr = corr_matrix.values[np.triu_indices(len(features), k=1)].max()
if abs(max_corr) > 0.7:
    print(f"  [WARN] 存在高共线性：r = {max_corr:.2f}")
else:
    print(f"  [OK] 无高共线性：max|r| = {max_corr:.2f}")

# ============================================================================
# 2. 数据集划分
# ============================================================================
print("\n[2/6] 数据集划分...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"  训练集：{len(X_train)} 样本 (80%)")
print(f"  测试集：{len(X_test)} 样本 (20%)")

# 标准化
scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

print(f"  [OK] 标准化完成")

# ============================================================================
# 3. GP 模型训练
# ============================================================================
print("\n[3/6] GP 模型训练...")

# 针对 200 样本优化核函数
kernel = ConstantKernel(100) * RBF(length_scale=[1.0, 1.0, 1.0]) + WhiteKernel(0.05)

gp_model = GaussianProcessRegressor(
    kernel=kernel,
    n_restarts_optimizer=30,  # 增加优化次数
    random_state=42,
    normalize_y=True
)

print(f"  核函数：{kernel}")
print(f"  开始训练...")

gp_model.fit(X_train_scaled, y_train_scaled)
print(f"  [OK] GP 模型训练完成")
print(f"  优化后核函数：{gp_model.kernel_}")

# ============================================================================
# 4. 预测与评估
# ============================================================================
print("\n[4/6] 预测与评估...")

# 预测 (带不确定性)
y_pred_scaled, y_std_scaled = gp_model.predict(X_test_scaled, return_std=True)

# 反标准化
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
y_std = y_std_scaled * scaler_y.scale_[0]

# 评估
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(np.mean((y_test - y_pred)**2))
nrmse = rmse / np.mean(y_test) * 100

print(f"\n  [STAT] 测试集性能:")
print(f"    R2: {r2:.3f} (目标：>0.80)")
print(f"    MAE: {mae:.1f} S/m")
print(f"    RMSE: {rmse:.1f} S/m")
print(f"    NRMSE: {nrmse:.1f}%")

# 不确定性
mean_uncertainty = np.mean(y_std)
rel_uncertainty = mean_uncertainty / np.mean(y_test) * 100

print(f"\n  [STAT] 不确定性:")
print(f"    平均：±{mean_uncertainty:.1f} S/m ({rel_uncertainty:.1f}%)")

# 95% 置信区间
ci_95_lower = y_pred - 2 * y_std
ci_95_upper = y_pred + 2 * y_std

# 覆盖率
in_ci = (y_test >= ci_95_lower) & (y_test <= ci_95_upper)
coverage = np.mean(in_ci) * 100
print(f"    95% CI 覆盖率：{coverage:.1f}%")

# 性能等级
if r2 >= 0.85:
    performance_level = "TOP"
    emoji = "[OK][OK][OK]"
elif r2 >= 0.80:
    performance_level = "EXCELLENT"
    emoji = "[OK][OK]"
elif r2 >= 0.75:
    performance_level = "GOOD"
    emoji = "[OK]"
else:
    performance_level = "NEEDS_IMPROVEMENT"
    emoji = "[LOOP]"

print(f"\n  {emoji} 性能等级：{performance_level}")

gp_performance = {
    'r2': float(r2),
    'mae': float(mae),
    'rmse': float(rmse),
    'nrmse_pct': float(nrmse),
    'mean_uncertainty': float(mean_uncertainty),
    'relative_uncertainty_pct': float(rel_uncertainty),
    'ci_95_coverage': float(coverage),
    'performance_level': performance_level
}

# ============================================================================
# 5. 保存模型
# ============================================================================
print("\n[5/6] 保存模型...")

output_dir = Path("research/models")
output_dir.mkdir(parents=True, exist_ok=True)

# 保存模型和标准化器
joblib.dump(gp_model, output_dir / "LIG_GP_200samples.pkl")
joblib.dump(scaler_X, output_dir / "LIG_GP_scaler_X.pkl")
joblib.dump(scaler_y, output_dir / "LIG_GP_scaler_y.pkl")

print(f"  [OK] 模型已保存:")
print(f"    LIG_GP_200samples.pkl")
print(f"    LIG_GP_scaler_X.pkl")
print(f"    LIG_GP_scaler_y.pkl")

# 保存配置
config = {
    'model': 'GaussianProcessRegressor',
    'features': features,
    'target': 'sigma_Sm',
    'dataset': {
        'source': str(data_path),
        'n_samples': len(df),
        'n_train': len(X_train),
        'n_test': len(X_test),
        'test_size': 0.2,
        'random_state': 42
    },
    'kernel': str(gp_model.kernel_),
    'performance': gp_performance,
    'training_date': datetime.now().isoformat()
}

config_path = output_dir / "LIG_GP_200samples_config.json"
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"  [OK] 配置已保存：{config_path}")

# ============================================================================
# 6. 可视化
# ============================================================================
print("\n[6/6] 生成可视化图表...")

figures_dir = Path("research/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# 图 1: 预测 vs 真实值
fig1, ax1 = plt.subplots(figsize=(8, 6), dpi=300)
ax1.errorbar(y_test, y_pred, yerr=y_std, fmt='o', capsize=3, markersize=6, alpha=0.7, 
             color='blue', ecolor='gray', elinewidth=1.5)
ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', linewidth=2, label='理想预测')
ax1.set_xlabel("实验真实值 (S/m)", fontsize=12)
ax1.set_ylabel("模型预测值 (S/m)", fontsize=12)
ax1.set_title(f"GP 预测 (200 样本)\nR² = {r2:.3f}, MAE = {mae:.1f} S/m", fontsize=14)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "GP_200samples_prediction.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 预测图：{figures_dir / 'GP_200samples_prediction.png'}")

# 图 2: 残差分析
fig2, (ax2a, ax2b) = plt.subplots(1, 2, figsize=(14, 5), dpi=300)

# 残差 vs 预测值
residuals = y_test - y_pred
ax2a.scatter(y_pred, residuals, alpha=0.7, s=60, color='blue')
ax2a.axhline(y=0, color='red', linestyle='--', linewidth=2)
ax2a.set_xlabel("预测值 (S/m)", fontsize=12)
ax2a.set_ylabel("残差 (S/m)", fontsize=12)
ax2a.set_title("残差分析", fontsize=13)
ax2a.grid(True, alpha=0.3, linestyle='--')

# 残差分布
ax2b.hist(residuals, bins=15, edgecolor='black', alpha=0.7, color='skyblue')
ax2b.axvline(x=0, color='red', linestyle='--', linewidth=2, label='零残差')
ax2b.set_xlabel("残差 (S/m)", fontsize=12)
ax2b.set_ylabel("样本数", fontsize=12)
ax2b.set_title(f"残差分布\n均值={np.mean(residuals):.1f}, 标准差={np.std(residuals):.1f}", fontsize=13)
ax2b.legend(fontsize=10)
ax2b.grid(True, alpha=0.3, linestyle='--', axis='y')
plt.tight_layout()
plt.savefig(figures_dir / "GP_200samples_residuals.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 残差图：{figures_dir / 'GP_200samples_residuals.png'}")

# 图 3: 不确定性分布
fig3, ax3 = plt.subplots(figsize=(8, 6), dpi=300)
ax3.hist(y_std, bins=15, edgecolor='black', alpha=0.7, color='lightgreen')
ax3.axvline(mean_uncertainty, color='red', linestyle='--', linewidth=2, 
            label=f'平均：±{mean_uncertainty:.1f} S/m')
ax3.set_xlabel("预测不确定性 (S/m)", fontsize=12)
ax3.set_ylabel("样本数", fontsize=12)
ax3.set_title(f"GP 预测不确定性分布\n平均：±{rel_uncertainty:.1f}%, 95% CI 覆盖率：{coverage:.1f}%", 
              fontsize=13)
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3, linestyle='--', axis='y')
plt.tight_layout()
plt.savefig(figures_dir / "GP_200samples_uncertainty.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 不确定性图：{figures_dir / 'GP_200samples_uncertainty.png'}")

# 图 4: 性能对比
fig4, ax4 = plt.subplots(figsize=(8, 6), dpi=300)
models = ['120 样本', '160 样本', '200 样本']
r2_vals = [0.50, 0.75, r2]  # 近似值
colors = ['#e74c3c', '#f39c12', '#2ecc71']
bars = ax4.bar(models, r2_vals, color=colors, edgecolor='black', linewidth=1.5)
ax4.set_ylabel("R²", fontsize=12)
ax4.set_title("GP 模型性能提升", fontsize=14)
ax4.set_ylim(0, 1.0)

for bar, r2_val in zip(bars, r2_vals):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
            f'R²={r2_val:.2f}', ha='center', va='bottom', fontsize=11)

ax4.axhline(y=0.80, color='red', linestyle='--', linewidth=1.5, label='目标 R²>0.80')
ax4.legend()
ax4.grid(True, alpha=0.3, linestyle='--', axis='y')
plt.tight_layout()
plt.savefig(figures_dir / "GP_performance_comparison.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 性能对比图：{figures_dir / 'GP_performance_comparison.png'}")

# ============================================================================
# 7. 总结
# ============================================================================
print("\n" + "=" * 70)
print(f"{emoji} GP 模型重新训练完成！")
print("=" * 70)

print(f"\n最终性能:")
print(f"  R² = {r2:.3f} {emoji} {performance_level}")
print(f"  MAE = {mae:.1f} S/m")
print(f"  不确定性 = ±{rel_uncertainty:.1f}%")
print(f"  95% CI 覆盖率 = {coverage:.1f}%")

print(f"\n文件:")
print(f"  模型：{output_dir / 'LIG_GP_200samples.pkl'}")
print(f"  配置：{output_dir / 'LIG_GP_200samples_config.json'}")
print(f"  图表：{figures_dir / 'GP_200samples_prediction.png'}")
print(f"        {figures_dir / 'GP_200samples_residuals.png'}")
print(f"        {figures_dir / 'GP_200samples_uncertainty.png'}")
print(f"        {figures_dir / 'GP_performance_comparison.png'}")

print(f"\n下一步:")
print(f"  1. 准备论文初稿")
print(f"  2. 实验验证预测")
print(f"  3. 投稿准备")

print("=" * 70)
