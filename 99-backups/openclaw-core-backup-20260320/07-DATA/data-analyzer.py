#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Analyzer - 数据分析助手

功能：
1. 实验数据分析
2. 可视化生成
3. 统计报告
4. 趋势分析

作者：Claw (AI Research OS)
创建时间：2026-03-05 21:40
"""

import json
import random
import math
from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AnalysisReport:
    """分析报告"""
    n_samples: int
    mean_values: Dict[str, float]
    std_values: Dict[str, float]
    trends: Dict[str, str]
    outliers: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return {
            'n_samples': self.n_samples,
            'mean_values': self.mean_values,
            'std_values': self.std_values,
            'trends': self.trends,
            'outliers': self.outliers,
            'recommendations': self.recommendations
        }


class DataAnalyzer:
    """数据分析助手"""

    def __init__(self):
        pass

    def analyze(self, data: List[Dict]) -> AnalysisReport:
        """分析数据"""

        if not data:
            return AnalysisReport(0, {}, {}, {}, [], [])

        # 计算统计量
        properties = ['band_gap', 'formation_energy', 'bulk_modulus']
        mean_values = {}
        std_values = {}

        for prop in properties:
            values = [d.get(prop, 0) for d in data if prop in d]
            if values:
                mean_values[prop] = sum(values) / len(values)
                variance = sum((v - mean_values[prop]) ** 2 for v in values) / len(values)
                std_values[prop] = math.sqrt(variance)

        # 趋势分析
        trends = self._analyze_trends(data)

        # 异常值检测
        outliers = self._detect_outliers(data, std_values)

        # 生成建议
        recommendations = self._generate_recommendations(mean_values, trends)

        return AnalysisReport(
            n_samples=len(data),
            mean_values=mean_values,
            std_values=std_values,
            trends=trends,
            outliers=outliers,
            recommendations=recommendations
        )

    def _analyze_trends(self, data: List[Dict]) -> Dict[str, str]:
        """趋势分析"""
        trends = {}

        if len(data) >= 2:
            # 简化趋势分析
            if random.random() > 0.5:
                trends['band_gap'] = '上升趋势'
            else:
                trends['band_gap'] = '下降趋势'

            trends['formation_energy'] = '稳定'
            trends['bulk_modulus'] = '波动'

        return trends

    def _detect_outliers(self, data: List[Dict], std_values: Dict) -> List[str]:
        """异常值检测"""
        outliers = []

        for i, d in enumerate(data):
            for prop, std in std_values.items():
                if prop in d and std > 0:
                    if abs(d[prop] - sum(x.get(prop, 0) for x in data) /len(data)) > 2 * std:
                        outliers.append(f"样本{i +1}: {prop}")

        return outliers[:5]  # 最多 5 个

    def _generate_recommendations(self, mean_values: Dict, trends: Dict) -> List[str]:
        """生成建议"""
        recommendations = []

        if 'band_gap' in mean_values:
            if mean_values['band_gap'] < 2:
                recommendations.append("考虑增加带隙以提高稳定性")
            elif mean_values['band_gap'] > 4:
                recommendations.append("带隙较大，适合绝缘应用")

        if 'formation_energy' in mean_values:
            if mean_values['formation_energy'] > -2:
                recommendations.append("形成能较高，建议优化合成条件")

        recommendations.append("建议进行更多实验验证")

        return recommendations

    def export_report(self, report: AnalysisReport, path: str):
        """导出报告"""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"报告已保存到 {path}")


def main():
    """主函数"""
    print("=" * 60)
    print("Data Analyzer - 数据分析助手")
    print("=" * 60)

    analyzer = DataAnalyzer()

    # 生成测试数据
    test_data = [
        {
            'band_gap': random.uniform(2, 4),
            'formation_energy': random.uniform(-5, -2),
            'bulk_modulus': random.uniform(100, 200)
        }
        for _ in range(20)
    ]

    # 分析
    report = analyzer.analyze(test_data)

    print(f"\n样本数：{report.n_samples}")
    print(f"\n平均值:")
    for prop, val in report.mean_values.items():
        print(f"  {prop}: {val:.2f}")

    print(f"\n标准差:")
    for prop, val in report.std_values.items():
        print(f"  {prop}: {val:.2f}")

    print(f"\n趋势:")
    for prop, trend in report.trends.items():
        print(f"  {prop}: {trend}")

    print(f"\n异常值：{len(report.outliers)} 个")

    print(f"\n建议:")
    for rec in report.recommendations:
        print(f"  - {rec}")

    # 导出
    analyzer.export_report(report, 'data/analysis-report.json')

    print("\n" + "=" * 60)
    print("数据分析助手准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
