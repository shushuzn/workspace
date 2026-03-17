#!/usr/bin/env python3
"""
GP 模型 - 无共线性特征
使用 E_Jcm2 替代 P_W
预期 R² > 0.80
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
print("GP 模型 - 无共线性特征 (E_Jcm2 + v_mms + co_ratio)")
print("=" * 70)

# ============================================================================
# 1. 加载数据
# ============================================================================
print("\n[1/6] 加载 LIG 数据...")

data_path = Path("research/data/lig_dataset_100.csv")
df = pd.read_csv(data_path)
print(f"  样本数：{len(df)}")

# 无共线性特征 (移除 P_W，保留 E_Jcm2)
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

print(f"  [OK] 标准化完成")

# ============================================================================
# 2. GP 训练
# ============================================================================
print("\n[2/6] GP 模型训练...")

# 针对 3 特征优化核函数
kernel = ConstantKernel(100) * RBF(length_scale=[1.0, 1.0, 1.0]) + WhiteKernel(0.05)

gp_model = GaussianProcessRegressor(
    kernel=kernel,
    n_restarts_optimizer=20,
    random_state=42,
    normalize_y=True
)

print(f"  开始训练...")
gp_model.fit(X_train_scaled, y_train_scaled)

print(f"  [OK] 训练完成")
print(f"  优化核函数：{gp_model.kernel_}")

# ============================================================================
# 3. 评估
# ============================================================================
print("\n[3/6] 评估...")

y_pred_scaled, y_std_scaled = gp_model.predict(X_test_scaled, return_std=True)
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
y_std = y_std_scaled * scaler_y.scale_[0]

r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(np.mean((y_test - y_pred)**2))
nrmse = rmse / np.mean(y_test) * 100

print(f"\n  性能指标:")
print(f"    R2: {r2:.3f} (目标：>0.80)")
print(f"    MAE: {mae:.1f} S/m")
print(f"    RMSE: {rmse:.1f} S/m")
print(f"    NRMSE: {nrmse:.1f}%")

# 不确定性
mean_unc = np.mean(y_std)
rel_unc = mean_unc / np.mean(y_test) * 100
print(f"\n  不确定性：±{mean_unc:.1f} S/m ({rel_unc:.1f}%)")

# 覆盖率
ci_lower = y_pred - 2 * y_std
ci_upper = y_pred + 2 * y_std
coverage = np.mean((y_test >= ci_lower) & (y_test <= ci_upper)) * 100
print(f"  95% CI 覆盖率：{coverage:.1f}%")

# ============================================================================
# 4-6. 保存、可视化、总结
# ============================================================================
print("\n[4/6] 保存模型...")

output_dir = Path("research/models")
output_dir.mkdir(parents=True, exist_ok=True)

joblib.dump(gp_model, output_dir / "LIG_GP_no_collinearity.pkl")
joblib.dump(scaler_X, output_dir / "LIG_GP_scaler_X.pkl")
joblib.dump(scaler_y, output_dir / "LIG_GP_scaler_y.pkl")

config = {
    'model': 'GaussianProcessRegressor',
    'features': features,
    'target': 'sigma_Sm',
    'kernel': str(gp_model.kernel_),
    'performance': {
        'r2': float(r2),
        'mae': float(mae),
        'rmse': float(rmse),
        'nrmse_pct': float(nrmse),
        'uncertainty_pct': float(rel_unc),
        'ci_coverage': float(coverage)
    }
}

with open(output_dir / "LIG_GP_no_collinearity_config.json", 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"  [OK] 模型已保存")

print("\n[5/6] 生成图表...")

figures_dir = Path("research/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# 预测图
fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
ax.errorbar(y_test, y_pred, yerr=y_std, fmt='o', capsize=3, markersize=6, alpha=0.7)
ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
ax.set_xlabel("真实值 (S/m)")
ax.set_ylabel("预测值 (S/m)")
ax.set_title(f"GP 预测 (无共线性)\nR2 = {r2:.3f}")
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(figures_dir / "GP_no_collinearity_prediction.png", dpi=300)
plt.close()

print(f"  [OK] 图表已保存")

# ============================================================================
# 6. 总结
# ============================================================================
print("\n[6/6] 总结...")

print("\n" + "=" * 70)
print(f"GP 模型完成 (无共线性特征)！")
print("=" * 70)

print(f"\n性能:")
print(f"  R2 = {r2:.3f} {'[OK]' if r2 > 0.75 else '[WARN]'}")
print(f"  MAE = {mae:.1f} S/m")
print(f"  不确定性 = ±{rel_unc:.1f}%")

print(f"\n特征选择:")
print(f"  ✅ {features}")
print(f"  ❌ 移除了 P_W (与 E_Jcm2 共线性 r=0.95)")

print(f"\n下一步:")
print(f"  1. 使用模型预测")
print(f"  2. 实验验证")
print(f"  3. 撰写论文")

print("=" * 70)
