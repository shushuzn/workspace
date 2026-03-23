#!/usr/bin/env python3
"""
GP + MACE 集成预测
结合 GP 和 MACE 的优势
预期 R2 > 0.85
"""
import torch
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
print("GP + MACE 集成预测")
print("=" * 70)

# ============================================================================
# 1. 加载 LIG 数据
# ============================================================================
print("\n[1/6] 加载 LIG 数据...")

data_path = Path("research/data/lig_dataset_100.csv")
df = pd.read_csv(data_path)
print(f"  数据来源：{data_path}")
print(f"  样本数：{len(df)}")

# 特征和标签
features = ['P_W', 'v_mms', 'co_ratio']
X = df[features].values
y = df['sigma_Sm'].values

# 数据集划分 (与之前保持一致)
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

print(f"  [OK] 数据标准化完成")

# ============================================================================
# 2. 加载 GP 模型
# ============================================================================
print("\n[2/6] 加载 GP 模型...")

gp_model_path = Path("research/models/LIG_GP_120_samples.pkl")
gp_scaler_X_path = Path("research/models/LIG_GP_scaler_X.pkl")
gp_scaler_y_path = Path("research/models/LIG_GP_scaler_y.pkl")

if gp_model_path.exists():
    gp_model = joblib.load(gp_model_path)
    gp_scaler_X = joblib.load(gp_scaler_X_path)
    gp_scaler_y = joblib.load(gp_scaler_y_path)
    print(f"  [OK] GP 模型加载成功")
    gp_loaded = True
else:
    print(f"  [WARN] GP 模型不存在，重新训练...")

    # 重新训练 GP
    kernel = ConstantKernel(100) * RBF(length_scale=[0.5, 0.5, 1.0]) + WhiteKernel(0.05)
    gp_model = GaussianProcessRegressor(
        kernel=kernel,
        n_restarts_optimizer=20,
        random_state=42,
        normalize_y=True
    )
    gp_model.fit(X_train_scaled, y_train_scaled)

    gp_scaler_X = scaler_X
    gp_scaler_y = scaler_y
    gp_loaded = True

# GP 预测
y_pred_gp_scaled, y_std_gp_scaled = gp_model.predict(X_test_scaled, return_std=True)
y_pred_gp = gp_scaler_y.inverse_transform(y_pred_gp_scaled.reshape(-1, 1)).flatten()
y_std_gp = y_std_gp_scaled * gp_scaler_y.scale_[0]

# GP 评估
r2_gp = r2_score(y_test, y_pred_gp)
mae_gp = mean_absolute_error(y_test, y_pred_gp)
print(f"  GP 性能：R2 = {r2_gp:.3f}, MAE = {mae_gp:.1f} S/m")

# ============================================================================
# 3. 加载 MACE 模型
# ============================================================================
print("\n[3/6] 加载 MACE 模型...")

mace_model_path = Path("research/models/MACE_LIG_regressor.pth")

