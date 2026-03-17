#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trend Analysis (Level 3)
趋势分析
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

class TrendAnalyzer:
    """趋势分析器"""
    
    def __init__(self):
        self.classified_dir = Path(r"D:\obsidian\Vault\Arxiv\daily\2026\03\2026-03-05\classified")
        self.output_dir = Path(r"D:\obsidian\Vault\Arxiv\daily\2026\03\2026-03-05\trends")
        
    def analyze_trends(self):
        """分析趋势"""
        print("=" * 60)
        print("Trend Analysis (Level 3)")
        print("=" * 60)
        
        # 读取分类后的论文
        print(f"\n[1/4] Loading classified papers...")
        classified_file = self.classified_dir / "all_classified.json"
        with open(classified_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        print(f"  Loaded {len(papers)} papers")
        
        # 热点话题识别
        print(f"\n[2/4] Identifying hot topics...")
        hot_topics = self._identify_hot_topics(papers)
        print(f"  Identified {len(hot_topics)} hot topics")
        
        # 新兴方向发现
        print(f"\n[3/4] Discovering emerging fields...")
        emerging_fields = self._discover_emerging_fields(papers)
        print(f"  Discovered {len(emerging_fields)} emerging fields")
        
        # 技术演进分析
        print(f"\n[4/4] Analyzing technology evolution...")
        tech_evolution = self._analyze_tech_evolution(papers)
        print(f"  Analyzed {len(tech_evolution)} technologies")
        
        # 保存结果
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        trends = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_papers': len(papers),
            'hot_topics': hot_topics,
            'emerging_fields': emerging_fields,
            'technology_evolution': tech_evolution
        }
        
        output_file = self.output_dir / "trends.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(trends, f, indent=2, ensure_ascii=False)
        print(f"\n  Saved to trends.json")
        
        print("\n" + "=" * 60)
        print("[COMPLETE]")
        print("=" * 60)
        
        return trends
    
    def _identify_hot_topics(self, papers):
        """识别热点话题"""
        # 统计关键词频率
        keyword_counter = Counter()
        for paper in papers:
            keywords = paper.get('keywords', [])
            keyword_counter.update(keywords)
        
        # 获取前 10 个热点
        hot_topics = []
        for keyword, count in keyword_counter.most_common(10):
            hot_topics.append({
                'topic': keyword,
                'count': count,
                'percentage': count / len(papers) * 100
            })
        
        return hot_topics
    
    def _discover_emerging_fields(self, papers):
        """发现新兴方向"""
        # 高相关性但数量少的方向
        emerging = []
        
        # 统计材料体系分布
        material_counter = Counter()
        for paper in papers:
            material = paper['classification']['material_system']
            material_counter[material] += 1
        
        # 新兴方向：数量少但重要性高
        for paper in papers:
            if paper['importance_score'] >= 8.0:
                material = paper['classification']['material_system']
                if material_counter[material] < 10:  # 少于 10 篇
                    if not any(e['field'] == material for e in emerging):
                        emerging.append({
                            'field': material,
                            'papers': material_counter[material],
                            'trend': 'emerging'
                        })
        
        return emerging
    
    def _analyze_tech_evolution(self, papers):
        """分析技术演进"""
        # 技术成熟度分析
        tech_stages = {
            'emerging': [],
            'growing': [],
            'mature': []
        }
        
        # 统计各技术的论文数量和时间分布
        # TODO: 需要历史数据
        
        # 简化版本：基于关键词
        for paper in papers:
            keywords = paper.get('keywords', [])
            if any(kw in keywords for kw in ['machine learning', 'AI', 'deep learning']):
                tech_stages['emerging'].append('AI-designed materials')
            elif any(kw in keywords for kw in ['composite', 'hybrid']):
                tech_stages['growing'].append('composite electrolyte')
            elif any(kw in keywords for kw in ['sulfide', 'LGPS']):
                tech_stages['mature'].append('sulfide electrolyte')
        
        # 去重
        result = []
        for stage, techs in tech_stages.items():
            for tech in set(techs):
                result.append({
                    'technology': tech,
                    'stage': stage
                })
        
        return result
    
    def run(self):
        """运行趋势分析"""
        return self.analyze_trends()

def demo():
    """演示使用"""
    analyzer = TrendAnalyzer()
    analyzer.run()

if __name__ == "__main__":
    demo()
