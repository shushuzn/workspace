#!/usr/bin/env python3
"""
预测 - 实验对比分析

功能：
1. 加载实验数据
2. 与预测值对比
3. 计算误差
4. 生成对比报告
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

def load_experimental_data(data_path):
    """加载实验数据"""
    df = pd.read_csv(data_path)
    return df

def calculate_error(predicted, experimental):
    """计算相对误差"""
    return abs(predicted - experimental) / predicted * 100

def generate_comparison_report(experimental_data_path, predictions_path):
    """生成对比报告"""
    # 加载数据
    df_exp = load_experimental_data(experimental_data_path)

    with open(predictions_path, 'r', encoding='utf-8') as f:
        predictions = json.load(f)['recommended']

    # 对比分析
    results = []
    for _, row in df_exp.iterrows():
        exp_id = row['实验 ID']
        pred = next((p for p in predictions if f"EXP-2026-03-11-{p['rank']:03d}" == exp_id), None)

        if pred:
            predicted_cond = pred['predicted_conductivity']
            experimental_cond = row['电导率_平均']
            error = calculate_error(predicted_cond, experimental_cond)

            results.append({
                '实验 ID': exp_id,
                '预测电导率': predicted_cond,
                '实验电导率': experimental_cond,
                '相对误差 (%)': error,
                '状态': '合格' if error < 20 else '需优化'
            })

    # 生成报告
    report_df = pd.DataFrame(results)
    print(report_df)

    # 统计
    avg_error = report_df['相对误差 (%)'].mean()
    pass_rate = (report_df['相对误差 (%)'] < 20).mean() * 100

    print(f"\n平均误差：{avg_error:.1f}%")
    print(f"合格率 (<20% 误差): {pass_rate:.1f}%")

    return report_df

if __name__ == "__main__":
    # 示例使用
    report = generate_comparison_report(
        'data/experimental_results.csv',
        '../cnt-lig-active-learning/recommendations/top_experiments.json'
    )