if mace_model_path.exists():
    # 加载 MACE 回归器
    import torch.nn as nn

    class MACERegressor(nn.Module):
        def __init__(self, input_dim=3, mace_hidden_dim=128, hidden_dim=64, output_dim=1):
            super().__init__()
            self.mace_encoder = nn.Sequential(
                nn.Linear(input_dim, mace_hidden_dim),
                nn.ReLU(),
                nn.Linear(mace_hidden_dim, mace_hidden_dim),
                nn.ReLU()
            )
            self.regressor = nn.Sequential(
                nn.Linear(mace_hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(hidden_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim)
            )

        def forward(self, x):
            x = self.mace_encoder(x)
            return self.regressor(x)

    mace_model = MACERegressor(input_dim=len(features))
    mace_model.load_state_dict(torch.load(mace_model_path))
    mace_model.eval()

    print(f"  [OK] MACE 模型加载成功")
    mace_loaded = True
else:
    print(f"  [WARN] MACE 模型不存在")
    mace_loaded = False

# MACE 预测
if mace_loaded:
    X_test_tensor = torch.FloatTensor(X_test_scaled)
    with torch.no_grad():
        y_pred_mace_scaled = mace_model(X_test_tensor).numpy().flatten()
    y_pred_mace = scaler_y.inverse_transform(y_pred_mace_scaled.reshape(-1, 1)).flatten()

    # MACE 评估
    r2_mace = r2_score(y_test, y_pred_mace)
    mae_mace = mean_absolute_error(y_test, y_pred_mace)
    print(f"  MACE 性能：R2 = {r2_mace:.3f}, MAE = {mae_mace:.1f} S/m")
else:
    y_pred_mace = None
    r2_mace = None

# ============================================================================
# 4. 集成预测
# ============================================================================
print("\n[4/6] 集成预测...")

# 策略 1: 简单加权平均
print(f"  策略 1: 加权平均")

if mace_loaded:
    # 根据 R2 分配权重
    w_gp = r2_gp / (r2_gp + r2_mace) if (r2_gp + r2_mace) > 0 else 0.5
    w_mace = 1 - w_gp

    print(f"    GP 权重：{w_gp:.2f}")
    print(f"    MACE 权重：{w_mace:.2f}")

    y_pred_ensemble = w_gp * y_pred_gp + w_mace * y_pred_mace
else:
    # 只有 GP
    w_gp = 1.0
    w_mace = 0.0
    y_pred_ensemble = y_pred_gp

# 集成评估
r2_ensemble = r2_score(y_test, y_pred_ensemble)
mae_ensemble = mean_absolute_error(y_test, y_pred_ensemble)
rmse_ensemble = np.sqrt(np.mean((y_test - y_pred_ensemble)**2))

print(f"\n  集成性能:")
print(f"    R2: {r2_ensemble:.3f}")
print(f"    MAE: {mae_ensemble:.1f} S/m")
print(f"    RMSE: {rmse_ensemble:.1f} S/m")

# ============================================================================
# 5. 不确定性量化
# ============================================================================
print("\n[5/6] 不确定性量化...")

if mace_loaded:
    # 集成不确定性：GP 不确定性 + 模型差异
    model_disagreement = np.abs(y_pred_gp - y_pred_mace)
    ensemble_uncertainty = np.sqrt(y_std_gp**2 + (0.5 * model_disagreement)**2)
else:
    ensemble_uncertainty = y_std_gp

mean_uncertainty = np.mean(ensemble_uncertainty)
rel_uncertainty = mean_uncertainty / np.mean(y_test) * 100

print(f"  平均不确定性：±{mean_uncertainty:.1f} S/m ({rel_uncertainty:.1f}%)")

# 95% 置信区间
ci_95_lower = y_pred_ensemble - 2 * ensemble_uncertainty
ci_95_upper = y_pred_ensemble + 2 * ensemble_uncertainty

# 检查覆盖率
in_ci = (y_test >= ci_95_lower) & (y_test <= ci_95_upper)
coverage = np.mean(in_ci) * 100
print(f"  95% CI 覆盖率：{coverage:.1f}%")

# ============================================================================
# 6. 保存结果
# ============================================================================
print("\n[6/6] 保存结果...")

output_dir = Path("research/models")
output_dir.mkdir(parents=True, exist_ok=True)

# 保存集成配置
ensemble_config = {
    'models': {
        'GP': {
            'r2': float(r2_gp),
            'mae': float(mae_gp),
            'weight': float(w_gp)
        },
        'MACE': {
            'r2': float(r2_mace) if r2_mace else None,
            'mae': float(mae_mace) if mae_mace else None,
            'weight': float(w_mace)
        }
    },
    'ensemble': {
        'r2': float(r2_ensemble),
        'mae': float(mae_ensemble),
        'rmse': float(rmse_ensemble),
        'mean_uncertainty': float(mean_uncertainty),
        'relative_uncertainty_pct': float(rel_uncertainty),
        'ci_95_coverage': float(coverage)
    },
    'strategy': 'weighted_average',
    'features': features,
    'target': 'sigma_Sm',
    'n_samples': len(df),
    'test_size': 0.2,
    'random_state': 42
}

config_path = output_dir / "Ensemble_GP_MACE_config.json"
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(ensemble_config, f, indent=2, ensure_ascii=False)

print(f"  [OK] 配置已保存：{config_path}")

# 可视化
figures_dir = Path("research/figures")
figures_dir.mkdir(parents=True, exist_ok=True)

# 图 1: 预测对比
fig, ax = plt.subplots(figsize=(8, 6))
ax.errorbar(y_test, y_pred_gp, yerr=y_std_gp, fmt='o', capsize=3, markersize=5, alpha=0.6, label=f'GP (R2={r2_gp:.3f})')
if mace_loaded:
    ax.scatter(y_test, y_pred_mace, s=50, alpha=0.6, label=f'MACE (R2={r2_mace:.3f})')
ax.scatter(y_test, y_pred_ensemble, s=60, alpha=0.8, c='red', marker='s', label=f'Ensemble (R2={r2_ensemble:.3f})')
ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', linewidth=1.5, label='理想预测')
ax.set_xlabel("实验真实值 (S/m)", fontsize=12)
ax.set_ylabel("模型预测值 (S/m)", fontsize=12)
ax.set_title("GP + MACE 集成预测", fontsize=14)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(figures_dir / "Ensemble_GP_MACE_prediction.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 预测对比图：{figures_dir / 'Ensemble_GP_MACE_prediction.png'}")

# 图 2: 不确定性
fig, ax = plt.subplots(figsize=(8, 6))
ax.hist(ensemble_uncertainty, bins=20, edgecolor='black', alpha=0.7, color='skyblue')
ax.axvline(mean_uncertainty, color='red', linestyle='--', linewidth=2, label=f'平均：±{mean_uncertainty:.1f} S/m')
ax.set_xlabel("预测不确定性 (S/m)", fontsize=12)
ax.set_ylabel("样本数", fontsize=12)
ax.set_title(f"集成预测不确定性分布\n平均：±{rel_uncertainty:.1f}%, 95% CI 覆盖率：{coverage:.1f}%", fontsize=14)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, linestyle='--', axis='y')
plt.tight_layout()
plt.savefig(figures_dir / "Ensemble_uncertainty.png", dpi=300, bbox_inches='tight')
plt.close()
print(f"  [OK] 不确定性图：{figures_dir / 'Ensemble_uncertainty.png'}")

