#!/usr/bin/env python3
"""
CNT 基复合材料 主动学习 + 高通量筛选系统

目标：
1. 基于现有模型推荐最优实验点
2. 模拟高通量筛选过程
3. 生成实验优先级列表
4. 形成"预测→设计→筛选→验证"完整闭环

输出：
- 主动学习推荐系统
- 高通量筛选结果
- 实验优先级列表
- 完整研究闭环
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import pickle
import json

print("=" * 70)
print("CNT 基复合材料 主动学习 + 高通量筛选系统")
print("=" * 70)

# ============================================================================
# 1. 加载预训练模型
# ============================================================================
print("\n[1/7] 加载预训练模型...")

MODEL_PATH = Path("11-research/cnt-lig-inverse-design/models/inverse_design_model.pkl")

try:
    with open(MODEL_PATH, 'rb') as f:
        model_data = pickle.load(f)
    gp_model = model_data['gp_model']
    scaler_X = model_data['scaler_X']
    scaler_y = model_data['scaler_y']
    features = model_data['features']
    print(f"  模型加载成功")
    print(f"  特征：{features}")
except FileNotFoundError:
    print(f"  ⚠️  模型未找到，使用模拟数据")
    # 创建简化模型
    gp_model = None
    features = ['cnt_ratio', 'lig_ratio', 'graphene_ratio', 'mxene_ratio', 'pedot_ratio']

# ============================================================================
# 2. 生成候选实验空间
# ============================================================================
print("\n[2/7] 生成候选实验空间...")

# 使用拉丁超立方采样生成候选点
from scipy.stats import qmc

n_candidates = 1000
sampler = qmc.LatinHypercube(d=len(features), seed=42)
candidate_samples = sampler.random(n=n_candidates)

# 缩放到实际范围 (0.1-0.5)
lower_bounds = [0.1] * len(features)
upper_bounds = [0.5] * len(features)

candidate_samples = qmc.scale(candidate_samples, lower_bounds, upper_bounds)

# 确保总和≈1 (归一化)
candidate_samples = candidate_samples / candidate_samples.sum(axis=1, keepdims=True)

print(f"  候选实验点数：{n_candidates}")
print(f"  特征维度：{len(features)}")

# ============================================================================
# 3. 主动学习 - 不确定性采样
# ============================================================================
print("\n[3/7] 主动学习 - 不确定性采样...")

def acquisition_function_ucb(gp_model, X_samples, scaler_X, kappa=2.0):
    """
    Upper Confidence Bound (UCB) 采集函数
    
    UCB = μ(x) + κ * σ(x)
    
    平衡探索 (高不确定性) 和利用 (高预测值)
    """
    if gp_model is None:
        # 模拟不确定性
        return np.random.random(len(X_samples))

    X_scaled = scaler_X.transform(X_samples)
    y_pred, y_std = gp_model.predict(X_scaled, return_std=True)

    # UCB 分数 (最大化)
    ucb_score = y_pred + kappa * y_std

    return ucb_score, y_pred, y_std

ucb_scores, predictions, uncertainties = acquisition_function_ucb(gp_model, candidate_samples, scaler_X)

print(f"  UCB 分数范围：{ucb_scores.min():.3f} - {ucb_scores.max():.3f}")
print(f"  预测电导率范围：{10**predictions.min():.2e} - {10**predictions.max():.2e} S/m")
print(f"  不确定性范围：{uncertainties.min():.3f} - {uncertainties.max():.3f}")

# ============================================================================
# 4. 推荐 Top N 实验
# ============================================================================
print("\n[4/7] 推荐 Top 实验...")

n_recommend = 20
top_indices = np.argsort(ucb_scores)[::-1][:n_recommend]

recommended_experiments = []
for i, idx in enumerate(top_indices, 1):
    exp = {
        'rank': i,
        'ucb_score': float(ucb_scores[idx]),
        'predicted_conductivity': float(10**predictions[idx]),
        'uncertainty': float(uncertainties[idx]),
        'exploration_score': float(uncertainties[idx] / uncertainties.max()),
        'exploitation_score': float(predictions[idx] / predictions.max())
    }
    for j, feat in enumerate(features):
        exp[feat] = float(candidate_samples[idx][j])
    recommended_experiments.append(exp)

print(f"\n  Top 5 推荐实验:")
print(f"{'排名':<6} {'预测电导率':<15} {'不确定性':<12} {'探索':<8} {'利用':<8}")
print("-" * 60)
for exp in recommended_experiments[:5]:
    print(f"{exp['rank']:<6} {exp['predicted_conductivity']:.2e}  {exp['uncertainty']:<12.4f} "
          f"{exp['exploration_score']:<8.3f} {exp['exploitation_score']:<8.3f}")

# ============================================================================
# 5. 高通量筛选模拟
# ============================================================================
print("\n[5/7] 高通量筛选模拟...")

# 定义筛选标准
screening_criteria = {
    'min_conductivity': 5e5,      # 最小电导率
    'max_uncertainty': 0.3,       # 最大不确定性
    'min_exploration': 0.3,       # 最小探索分数
    'cost_limit': 6.0             # 成本上限
}

# 成本计算
def calculate_cost(sample, features):
    cost_weights = {
        'cnt_ratio': 10.0,
        'lig_ratio': 1.0,
        'graphene_ratio': 8.0,
        'mxene_ratio': 5.0,
        'pedot_ratio': 3.0
    }
    cost = sum(sample[j] * cost_weights.get(features[j], 1.0) for j in range(len(sample)))
    return cost

# 筛选
passed_screening = []
for i, idx in enumerate(top_indices):
    sample = candidate_samples[idx]
    cost = calculate_cost(sample, features)

    if (10**predictions[idx] >= screening_criteria['min_conductivity'] and
        uncertainties[idx] <= screening_criteria['max_uncertainty'] and
        cost <= screening_criteria['cost_limit']):

        passed = {
            'sample_id': i + 1,
            'cost': cost,
            **{feat: float(sample[j]) for j, feat in enumerate(features)},
            'predicted_conductivity': float(10**predictions[idx]),
            'uncertainty': float(uncertainties[idx])
        }
        passed_screening.append(passed)

print(f"  筛选标准:")
for key, value in screening_criteria.items():
    print(f"    {key}: {value}")

print(f"\n  通过筛选：{len(passed_screening)}/{n_recommend}")
print(f"  通过率：{len(passed_screening) /n_recommend *100:.1f}%")

# ============================================================================
# 6. 实验优先级排序
# ============================================================================
print("\n[6/7] 实验优先级排序...")

def priority_score(exp, weights=None):
    """
    综合优先级评分
    
    score = w1*performance + w2*certainty + w3*cost_efficiency
    """
    if weights is None:
        weights = {'performance': 0.5, 'certainty': 0.3, 'cost': 0.2}

    # 归一化性能 (电导率)
    perf_score = np.log10(exp['predicted_conductivity']) / 6.0  # 归一化到 0-1

    # 确定性 (低不确定性 = 高分数)
    cert_score = 1.0 - exp['uncertainty']

    # 成本效益
    cost_score = 1.0 - (exp.get('cost', 5.0) / 10.0)

    total_score = (
        weights['performance'] * perf_score +
        weights['certainty'] * cert_score +
        weights['cost'] * cost_score
    )

    return total_score

# 计算优先级
for exp in passed_screening:
    exp['priority_score'] = priority_score(exp)

# 排序
passed_screening.sort(key=lambda x: x['priority_score'], reverse=True)

print(f"\n  Top 10 优先实验:")
print(f"{'优先级':<8} {'电导率':<15} {'成本':<8} {'CNT':<8} {'LIG':<8} {'G':<8}")
print("-" * 60)
for exp in passed_screening[:10]:
    print(f"{exp['priority_score']:<8.3f} {exp['predicted_conductivity']:.2e}  "
          f"{exp['cost']:<8.2f} {exp['cnt_ratio']:<8.2f} {exp['lig_ratio']:<8.2f} "
          f"{exp['graphene_ratio']:<8.2f}")

# ============================================================================
# 7. 保存结果
# ============================================================================
print("\n[7/7] 保存结果...")

OUTPUT_DIR = Path("11-research/cnt-lig-active-learning")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 保存推荐实验
RECOMMENDATIONS_DIR = OUTPUT_DIR / "recommendations"
RECOMMENDATIONS_DIR.mkdir(parents=True, exist_ok=True)

# Top 推荐
top_rec_file = RECOMMENDATIONS_DIR / "top_experiments.json"
with open(top_rec_file, 'w', encoding='utf-8') as f:
    json.dump({
        'total_candidates': n_candidates,
        'recommended': recommended_experiments,
        'passed_screening': passed_screening,
        'screening_criteria': screening_criteria
    }, f, ensure_ascii=False, indent=2)
print(f"  推荐实验：{top_rec_file}")

# 实验优先级列表
priority_file = RECOMMENDATIONS_DIR / "experiment_priority_list.csv"
if len(passed_screening) > 0:
    df_priority = pd.DataFrame(passed_screening)
    df_priority.to_csv(priority_file, index=False, encoding='utf-8-sig')
    print(f"  优先级列表：{priority_file}")

# 生成实验方案
protocol_file = RECOMMENDATIONS_DIR / "experimental_protocol.md"
with open(protocol_file, 'w', encoding='utf-8') as f:
    f.write("# CNT 基复合材料 实验方案\n\n")
    f.write("## 推荐实验 (Top 10)\n\n")
    f.write("| 优先级 | CNT | LIG | 石墨烯 | MXene | PEDOT | 预测电导率 | 成本 |\n")
    f.write("|--------|-----|-----|--------|-------|-------|------------|------|\n")
    for exp in passed_screening[:10]:
        f.write(f"| {exp['priority_score']:.3f} | {exp['cnt_ratio']:.0%} | "
                f"{exp['lig_ratio']:.0%} | {exp['graphene_ratio']:.0%} | "
                f"{exp['mxene_ratio']:.0%} | {exp['pedot_ratio']:.0%} | "
                f"{exp['predicted_conductivity']:.2e} | {exp['cost']:.1f} |\n")

    f.write("\n## 实验步骤\n\n")
    f.write("### 1. 材料准备\n")
    f.write("- CNT: 单壁/多壁碳纳米管\n")
    f.write("- LIG: 聚酰亚胺薄膜 (Kapton)\n")
    f.write("- 石墨烯：氧化石墨烯 (GO) 或还原氧化石墨烯 (rGO)\n")
    f.write("- MXene: Ti3C2Tx\n")
    f.write("- PEDOT: PEDOT:PSS 水分散液\n\n")

    f.write("### 2. 复合工艺\n")
    f.write("1. 按推荐比例称量各组分\n")
    f.write("2. 超声分散 30 分钟\n")
    f.write("3. 真空过滤成膜\n")
    f.write("4. 热压成型 (100°C, 10 MPa, 10 分钟)\n\n")

    f.write("### 3. 性能测试\n")
    f.write("- 电导率：四探针法\n")
    f.write("- 力学性能：拉伸测试\n")
    f.write("- 微观结构：SEM/TEM\n")
    f.write("- 拉曼光谱：ID/IG 比值\n\n")

    f.write("### 4. 数据反馈\n")
    f.write("- 将实验结果反馈到模型\n")
    f.write("- 更新主动学习推荐\n")
    f.write("- 迭代优化\n")

print(f"  实验方案：{protocol_file}")

# 生成可视化数据
viz_file = RECOMMENDATIONS_DIR / "screening_visualization.json"
with open(viz_file, 'w', encoding='utf-8') as f:
    viz_data = {
        'candidate_distribution': {
            'cnt_ratio': candidate_samples[:, 0].tolist() if 'cnt_ratio' in features else [],
            'lig_ratio': candidate_samples[:, 1].tolist() if 'lig_ratio' in features else [],
            'graphene_ratio': candidate_samples[:, 2].tolist() if 'graphene_ratio' in features else []
        },
        'ucb_scores': ucb_scores.tolist(),
        'predictions': predictions.tolist(),
        'uncertainties': uncertainties.tolist()
    }
    json.dump(viz_data, f, ensure_ascii=False, indent=2)
print(f"  可视化数据：{viz_file}")

print(f"\n[OK] 主动学习 + 高通量筛选系统完成！")
print(f"\n关键成果:")
print(f"  1. 候选实验空间：{n_candidates} 个")
print(f"  2. Top 推荐：{n_recommend} 个")
print(f"  3. 通过筛选：{len(passed_screening)} 个")
print(f"  4. 实验方案：已生成")
