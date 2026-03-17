#!/usr/bin/env python3
"""
快速生成 GP 特征重要性图表
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
import matplotlib.pyplot as plt

print("生成 GP 特征重要性图表...")

# 加载数据
data_path = Path("D:/OpenClaw/workspace/11-research/data/lig_dataset_200.csv")
df = pd.read_csv(data_path)

features = ['P_W', 'v_mms', 'E_Jcm2', 'co_ratio']
X = df[features].values
y = df['sigma_Sm'].values

# 数据集划分
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 标准化
scaler_X = StandardScaler()
scaler_y = StandardScaler()

X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

# GP 模型训练
kernel = ConstantKernel(100) * RBF(length_scale=[0.5, 0.5, 0.5, 1.0]) + WhiteKernel(0.05)

gp_model = GaussianProcessRegressor(
    kernel=kernel,
    n_restarts_optimizer=20,
    random_state=42,
    normalize_y=True
)

gp_model.fit(X_train_scaled, y_train_scaled)

# 提取长度尺度
kernel = gp_model.kernel_
if hasattr(kernel, 'k1'):
    rbf_component = kernel.k1
    if hasattr(rbf_component, 'k2'):
        rbf_component = rbf_component.k1
    if hasattr(rbf_component, 'length_scale'):
        length_scales = rbf_component.length_scale
    else:
        length_scales = 1.0
else:
    if hasattr(kernel, 'length_scale'):
        length_scales = kernel.length_scale
    else:
        length_scales = 1.0

if np.isscalar(length_scales):
    length_scales = [length_scales] * len(features)

# 计算重要性 (长度尺度越小越重要)
importance = 1 / (np.array(length_scales) + 1e-6)
importance = importance / importance.max() * 100

# 排序
sorted_idx = np.argsort(importance)[::-1]
features_sorted = [features[i] for i in sorted_idx]
importance_sorted = importance[sorted_idx]

# 特征名称映射
feature_names_cn = {
    'E_Jcm2': '功率密度 (J/cm²)',
    'v_mms': '扫描速度 (mm/s)',
    'co_ratio': 'C/O 比',
    'P_W': '功率 (W)'
}

# 生成图表
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
y_pos = np.arange(len(features_sorted))
ax.barh(y_pos, importance_sorted, color='steelblue')
ax.set_yticks(y_pos)
ax.set_yticklabels([feature_names_cn.get(f, f) for f in features_sorted], fontsize=12)
ax.invert_yaxis()
ax.set_xlabel('特征重要性 (%)', fontsize=14)
ax.set_title('GP 模型特征重要性\n(基于核函数长度尺度)', fontsize=16)
ax.grid(True, alpha=0.3, linestyle='--', axis='x')
plt.tight_layout()

# 保存
figures_dir = Path("D:/OpenClaw/workspace/11-research/figures")
figures_dir.mkdir(parents=True, exist_ok=True)
output_path = figures_dir / "GP_feature_importance.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"✓ 图表已保存：{output_path}")
print(f"\n特征重要性:")
for i, (f, imp) in enumerate(zip(features_sorted, importance_sorted), 1):
    cn_name = feature_names_cn.get(f, f)
    print(f"  {i}. {cn_name}: {imp:.1f}%")
