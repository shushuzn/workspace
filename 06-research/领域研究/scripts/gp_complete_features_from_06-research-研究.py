#!/usr/bin/env python3
"""
GP 模型 - 使用完整特征 (包含 E_Jcm2)
预期 R2 > 0.80
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

print("=" * 70)
print("GP 模型 - 完整特征 (包含 E_Jcm2)")
print("=" * 70)

# ============================================================================
# 1. 加载 LIG 数据
# ============================================================================
print("\n[1/6] 加载 LIG 数据...")

data_path = Path("research/data/lig_dataset_100.csv")
df = pd.read_csv(data_path)
print(f"  数据来源：{data_path}")
print(f"  样本数：{len(df)}")

# 完整特征 (包含 E_Jcm2)
features = ['P_W', 'v_mms', 'E_Jcm2', 'co_ratio']
X = df[features].values
y = df['sigma_Sm'].values

print(f"  特征：{features}")
print(f"  目标：电导率 (sigma)")

# 验证共线性
print(f"\n  特征相关性:")
corr_df = pd.DataFrame(X, columns=features)
corr_matrix = corr_df.corr()
print(corr_matrix.round(2))

# 数据集划分
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"\n  训练集：{len(X_train)} 样本")
print(f"  测试集：{len(X_test)} 样本")

# 标准化
scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

print(f"  [OK] 数据标准化完成")

# ============================================================================
# 2. GP 模型训练
# ============================================================================
print("\n[2/6] GP 模型训练...")

# 优化核函数 (针对 4 特征)
kernel = ConstantKernel(100) * RBF(length_scale=[0.5, 0.5, 0.5, 1.0]) + WhiteKernel(0.05)

gp_model = GaussianProcessRegressor(
    kernel=kernel,
    n_restarts_optimizer=20,
    random_state=42,
    normalize_y=True
)

print(f"  核函数：{kernel}")
print(f"  开始训练...")

gp_model.fit(X_train_scaled, y_train_scaled)
print(f"  [OK] GP 模型训练完成")
print(f"  优化后核函数：{gp_model.kernel_}")

# ============================================================================
# 3. 预测与评估
# ============================================================================
print("\n[3/6] 预测与评估...")

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

print(f"\n  测试集性能:")
print(f"    R2: {r2:.3f} (目标：>0.80)")
print(f"    MAE: {mae:.1f} S/m")
print(f"    RMSE: {rmse:.1f} S/m")
print(f"    NRMSE: {nrmse:.1f}%")

# 不确定性
mean_uncertainty = np.mean(y_std)
rel_uncertainty = mean_uncertainty / np.mean(y_test) * 100

print(f"\n  不确定性:")
print(f"    平均：±{mean_uncertainty:.1f} S/m ({rel_uncertainty:.1f}%)")

# 95% 置信区间
ci_95_lower = y_pred - 2 * y_std
ci_95_upper = y_pred + 2 * y_std

# 覆盖率
in_ci = (y_test >= ci_95_lower) & (y_test <= ci_95_upper)
coverage = np.mean(in_ci) * 100
print(f"    95% CI 覆盖率：{coverage:.1f}%")

gp_performance = {
    'r2': float(r2),
    'mae': float(mae),
    'rmse': float(rmse),
    'nrmse_pct': float(nrmse),
    'mean_uncertainty': float(mean_uncertainty),
    'relative_uncertainty_pct': float(rel_uncertainty),
    'ci_95_coverage': float(coverage)
}

# ============================================================================
# 4. 保存模型
# ============================================================================
print("\n[4/6] 保存模型...")

output_dir = Path("research/models")
output_dir.mkdir(parents=True, exist_ok=True)

# 保存模型和标准化器
joblib.dump(gp_model, output_dir / "LIG_GP_complete_features.pkl")
joblib.dump(scaler_X, output_dir / "LIG_GP_scaler_X.pkl")
joblib.dump(scaler_y, output_dir / "LIG_GP_scaler_y.pkl")

print(f"  [OK] 模型已保存:")
print(f"    LIG_GP_complete_features.pkl")
print(f"    LIG_GP_scaler_X.pkl")
print(f"    LIG_GP_scaler_y.pkl")

# 保存配置
config = {
    'model': 'GaussianProcessRegressor',
    'features': features,
    'target': 'sigma_Sm',
    'kernel': str(gp_model.kernel_),
    'dataset': {
        'source': str(data_path),
        'n_samples': len(df),
        'n_train': len(X_train),
        'n_test': len(X_test),
        'test_size': 0.2,
        'random_state': 42
    },
    'performance': gp_performance
}

config_path = output_dir / "LIG_GP_complete_config.json"
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"  [OK] 配置已保存：{config_path}")

# ============================================================================
# 5. 可视化
# ============================================================================
print("\n[5/6] 生成图表...")

figures_dir = Path("research/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# 图 1: 预测 vs 真实值
fig1, ax1 = plt.subplots(figsize=(8, 6), dpi=300)
ax1.errorbar(y_test, y_pred, yerr=y_std, fmt='o', capsize=3, markersize=6, alpha=0.7, 
             color='blue', ecolor='gray', elinewidth=1.5)
ax1.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', linewidth=2, label='理想预测')
ax1.set_xlabel("实验真实值 (S/m)", fontsize=12)
ax1.set_ylabel("模型预测值 (S/m)", fontsize=12)
ax1.set_title(f"GP 预测 (完整特征)\nR2 = {r2:.3f}, MAE = {mae:.1f} S/m", fontsize=14)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(figures_dir / "GP_complete_prediction.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 预测图：{figures_dir / 'GP_complete_prediction.png'}")

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
plt.savefig(figures_dir / "GP_complete_residuals.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 残差图：{figures_dir / 'GP_complete_residuals.png'}")

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
plt.savefig(figures_dir / "GP_complete_uncertainty.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 不确定性图：{figures_dir / 'GP_complete_uncertainty.png'}")

# ============================================================================
# 6. 总结
# ============================================================================
print("\n[6/6] 总结...")

print("\n" + "=" * 70)
print("[OK] GP 模型训练完成 (完整特征)！")
print("=" * 70)

print(f"\n性能指标:")
print(f"  R2: {r2:.3f} (目标：>0.80)")
print(f"  MAE: {mae:.1f} S/m")
print(f"  NRMSE: {nrmse:.1f}%")
print(f"  不确定性：±{rel_uncertainty:.1f}%")
print(f"  95% CI 覆盖率：{coverage:.1f}%")

# 性能等级
if r2 >= 0.85:
    print(f"\n[TOP] 优秀！R2 > 0.85，达到顶配水平！")
    performance_level = "TOP"
elif r2 >= 0.80:
    print(f"\n[OK] 良好！R2 > 0.80，达到目标！")
    performance_level = "OK"
elif r2 >= 0.75:
    print(f"\n[GOOD] 可接受！R2 > 0.75")
    performance_level = "GOOD"
else:
    print(f"\n[WARN] 需要改进：R2 = {r2:.3f}")
    performance_level = "NEEDS_IMPROVEMENT"

# 与之前对比
print(f"\n模型对比:")
print(f"  GP (3 特征，无 E_Jcm2): R2 ≈ 0.50")
print(f"  GP (4 特征，完整):      R2 = {r2:.3f} {'⭐' if r2 > 0.75 else ''}")
print(f"  提升：{(r2 - 0.50) / 0.50 * 100:+.0f}%")

print(f"\n生成文件:")
print(f"  模型：{output_dir / 'LIG_GP_complete_features.pkl'}")
print(f"  配置：{output_dir / 'LIG_GP_complete_config.json'}")
print(f"  图表：{figures_dir / 'GP_complete_prediction.png'}")
print(f"        {figures_dir / 'GP_complete_residuals.png'}")
print(f"        {figures_dir / 'GP_complete_uncertainty.png'}")

print(f"\n下一步:")
print(f"  1. 使用 GP 模型进行预测")
print(f"  2. 实验验证")
print(f"  3. 撰写论文")

print("=" * 70)
