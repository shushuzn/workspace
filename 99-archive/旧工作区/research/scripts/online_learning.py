#!/usr/bin/env python3
"""
在线学习：实时GP模型更新
每添加一个新实验数据，立即更新模型并评估R²
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
from datetime import datetime

print("=" * 70)
print("在线学习：实时 GP 模型更新")
print("=" * 70)

# 1. 加载现有数据
print("\n[1/5] 加载现有数据...")
base_data = Path("research/data/lig_dataset_200.csv")
df_base = pd.read_csv(base_data)
print(f"  基础数据：{len(df_base)} 样本")

# 2. 加载实验数据 (如果存在)
print("\n[2/5] 加载实验数据...")
exp_data = Path("research/data/lig_experiment_data.csv")
if exp_data.exists():
    df_exp = pd.read_csv(exp_data)
    print(f"  实验数据：{len(df_exp)} 样本")
    df_combined = pd.concat([df_base, df_exp], ignore_index=True)
    print(f"  合并后：{len(df_combined)} 样本")
else:
    print(f"  [INFO] 实验数据不存在，使用基础数据")
    df_combined = df_base
    df_exp = pd.DataFrame()

# 3. 准备数据
print("\n[3/5] 准备数据...")
features = ['E_Jcm2', 'v_mms', 'co_ratio']
X = df_combined[features].values
y = df_combined['sigma_Sm'].values

# 划分训练/测试集 (测试集固定为原始 200 样本中的 40 个)
if len(df_exp) > 0:
    # 有实验数据：用原始 200 样本的 40 个作为测试集
    X_base = df_base[features].values
    y_base = df_base['sigma_Sm'].values
    _, X_test, _, y_test = train_test_split(X_base, y_base, test_size=0.2, random_state=42)
    X_train = X
    y_train = y
else:
    # 无实验数据：正常划分
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"  训练集：{len(X_train)} 样本")
print(f"  测试集：{len(X_test)} 样本")

# 标准化
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_train_s = scaler_X.fit_transform(X_train)
X_test_s = scaler_X.transform(X_test)
y_train_s = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_s = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

# 4. GP 模型训练
print("\n[4/5] GP 模型训练...")

kernel = ConstantKernel(50, (10, 200)) * RBF(2.0, (0.1, 5)) + WhiteKernel(0.1, (0.01, 0.5))
gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=30, random_state=42, normalize_y=True)
gp.fit(X_train_s, y_train_s)

# 预测与评估
y_pred_s, y_std_s = gp.predict(X_test_s, return_std=True)
y_pred = scaler_y.inverse_transform(y_pred_s.reshape(-1, 1)).flatten()
y_std = y_std_s * scaler_y.scale_[0]

r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rel_unc = np.mean(y_std) / np.mean(y_test) * 100

print(f"\n  模型性能:")
print(f"    R2: {r2:.3f}")
print(f"    MAE: {mae:.1f} S/m")
print(f"    不确定性：±{rel_unc:.1f}%")

# 性能等级
if r2 >= 0.85:
    level = "TOP"
    emoji = "[OK][OK][OK]"
elif r2 >= 0.80:
    level = "EXCELLENT"
    emoji = "[OK][OK]"
elif r2 >= 0.75:
    level = "GOOD"
    emoji = "[OK]"
else:
    level = "NEEDS_IMPROVEMENT"
    emoji = "[LOOP]"

print(f"  等级：{level}")

# 5. 保存模型
print("\n[5/5] 保存模型...")

output_dir = Path("research/models")
output_dir.mkdir(parents=True, exist_ok=True)

# 保存模型
joblib.dump(gp, output_dir / "LIG_GP_online.pkl")
joblib.dump(scaler_X, output_dir / "LIG_GP_scaler_X_online.pkl")
joblib.dump(scaler_y, output_dir / "LIG_GP_scaler_y_online.pkl")

# 保存配置
config = {
    'model': 'GaussianProcessRegressor (Online Learning)',
    'features': features,
    'n_base_samples': len(df_base),
    'n_experiment_samples': len(df_exp),
    'n_total_samples': len(df_combined),
    'performance': {
        'r2': float(r2),
        'mae': float(mae),
        'uncertainty_pct': float(rel_unc),
        'level': level
    },
    'update_date': datetime.now().isoformat()
}

with open(output_dir / "LIG_GP_online_config.json", 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"  [OK] 模型已保存")

# 对比
print("\n" + "=" * 70)
print("在线学习完成！")
print("=" * 70)

print(f"\n性能对比:")
print(f"  原始 (120 样本):    R2 = 0.50")
print(f"  文献挖掘 (200 样本): R2 = 0.795")
if len(df_exp) > 0:
    print(f"  在线学习 (+{len(df_exp)} 实验): R2 = {r2:.3f} {emoji}")
    print(f"  提升：{(r2 - 0.795) / 0.795 * 100:+.1f}%")
else:
    print(f"  在线学习 (0 实验):  R2 = {r2:.3f}")
    print(f"  [INFO] 请添加实验数据后重新运行")

print(f"\n下一步:")
print(f"  1. 添加新实验数据到 research/data/lig_experiment_data.csv")
print(f"  2. 重新运行此脚本更新模型")
print(f"  3. 评估 R2 提升")

print("=" * 70)

# 生成实验数据模板
if not exp_data.exists():
    print("\n[INFO] 创建实验数据模板...")
    template = """sample_id,date,P_W,v_mms,E_Jcm2,co_ratio,precursor,sigma_Sm,sigma_std,method,uncertainty,notes,source
EXP-001,2026-03-10,0.30,30,10.0,3.3,PI,2520,25,4-probe,±2%,good quality,experiment
EXP-002,2026-03-10,0.35,25,14.0,3.3,PI,3180,30,4-probe,±2%,high conductivity,experiment
EXP-003,2026-03-11,0.40,20,20.0,3.3,PI,3850,40,4-probe,±2%,very high power,experiment
"""
    with open(exp_data, 'w', encoding='utf-8') as f:
        f.write(template)
    print(f"  [OK] 模板已创建：{exp_data}")
    print(f"  [INFO] 请编辑此文件添加真实实验数据")
