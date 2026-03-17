#!/usr/bin/env python3
"""
CNT-LIG-石墨烯 三元复合材料预测模型

目标：
1. 构建三元复合数据集 (100+ 样本)
2. 研究三元协同效应
3. 发现最优三元比例
4. 对比二元 vs 三元性能

输出：
- 三元复合数据集
- 三元协同模型
- 最优比例建议
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import json

print("=" * 70)
print("CNT-LIG-石墨烯 三元复合材料预测模型")
print("=" * 70)

# ============================================================================
# 1. 创建三元复合数据集
# ============================================================================
print("\n[1/5] 创建三元复合数据集...")

# 加载现有数据
CNT_DATA = Path("D:/OpenClaw/workspace/11-research/cnt-research/data/cnt_dataset_v4_real.csv")
LIG_DATA = Path("D:/OpenClaw/workspace/11-research/data/lig_dataset_200.csv")

df_cnt = pd.read_csv(CNT_DATA)
df_lig = pd.read_csv(LIG_DATA)

print(f"  CNT 样本：{len(df_cnt)}")
print(f"  LIG 样本：{len(df_lig)}")

# 石墨烯性能参数 (文献值)
graphene_properties = {
    'conductivity': 1e6,  # S/m (单层石墨烯)
    'strength': 130,  # GPa
    'youngs_modulus': 1000,  # GPa
    'specific_surface': 2630  # m²/g
}

print(f"  石墨烯电导率：{graphene_properties['conductivity']:.2e} S/m")

# 生成三元复合数据
np.random.seed(42)
ternary_data = []

# 三元比例组合 (CNT + LIG + Graphene = 100%)
# 使用三角网格采样
for cnt_ratio in np.linspace(0.1, 0.7, 7):  # 10% - 70%
    for lig_ratio in np.linspace(0.1, 0.8 - cnt_ratio, 8):
        graphene_ratio = 1.0 - cnt_ratio - lig_ratio
        
        if graphene_ratio < 0.1 or graphene_ratio > 0.6:
            continue
        
        # 随机采样 CNT 和 LIG 样本 (仅数值列)
        cnt_sample = df_cnt[['conductivity_Sm', 'diameter_nm', 'layers']].sample(n=3, random_state=42).mean(numeric_only=True)
        lig_sample = df_lig[['sigma_Sm', 'P_W', 'v_mms']].sample(n=3, random_state=42).mean(numeric_only=True)
        
        for idx in range(3):  # 每个比例 3 个重复
            # 各组分贡献
            cnt_conductivity = cnt_sample['conductivity_Sm'] if pd.notna(cnt_sample['conductivity_Sm']) else 1e5
            lig_conductivity = lig_sample['sigma_Sm'] if 'sigma_Sm' in lig_sample and pd.notna(lig_sample['sigma_Sm']) else 1000
            graphene_conductivity = graphene_properties['conductivity']
            
            # 三元协同效应
            # 假设：三元协同 > 二元协同
            # 最优区域：CNT 20-40%, LIG 30-50%, Graphene 20-40%
            synergy_2d = (
                0.3 * np.exp(-((cnt_ratio - 0.4) ** 2) / 0.1) +  # CNT-LIG 协同
                0.3 * np.exp(-((graphene_ratio - 0.3) ** 2) / 0.1) +  # CNT-Graphene 协同
                0.2 * np.exp(-((lig_ratio - 0.4) ** 2) / 0.1)  # LIG-Graphene 协同
            )
            
            # 三元协同增强
            synergy_3d = 1.0 + synergy_2d + 0.2 * cnt_ratio * lig_ratio * graphene_ratio * 10
            
            # 复合电导率
            composite_conductivity = (
                cnt_ratio * cnt_conductivity +
                lig_ratio * lig_conductivity +
                graphene_ratio * graphene_conductivity
            ) * synergy_3d
            
            # 添加噪声
            noise = np.random.normal(1.0, 0.08)
            composite_conductivity *= noise
            
            ternary_data.append({
                'sample_id': f'TERNARY-{cnt_ratio:.1f}-{lig_ratio:.1f}-{graphene_ratio:.1f}-{idx:02d}',
                'cnt_ratio': cnt_ratio,
                'lig_ratio': lig_ratio,
                'graphene_ratio': graphene_ratio,
                'cnt_conductivity': cnt_conductivity,
                'lig_conductivity': lig_conductivity,
                'graphene_conductivity': graphene_conductivity,
                'composite_conductivity': composite_conductivity,
                'synergy_2d': synergy_2d,
                'synergy_3d': synergy_3d,
                'total_synergy': synergy_3d - 1.0,
                'method': 'CNT-LIG-Graphene Ternary',
                'source': 'Simulated'
            })

df_ternary = pd.DataFrame(ternary_data)
print(f"  生成三元样本：{len(df_ternary)}")

# 保存数据集
DATA_DIR = Path("11-research/cnt-lig-graphene-ternary/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

output_file = DATA_DIR / "ternary_composite_dataset.csv"
df_ternary.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"  已保存：{output_file}")

# ============================================================================
# 2. 数据分析
# ============================================================================
print("\n[2/5] 数据分析...")

print(f"\n三元比例范围:")
print(f"  CNT: {df_ternary['cnt_ratio'].min():.1%} - {df_ternary['cnt_ratio'].max():.1%}")
print(f"  LIG: {df_ternary['lig_ratio'].min():.1%} - {df_ternary['lig_ratio'].max():.1%}")
print(f"  Graphene: {df_ternary['graphene_ratio'].min():.1%} - {df_ternary['graphene_ratio'].max():.1%}")

print(f"\n电导率统计:")
print(f"  三元复合：{df_ternary['composite_conductivity'].mean():.2e} S/m")
print(f"  最大值：{df_ternary['composite_conductivity'].max():.2e} S/m")

print(f"\n协同效应:")
print(f"  平均三元协同：{(df_ternary['synergy_3d'].mean() - 1) * 100:.1f}% 增强")
print(f"  最大三元协同：{(df_ternary['synergy_3d'].max() - 1) * 100:.1f}% 增强")

# ============================================================================
# 3. 二元 vs 三元对比
# ============================================================================
print("\n[3/5] 二元 vs 三元对比...")

# 加载二元复合数据
BINARY_DATA = Path("11-research/cnt-lig-composite/data/cnt_lig_composite_dataset.csv")
df_binary = pd.read_csv(BINARY_DATA)

print(f"\n性能对比:")
print(f"  二元复合 (CNT-LIG): {df_binary['composite_conductivity'].mean():.2e} S/m")
print(f"  三元复合 (CNT-LIG-G): {df_ternary['composite_conductivity'].mean():.2e} S/m")

improvement = (df_ternary['composite_conductivity'].mean() / df_binary['composite_conductivity'].mean() - 1) * 100
print(f"  三元提升：{improvement:.1f}%")

print(f"\n协同效应对比:")
print(f"  二元协同：{(df_binary['synergy_factor'].mean() - 1) * 100:.1f}% 增强")
print(f"  三元协同：{(df_ternary['synergy_3d'].mean() - 1) * 100:.1f}% 增强")

synergy_improvement = (df_ternary['synergy_3d'].mean() / df_binary['synergy_factor'].mean() - 1) * 100
print(f"  协同提升：{synergy_improvement:.1f}%")

# ============================================================================
# 4. 最优比例发现
# ============================================================================
print("\n[4/5] 最优比例发现...")

# 找到最优三元比例
optimal_idx = df_ternary['composite_conductivity'].idxmax()
optimal_row = df_ternary.loc[optimal_idx]

print(f"\n🏆 最优三元比例:")
print(f"  CNT: {optimal_row['cnt_ratio']:.0%}")
print(f"  LIG: {optimal_row['lig_ratio']:.0%}")
print(f"  Graphene: {optimal_row['graphene_ratio']:.0%}")
print(f"  电导率：{optimal_row['composite_conductivity']:.2e} S/m")
print(f"  协同因子：{optimal_row['synergy_3d']:.2f}x")

# 分析高性能够本 (Top 10%)
top_10_threshold = df_ternary['composite_conductivity'].quantile(0.9)
top_10_samples = df_ternary[df_ternary['composite_conductivity'] >= top_10_threshold]

print(f"\n📊 Top 10% 高性能样本特征:")
print(f"  样本数：{len(top_10_samples)}")
print(f"  CNT 比例：{top_10_samples['cnt_ratio'].mean():.0%} +/- {top_10_samples['cnt_ratio'].std():.0%}")
print(f"  LIG 比例：{top_10_samples['lig_ratio'].mean():.0%} +/- {top_10_samples['lig_ratio'].std():.0%}")
print(f"  石墨烯：{top_10_samples['graphene_ratio'].mean():.0%} +/- {top_10_samples['graphene_ratio'].std():.0%}")

# ============================================================================
# 5. 预测模型训练
# ============================================================================
print("\n[5/5] 预测模型训练...")

# 特征工程
FEATURES = ['cnt_ratio', 'lig_ratio', 'graphene_ratio']
TARGET = 'composite_conductivity'

X = df_ternary[FEATURES].values
y = np.log10(df_ternary[TARGET].values)

# 数据集划分
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"  训练集：{len(X_train)} 样本")
print(f"  测试集：{len(X_test)} 样本")

# 标准化
scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

# GP 模型训练
print("\n  训练 GP 模型...")
kernel = ConstantKernel(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1)
gp_model = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5, random_state=42)
gp_model.fit(X_train_scaled, y_train_scaled)

# 预测
y_pred_scaled = gp_model.predict(X_test_scaled)
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

# 评估
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

# 交叉验证
cv_scores = cross_val_score(gp_model, X_train_scaled, y_train_scaled, cv=5, scoring='r2')
cv_r2_mean = cv_scores.mean()
cv_r2_std = cv_scores.std()

print(f"\n  模型性能:")
print(f"    R² = {r2:.4f}")
print(f"    MAE = {mae:.4f}")
print(f"    RMSE = {rmse:.4f}")
print(f"    CV R² = {cv_r2_mean:.4f} (+/- {cv_r2_std:.4f})")

# ============================================================================
# 6. 保存结果
# ============================================================================
print("\n[6/5] 保存结果...")

# 保存模型
MODELS_DIR = Path("11-research/cnt-lig-graphene-ternary/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

import pickle
model_path = MODELS_DIR / "ternary_gp_model.pkl"
with open(model_path, 'wb') as f:
    pickle.dump({
        'gp_model': gp_model,
        'scaler_X': scaler_X,
        'scaler_y': scaler_y,
        'features': FEATURES,
        'target': TARGET
    }, f)
print(f"  模型已保存：{model_path}")

# 保存结果报告
REPORTS_DIR = Path("11-research/cnt-lig-graphene-ternary/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

results = {
    'summary': {
        'total_samples': len(df_ternary),
        'optimal_ratio': {
            'cnt': float(optimal_row['cnt_ratio']),
            'lig': float(optimal_row['lig_ratio']),
            'graphene': float(optimal_row['graphene_ratio'])
        },
        'optimal_conductivity': float(optimal_row['composite_conductivity']),
        'synergy_3d': float(optimal_row['synergy_3d'])
    },
    'binary_vs_ternary': {
        'binary_conductivity': float(df_binary['composite_conductivity'].mean()),
        'ternary_conductivity': float(df_ternary['composite_conductivity'].mean()),
        'improvement_percent': float(improvement),
        'synergy_improvement_percent': float(synergy_improvement)
    },
    'model_performance': {
        'r2': float(r2),
        'mae': float(mae),
        'rmse': float(rmse),
        'cv_r2_mean': float(cv_r2_mean),
        'cv_r2_std': float(cv_r2_std)
    },
    'top_10_percent': {
        'cnt_mean': float(top_10_samples['cnt_ratio'].mean()),
        'lig_mean': float(top_10_samples['lig_ratio'].mean()),
        'graphene_mean': float(top_10_samples['graphene_ratio'].mean())
    }
}

results_file = REPORTS_DIR / "ternary_analysis_results.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"  结果已保存：{results_file}")

print(f"\n[OK] 三元复合材料分析完成！")
print(f"\n关键发现:")
print(f"  1. 最优三元比例：CNT {optimal_row['cnt_ratio']:.0%} / LIG {optimal_row['lig_ratio']:.0%} / Graphene {optimal_row['graphene_ratio']:.0%}")
print(f"  2. 三元协同增强：{(optimal_row['synergy_3d'] - 1) * 100:.0f}%")
print(f"  3. 相比二元提升：{improvement:.0f}%")
print(f"  4. 模型预测 R²: {r2:.4f}")
