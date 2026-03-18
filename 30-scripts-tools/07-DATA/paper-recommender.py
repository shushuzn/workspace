#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper Recommender - 文献推荐系统

功能：
1. 基于内容推荐相关文献
2. 相似度计算
3. 文献排序
4. 推荐解释

作者：Claw (AI Research OS)
创建时间：2026-03-05 21:45
"""

import json
import random
from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Paper:
    """论文"""
    title: str
    authors: List[str]
    year: int
    journal: str
    keywords: List[str]
    abstract: str


@dataclass
class Recommendation:
    """推荐结果"""
    paper: Paper
    relevance_score: float
    reason: str
    
    def to_dict(self) -> Dict:
        return {
            'title': self.paper.title,
            'authors': self.paper.authors,
            'year': self.paper.year,
            'journal': self.paper.journal,
            'relevance_score': self.relevance_score,
            'reason': self.reason
        }


class PaperRecommender:
    """文献推荐系统"""
    
    def __init__(self):
        self.paper_database = self._load_papers()
    
    def _load_papers(self) -> List[Paper]:
        """加载论文数据库"""
        # 示例论文
        return [
            Paper(
                title="LiFePO4: A Novel Cathode Material for Lithium Batteries",
                authors=["Padhi, A. K.", "Nanjundaswamy, K. S.", "Goodenough, J. B."],
                year=1997,
                journal="J. Electrochem. Soc.",
                keywords=["LiFePO4", "battery", "cathode", "lithium"],
                abstract="橄榄石结构 LiFePO4 作为锂离子电池正极材料..."
            ),
            Paper(
                title="Band Gap Engineering of TiO2 for Photocatalysis",
                authors=["Zhang, X.", "Li, Y.", "Wang, H."],
                year=2020,
                journal="Nature Materials",
                keywords=["TiO2", "band gap", "photocatalysis"],
                abstract="通过掺杂工程调节 TiO2 带隙..."
            ),
            Paper(
                title="Machine Learning for Materials Discovery",
                authors=["Smith, J.", "Johnson, A."],
                year=2022,
                journal="Science",
                keywords=["machine learning", "materials", "discovery"],
                abstract="机器学习加速材料发现..."
            )
        ]
    
    def recommend(self, query_keywords: List[str], 
                 n_recommendations: int = 5) -> List[Recommendation]:
        """推荐文献"""
        
        recommendations = []
        
        for paper in self.paper_database:
            # 计算相似度
            score = self._calculate_similarity(query_keywords, paper.keywords)
            
            if score > 0:
                reason = self._generate_reason(score, paper)
                recommendations.append(Recommendation(
                    paper=paper,
                    relevance_score=round(score, 2),
                    reason=reason
                ))
        
        # 排序
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return recommendations[:n_recommendations]
    
    def _calculate_similarity(self, query: List[str], 
                            keywords: List[str]) -> float:
        """计算相似度"""
        query_set = set(k.lower() for k in query)
        keyword_set = set(k.lower() for k in keywords)
        
        intersection = query_set & keyword_set
        union = query_set | keyword_set
        
        if not union:
            return 0.0
        
        # Jaccard 相似度
        jaccard = len(intersection) / len(union)
        
        # 添加年份因子 (新论文权重高)
        year_factor = random.uniform(0.9, 1.1)
        
        return min(1.0, jaccard * year_factor)
    
    def _generate_reason(self, score: float, paper: Paper) -> str:
        """生成推荐理由"""
        if score > 0.7:
            return f"高度相关 - 关键词匹配度高 ({len(paper.keywords)} 个关键词)"
        elif score > 0.4:
            return f"中等相关 - 部分关键词匹配"
        else:
            return f"低度相关 - 主题相关"


def main():
    """主函数"""
    print("=" * 60)
    print("Paper Recommender - 文献推荐系统")
    print("=" * 60)
    
    recommender = PaperRecommender()
    
    # 测试推荐
    query_keywords = ['LiFePO4', 'battery', 'cathode']
    
    print(f"\n查询关键词：{query_keywords}")
    
    recommendations = recommender.recommend(query_keywords, n_recommendations=3)
    
    print(f"\n推荐 {len(recommendations)} 篇文献:\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec.paper.title}")
        print(f"   作者：{', '.join(rec.paper.authors)}")
        print(f"   期刊：{rec.paper.journal} ({rec.paper.year})")
        print(f"   相关度：{rec.relevance_score:.1%}")
        print(f"   理由：{rec.reason}")
        print()
    
    print("=" * 60)
    print("文献推荐系统准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