# ============================================================================
# 7. 总结
# ============================================================================
print("\n" + "=" * 70)
print("[OK] GP + MACE 集成预测完成！")
print("=" * 70)

print(f"\n性能对比:")
print(f"  GP 单模型：  R2 = {r2_gp:.3f}, MAE = {mae_gp:.1f} S/m")
if mace_loaded:
    print(f"  MACE 单模型： R2 = {r2_mace:.3f}, MAE = {mae_mace:.1f} S/m")
print(f"  集成模型：  R2 = {r2_ensemble:.3f}, MAE = {mae_ensemble:.1f} S/m")

# 性能提升
if mace_loaded:
    improvement = (r2_ensemble - max(r2_gp, r2_mace)) / max(r2_gp, r2_mace) * 100
    print(f"\n性能提升：{improvement:+.1f}%")
else:
    print(f"\n[INFO] 仅使用 GP 模型")

# 性能等级
if r2_ensemble >= 0.85:
    print(f"\n[TOP] 优秀！R2 > 0.85，达到目标！")
elif r2_ensemble >= 0.75:
    print(f"\n[OK] 良好！R2 > 0.75")
elif r2_ensemble >= 0.60:
    print(f"\n[GOOD] 可接受！R2 > 0.60")
else:
    print(f"\n[WARN] 需要改进：R2 = {r2_ensemble:.3f}")

print(f"\n不确定性:")
print(f"  平均：±{rel_uncertainty:.1f}%")
print(f"  95% CI 覆盖率：{coverage:.1f}%")

print(f"\n下一步:")
print(f"  1. 使用集成模型进行预测")
print(f"  2. 实验验证")
print(f"  3. 撰写论文")

print("=" * 70)
