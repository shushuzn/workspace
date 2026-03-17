#!/usr/bin/env python3
"""
学科学术段位评价系统

功能:
- 学科/领域段位评定
- 多维度评分
- 段位对比可视化
- 晋升路径建议

使用:
    python domain_ranker.py --evaluate LIG
    python domain_ranker.py --compare LIG Graphene Perovskite
"""

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple
from datetime import datetime

# 设置 UTF-8 编码 (Windows 兼容)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


# 段位定义
RANKS = [
    ("黑铁", 0, 100, "[IRON]"),
    ("青铜", 100, 200, "[BRONZE]"),
    ("白银", 200, 300, "[SILVER]"),
    ("黄金", 300, 400, "[GOLD]"),
    ("铂金", 400, 500, "[PLAT]"),
    ("钻石", 500, 600, "[DIAM]"),
    ("大师", 600, 700, "[MASTER]"),
    ("宗师", 700, 800, "[GRAND]"),
]


@dataclass
class DomainData:
    """学科/领域数据"""
    name: str
    theory_score: float  # 0-100
    technology_score: float  # 0-100
    impact_score: float  # 0-100
    application_score: float  # 0-100
    talent_score: float  # 0-100
    funding_score: float  # 0-100


class DomainRanker:
    """学科学术段位评价器"""
    
    def __init__(self):
        # 权重配置
        self.weights = {
            'theory': 0.25,
            'technology': 0.25,
            'impact': 0.20,
            'application': 0.15,
            'talent': 0.10,
            'funding': 0.05
        }
    
    def calculate_score(self, domain: DomainData) -> Tuple[int, str, int]:
        """
        计算段位分数
        
        返回:
            (总分，段位名称，段位内等级)
        """
        # 加权总分 (0-100)
        weighted_score = (
            domain.theory_score * self.weights['theory'] +
            domain.technology_score * self.weights['technology'] +
            domain.impact_score * self.weights['impact'] +
            domain.application_score * self.weights['application'] +
            domain.talent_score * self.weights['talent'] +
            domain.funding_score * self.weights['funding']
        )
        
        # 转换为 1-800 分
        total_score = int(weighted_score * 8)
        total_score = max(1, min(800, total_score))
        
        # 确定段位
        rank_name, level = self.score_to_rank(total_score)
        
        return total_score, rank_name, level
    
    def score_to_rank(self, score: int) -> Tuple[str, int]:
        """分数转换为段位"""
        for rank_name, min_score, max_score, emoji in RANKS:
            if min_score < score <= max_score:
                level = score - min_score
                return rank_name, level
        return "宗师", 100
    
    def get_rank_info(self, score: int) -> Dict:
        """获取段位详细信息"""
        rank_name, level = self.score_to_rank(score)
        
        # 找到当前段位信息
        for r_name, min_s, max_s, emoji in RANKS:
            if r_name == rank_name:
                progress = level / 100 * 100
                next_rank = RANKS[RANKS.index((r_name, min_s, max_s, emoji)) + 1][0] if RANKS.index((r_name, min_s, max_s, emoji)) < len(RANKS) - 1 else None
                points_to_next = (min_s + 100) - score if next_rank else 0
                
                return {
                    'rank': rank_name,
                    'level': level,
                    'emoji': emoji,
                    'progress': progress,
                    'next_rank': next_rank,
                    'points_to_next': points_to_next
                }
        
        return {}
    
    def compare_domains(self, domains: Dict[str, DomainData]) -> List[Dict]:
        """比较多个领域"""
        results = []
        
        for name, data in domains.items():
            score, rank, level = self.calculate_score(data)
            rank_info = self.get_rank_info(score)
            
            results.append({
                'name': name,
                'score': score,
                'rank': rank,
                'level': level,
                'rank_info': rank_info,
                'scores': {
                    'theory': data.theory_score,
                    'technology': data.technology_score,
                    'impact': data.impact_score,
                    'application': data.application_score,
                    'talent': data.talent_score,
                    'funding': data.funding_score
                }
            })
        
        # 按总分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def print_ranking(self, results: List[Dict]):
        """打印排名结果"""
        print("\n" + "=" * 70)
        print("学科学术段位排名")
        print("=" * 70)
        print(f"{'排名':<4} {'领域':<20} {'段位':<12} {'分数':<8} {'进度':<20}")
        print("-" * 70)
        
        for i, result in enumerate(results, 1):
            rank_info = result['rank_info']
            emoji = rank_info.get('emoji', '⬛')
            progress_bar = self._create_progress_bar(rank_info.get('progress', 0))
            
            print(f"{i:<4} {result['name']:<20} {emoji} {result['rank']} {result['level']:<3} {result['score']:<8} {progress_bar}")
        
        print("=" * 70)
    
    def _create_progress_bar(self, progress: float, length: int = 20) -> str:
        """创建进度条"""
        filled = int(progress / 100 * length)
        bar = "#" * filled + "-" * (length - filled)
        return f"[{bar}] {progress:.0f}%"
    
    def generate_recommendations(self, domain: DomainData) -> List[str]:
        """生成晋升建议"""
        score, rank, level = self.calculate_score(domain)
        recommendations = []
        
        # 找出最弱的维度
        scores = {
            '理论基础': domain.theory_score,
            '技术成熟度': domain.technology_score,
            '学术影响力': domain.impact_score,
            '应用广度': domain.application_score,
            '人才储备': domain.talent_score,
            '资金投入': domain.funding_score
        }
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        # 生成建议
        for dim, score in sorted_scores[:3]:  # 最弱的 3 个维度
            if score < 50:
                recommendations.append(f"[URGENT] 优先提升{dim} (当前{score:.0f}分)")
            elif score < 70:
                recommendations.append(f"[FOCUS] 重点加强{dim} (当前{score:.0f}分)")
            else:
                recommendations.append(f"[OK] 继续保持{dim} (当前{score:.0f}分)")
        
        return recommendations


