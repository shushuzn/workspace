#!/usr/bin/env python3
"""
CNT-LIG-石墨烯-MXene 四元复合材料预测模型

目标：
1. 构建四元复合数据集 (100+ 样本)
2. 研究四元协同效应
3. 发现最优四元比例
4. 对比二元/三元/四元性能演进

输出：
- 四元复合数据集
- 四元协同模型
- 材料设计指南
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
print("CNT-LIG-石墨烯-MXene 四元复合材料预测模型")
print("=" * 70)

# ============================================================================
# 1. 创建四元复合数据集
# ============================================================================
print("\n[1/6] 创建四元复合数据集...")

# 各组分本征性能
material_properties = {
    'CNT': {
        'conductivity': 1e6,      # S/m
        'strength': 63,           # GPa
        'youngs_modulus': 1000,   # GPa
        'dimension': '1D'
    },
    'LIG': {
        'conductivity': 2e3,      # S/m
        'strength': 20,           # GPa
        'youngs_modulus': 100,    # GPa
        'dimension': '3D'
    },
    'Graphene': {
        'conductivity': 1e6,      # S/m
        'strength': 130,          # GPa
        'youngs_modulus': 1000,   # GPa
        'dimension': '2D'
    },
    'MXene': {
        'conductivity': 6e4,      # S/m (Ti3C2Tx)
        'strength': 40,           # GPa
        'youngs_modulus': 330,    # GPa
        'dimension': '2D',
        'special': 'pseudocapacitance'  # 赝电容特性
    }
}

print("\n四元组分本征性能:")
for mat, props in material_properties.items():
    print(f"  {mat} ({props['dimension']}): σ={props['conductivity']:.2e} S/m")

# 生成四元复合数据
np.random.seed(42)
quaternary_data = []

# 四元比例组合 (总和=100%)
# 使用单纯形网格采样
steps = 10
for i in range(steps + 1):
    for j in range(steps + 1 - i):
        for k in range(steps + 1 - i - j):
            l = steps - i - j - k

            cnt_ratio = i / steps
            lig_ratio = j / steps
            graphene_ratio = k / steps
            mxene_ratio = l / steps

            # 过滤极端比例 (确保每种组分至少 5%)
            if min(cnt_ratio, lig_ratio, graphene_ratio, mxene_ratio) < 0.05:
                continue

            # 四元协同效应模型
            # 1. 二元协同
            synergy_cnt_lig = 0.3 * np.exp(-((cnt_ratio - 0.3) ** 2) / 0.05)
            synergy_cnt_g = 0.3 * np.exp(-((cnt_ratio - graphene_ratio) ** 2) / 0.02)
            synergy_cnt_mxene = 0.2 * np.exp(-((cnt_ratio - mxene_ratio) ** 2) / 0.03)
            synergy_lig_g = 0.15 * np.exp(-((lig_ratio - graphene_ratio) ** 2) / 0.05)
            synergy_lig_mxene = 0.15 * np.exp(-((lig_ratio - mxene_ratio) ** 2) / 0.05)
            synergy_g_mxene = 0.25 * np.exp(-((graphene_ratio - mxene_ratio) ** 2) / 0.02)

            # 2. 三元协同
            synergy_ternary = (
                0.15 * cnt_ratio * graphene_ratio * mxene_ratio +  # CNT-G-MXene
                0.10 * cnt_ratio * lig_ratio * graphene_ratio +    # CNT-LIG-G
                0.10 * cnt_ratio * lig_ratio * mxene_ratio         # CNT-LIG-MXene
            )

            # 3. 四元协同 (独特效应)
            # MXene 赝电容 + 石墨烯高导电 + CNT 长程 + LIG 柔性
            synergy_quaternary = 0.2 * cnt_ratio * lig_ratio * graphene_ratio * mxene_ratio * 20

            # 总协同因子
            total_synergy = 1.0 + (
                synergy_cnt_lig + synergy_cnt_g + synergy_cnt_mxene +
                synergy_lig_g + synergy_lig_mxene + synergy_g_mxene +
                synergy_ternary + synergy_quaternary
            )

            # 复合电导率 (混合规则 + 协同)
            base_conductivity = (
                cnt_ratio * material_properties['CNT']['conductivity'] +
                lig_ratio * material_properties['LIG']['conductivity'] +
                graphene_ratio * material_properties['Graphene']['conductivity'] +
                mxene_ratio * material_properties['MXene']['conductivity']
            )

            composite_conductivity = base_conductivity * total_synergy

            # 添加实验噪声
            noise = np.random.normal(1.0, 0.06)
            composite_conductivity *= noise

            quaternary_data.append({
                'sample_id': f'Q-{cnt_ratio:.2f}-{lig_ratio:.2f}-{graphene_ratio:.2f}-{mxene_ratio:.2f}',
                'cnt_ratio': cnt_ratio,
                'lig_ratio': lig_ratio,
                'graphene_ratio': graphene_ratio,
                'mxene_ratio': mxene_ratio,
                'base_conductivity': base_conductivity,
                'synergy_binary': synergy_cnt_lig + synergy_cnt_g + synergy_cnt_mxene + synergy_lig_g + synergy_lig_mxene + synergy_g_mxene,
                'synergy_ternary': synergy_ternary,
                'synergy_quaternary': synergy_quaternary,
                'total_synergy': total_synergy,
                'composite_conductivity': composite_conductivity,
                'method': 'Quaternary Composite',
                'source': 'Simulated'
            })

df_quaternary = pd.DataFrame(quaternary_data)
print(f"\n  生成四元样本：{len(df_quaternary)}")

# 保存数据集
DATA_DIR = Path("11-research/cnt-lig-graphene-mxene-quaternary/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

output_file = DATA_DIR / "quaternary_composite_dataset.csv"
df_quaternary.to_csv(output_file, index=False, encoding='utf-8-sig')
print(f"  已保存：{output_file}")

# ============================================================================
# 2. 数据分析
# ============================================================================
print("\n[2/6] 数据分析...")

print(f"\n四元比例范围:")
print(f"  CNT: {df_quaternary['cnt_ratio'].min():.0%} - {df_quaternary['cnt_ratio'].max():.0%}")
print(f"  LIG: {df_quaternary['lig_ratio'].min():.0%} - {df_quaternary['lig_ratio'].max():.0%}")
print(f"  Graphene: {df_quaternary['graphene_ratio'].min():.0%} - {df_quaternary['graphene_ratio'].max():.0%}")
print(f"  MXene: {df_quaternary['mxene_ratio'].min():.0%} - {df_quaternary['mxene_ratio'].max():.0%}")

print(f"\n电导率统计:")
print(f"  四元复合：{df_quaternary['composite_conductivity'].mean():.2e} S/m")
print(f"  最大值：{df_quaternary['composite_conductivity'].max():.2e} S/m")
print(f"  最小值：{df_quaternary['composite_conductivity'].min():.2e} S/m")

print(f"\n协同效应分解:")
print(f"  二元协同贡献：{df_quaternary['synergy_binary'].mean():.3f} ({df_quaternary['synergy_binary'].mean()/df_quaternary['total_synergy'].mean()*100:.1f}%)")
print(f"  三元协同贡献：{df_quaternary['synergy_ternary'].mean():.3f} ({df_quaternary['synergy_ternary'].mean()/df_quaternary['total_synergy'].mean()*100:.1f}%)")
print(f"  四元协同贡献：{df_quaternary['synergy_quaternary'].mean():.3f} ({df_quaternary['synergy_quaternary'].mean()/df_quaternary['total_synergy'].mean()*100:.1f}%)")

# ============================================================================
# 3. 一元→二元→三元→四元 演进对比
# ============================================================================
print("\n[3/6] 材料体系演进对比...")

# 加载历史数据
try:
    # 单一材料 (CNT/LIG)
    cnt_conductivity = 6.99e5  # CNT 平均
    lig_conductivity = 1.94e3  # LIG 平均
    graphene_conductivity = 1e6  # 石墨烯
    mxene_conductivity = 6e4  # MXene

    # 二元复合
    binary_data = pd.read_csv("11-research/cnt-lig-composite/data/cnt_lig_composite_dataset.csv")
    binary_conductivity = binary_data['composite_conductivity'].mean()
    binary_synergy = binary_data['synergy_factor'].mean() - 1

    # 三元复合
    ternary_data = pd.read_csv("11-research/cnt-lig-graphene-ternary/data/ternary_composite_dataset.csv")
    ternary_conductivity = ternary_data['composite_conductivity'].mean()
    ternary_synergy = ternary_data['synergy_3d'].mean() - 1

    print(f"\n📈 性能演进:")
    print(f"  单一 CNT:   {cnt_conductivity:.2e} S/m")
    print(f"  单一 LIG:   {lig_conductivity:.2e} S/m")
    print(f"  二元复合：  {binary_conductivity:.2e} S/m (协同 {binary_synergy*100:.1f}%)")
    print(f"  三元复合：  {ternary_conductivity:.2e} S/m (协同 {ternary_synergy*100:.1f}%)")
    print(f"  四元复合：  {df_quaternary['composite_conductivity'].mean():.2e} S/m (协同 {(df_quaternary['total_synergy'].mean()-1)*100:.1f}%)")

    # 计算提升
    improvement_binary = (binary_conductivity / cnt_conductivity - 1) * 100
    improvement_ternary = (ternary_conductivity / binary_conductivity - 1) * 100
    improvement_quaternary = (df_quaternary['composite_conductivity'].mean() / ternary_conductivity - 1) * 100

    print(f"\n📊 相对提升:")
    print(f"  单一→二元：{improvement_binary:+.1f}%")
    print(f"  二元→三元：{improvement_ternary:+.1f}%")
    print(f"  三元→四元：{improvement_quaternary:+.1f}%")

except FileNotFoundError as e:
    print(f"  ⚠️  历史数据未找到：{e}")
    print(f"  仅显示四元数据")

# ============================================================================
# 4. 最优比例发现
# ============================================================================
print("\n[4/6] 最优比例发现...")

# 找到最优四元比例
optimal_idx = df_quaternary['composite_conductivity'].idxmax()
optimal_row = df_quaternary.loc[optimal_idx]

print(f"\n🏆 最优四元比例:")
print(f"  CNT: {optimal_row['cnt_ratio']:.0%}")
print(f"  LIG: {optimal_row['lig_ratio']:.0%}")
print(f"  Graphene: {optimal_row['graphene_ratio']:.0%}")
print(f"  MXene: {optimal_row['mxene_ratio']:.0%}")
print(f"  电导率：{optimal_row['composite_conductivity']:.2e} S/m")
print(f"  总协同因子：{optimal_row['total_synergy']:.2f}x")

# 分析 Top 10% 样本
top_10_threshold = df_quaternary['composite_conductivity'].quantile(0.9)
top_10_samples = df_quaternary[df_quaternary['composite_conductivity'] >= top_10_threshold]

print(f"\n📊 Top 10% 高性能样本:")
print(f"  样本数：{len(top_10_samples)}")
print(f"  平均比例:")
print(f"    CNT: {top_10_samples['cnt_ratio'].mean():.0%} +/- {top_10_samples['cnt_ratio'].std():.0%}")
print(f"    LIG: {top_10_samples['lig_ratio'].mean():.0%} +/- {top_10_samples['lig_ratio'].std():.0%}")
print(f"    Graphene: {top_10_samples['graphene_ratio'].mean():.0%} +/- {top_10_samples['graphene_ratio'].std():.0%}")
print(f"    MXene: {top_10_samples['mxene_ratio'].mean():.0%} +/- {top_10_samples['mxene_ratio'].std():.0%}")

# ============================================================================
# 5. 预测模型训练
# ============================================================================
print("\n[5/6] 预测模型训练...")

FEATURES = ['cnt_ratio', 'lig_ratio', 'graphene_ratio', 'mxene_ratio']
TARGET = 'composite_conductivity'

X = df_quaternary[FEATURES].values
y = np.log10(df_quaternary[TARGET].values)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"  训练集：{len(X_train)} 样本")
print(f"  测试集：{len(X_test)} 样本")

scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_train_scaled = scaler_X.fit_transform(X_train)
X_test_scaled = scaler_X.transform(X_test)
y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
y_test_scaled = scaler_y.transform(y_test.reshape(-1, 1)).flatten()

print("\n  训练 GP 模型...")
kernel = ConstantKernel(1.0) * RBF(length_scale=1.0) + WhiteKernel(noise_level=0.1)
gp_model = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=5, random_state=42)
gp_model.fit(X_train_scaled, y_train_scaled)

y_pred_scaled = gp_model.predict(X_test_scaled)
y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()

r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

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
print("\n[6/6] 保存结果...")

MODELS_DIR = Path("11-research/cnt-lig-graphene-mxene-quaternary/models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)

import pickle
model_path = MODELS_DIR / "quaternary_gp_model.pkl"
with open(model_path, 'wb') as f:
    pickle.dump({
        'gp_model': gp_model,
        'scaler_X': scaler_X,
        'scaler_y': scaler_y,
        'features': FEATURES,
        'target': TARGET
    }, f)
print(f"  模型已保存：{model_path}")

REPORTS_DIR = Path("11-research/cnt-lig-graphene-mxene-quaternary/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

results = {
    'summary': {
        'total_samples': len(df_quaternary),
        'optimal_ratio': {
            'cnt': float(optimal_row['cnt_ratio']),
            'lig': float(optimal_row['lig_ratio']),
            'graphene': float(optimal_row['graphene_ratio']),
            'mxene': float(optimal_row['mxene_ratio'])
        },
        'optimal_conductivity': float(optimal_row['composite_conductivity']),
        'total_synergy': float(optimal_row['total_synergy'])
    },
    'synergy_breakdown': {
        'binary_contribution': float(df_quaternary['synergy_binary'].mean()),
        'ternary_contribution': float(df_quaternary['synergy_ternary'].mean()),
        'quaternary_contribution': float(df_quaternary['synergy_quaternary'].mean())
    },
    'model_performance': {
        'r2': float(r2),
        'mae': float(mae),
        'rmse': float(rmse),
        'cv_r2_mean': float(cv_r2_mean),
        'cv_r2_std': float(cv_r2_std)
    }
}

results_file = REPORTS_DIR / "quaternary_analysis_results.json"
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"  结果已保存：{results_file}")

print(f"\n[OK] 四元复合材料分析完成！")
print(f"\n关键发现:")
print(f"  1. 最优四元比例：CNT {optimal_row['cnt_ratio']:.0%} / LIG {optimal_row['lig_ratio']:.0%} / G {optimal_row['graphene_ratio']:.0%} / MXene {optimal_row['mxene_ratio']:.0%}")
print(f"  2. 四元协同增强：{(optimal_row['total_synergy'] - 1) * 100:.0f}%")
print(f"  3. 模型预测 R²: {r2:.4f}")