# 预定义领域数据
PREDEFINED_DOMAINS = {
    'LIG': DomainData(
        name='激光诱导石墨烯',
        theory_score=60,
        technology_score=55,
        impact_score=65,
        application_score=70,
        talent_score=50,
        funding_score=45
    ),
    'Graphene': DomainData(
        name='石墨烯',
        theory_score=85,
        technology_score=70,
        impact_score=90,
        application_score=75,
        talent_score=80,
        funding_score=75
    ),
    'DeepLearning': DomainData(
        name='深度学习',
        theory_score=75,
        technology_score=85,
        impact_score=95,
        application_score=90,
        talent_score=85,
        funding_score=80
    ),
    'CRISPR': DomainData(
        name='CRISPR 基因编辑',
        theory_score=80,
        technology_score=75,
        impact_score=85,
        application_score=70,
        talent_score=65,
        funding_score=70
    ),
    'Perovskite': DomainData(
        name='钙钛矿太阳能电池',
        theory_score=70,
        technology_score=65,
        impact_score=75,
        application_score=60,
        talent_score=60,
        funding_score=65
    )
}


def main():
    parser = argparse.ArgumentParser(description="学科学术段位评价系统")
    parser.add_argument("--evaluate", type=str, nargs="+",
                        help="评估指定领域 (如：LIG Graphene)")
    parser.add_argument("--compare", action="store_true",
                        help="比较所有预定义领域")
    parser.add_argument("--export", type=str,
                        help="导出结果到 JSON 文件")
    args = parser.parse_args()
    
    ranker = DomainRanker()
    
    if args.evaluate:
        # 评估指定领域
        domains_to_eval = {}
        for name in args.evaluate:
            if name in PREDEFINED_DOMAINS:
                domains_to_eval[name] = PREDEFINED_DOMAINS[name]
            else:
                print(f"[WARN] 未知领域：{name}，使用默认数据")
                domains_to_eval[name] = DomainData(
                    name=name,
                    theory_score=50,
                    technology_score=50,
                    impact_score=50,
                    application_score=50,
                    talent_score=50,
                    funding_score=50
                )
        
        results = ranker.compare_domains(domains_to_eval)
        ranker.print_ranking(results)
        
        # 生成建议
        for name in args.evaluate:
            if name in PREDEFINED_DOMAINS:
                print(f"\n[REPORT] {name} 晋升建议:")
                recs = ranker.generate_recommendations(PREDEFINED_DOMAINS[name])
                for rec in recs:
                    print(f"  {rec}")
    
    elif args.compare:
        # 比较所有预定义领域
        results = ranker.compare_domains(PREDEFINED_DOMAINS)
        ranker.print_ranking(results)
    
    else:
        # 默认显示所有领域
        print("学科学术段位评价系统")
        print("=" * 70)
        print("\n使用示例:")
        print("  python domain_ranker.py --evaluate LIG")
        print("  python domain_ranker.py --compare")
        print("\n预定义领域:")
        for name in PREDEFINED_DOMAINS:
            score, rank, level = ranker.calculate_score(PREDEFINED_DOMAINS[name])
            print(f"  - {name}: {rank} {level}级 ({score}/800)")
    
    return 0


if __name__ == "__main__":
    exit(main())
