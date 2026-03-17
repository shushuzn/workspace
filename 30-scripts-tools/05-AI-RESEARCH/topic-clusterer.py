#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topic Clustering (Level 4)
主题聚类
"""

import os
import json
from pathlib import Path
from datetime import datetime

class TopicClusterer:
    """主题聚类器"""
    
    def __init__(self):
        self.trends_file = Path(r"D:\obsidian\Vault\Arxiv\daily\2026\03\2026-03-05\trends\trends.json")
        self.output_dir = Path(r"D:\obsidian\Vault\Arxiv\daily\2026\03\2026-03-05\clusters")
        
    def cluster_topics(self):
        """聚类主题"""
        print("=" * 60)
        print("Topic Clustering (Level 4)")
        print("=" * 60)
        
        # 读取趋势数据
        print(f"\n[1/3] Loading trends...")
        with open(self.trends_file, 'r', encoding='utf-8') as f:
            trends = json.load(f)
        print(f"  Loaded trends from {trends['date']}")
        
        # 主题聚类
        print(f"\n[2/3] Clustering topics...")
        clusters = self._perform_clustering(trends)
        print(f"  Created {len(clusters)} clusters")
        
        # 研究网络构建
        print(f"\n[3/3] Building research network...")
        network = self._build_network(clusters)
        print(f"  Built network with {len(network['nodes'])} nodes")
        
        # 保存结果
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        result = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'clusters': clusters,
            'network': network
        }
        
        output_file = self.output_dir / "clusters.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n  Saved to clusters.json")
        
        print("\n" + "=" * 60)
        print("[COMPLETE]")
        print("=" * 60)
        
        return result
    
    def _perform_clustering(self, trends):
        """执行聚类"""
        # 基于热点话题聚类
        clusters = []
        
        hot_topics = trends.get('hot_topics', [])
        
        # 聚类 1: 氧化物电解质
        oxide_topics = [t for t in hot_topics if any(kw in t['topic'].lower() for kw in ['oxide', 'LLZO', 'garnet'])]
        if oxide_topics:
            clusters.append({
                'id': 1,
                'name': 'Oxide Electrolytes',
                'topics': oxide_topics,
                'size': sum(t['count'] for t in oxide_topics),
                'keywords': ['LLZO', 'garnet', 'oxide'],
                'research_gap': 'Low ionic conductivity at room temperature'
            })
        
        # 聚类 2: 界面工程
        interface_topics = [t for t in hot_topics if any(kw in t['topic'].lower() for kw in ['interface', 'coating', 'ALD'])]
        if interface_topics:
            clusters.append({
                'id': 2,
                'name': 'Interface Engineering',
                'topics': interface_topics,
                'size': sum(t['count'] for t in interface_topics),
                'keywords': ['coating', 'interface', 'ALD'],
                'research_gap': 'Long-term stability unclear'
            })
        
        # 聚类 3: 复合电解质
        composite_topics = [t for t in hot_topics if any(kw in t['topic'].lower() for kw in ['composite', 'hybrid', 'polymer'])]
        if composite_topics:
            clusters.append({
                'id': 3,
                'name': 'Composite Electrolytes',
                'topics': composite_topics,
                'size': sum(t['count'] for t in composite_topics),
                'keywords': ['composite', 'hybrid', 'polymer-ceramic'],
                'research_gap': 'Optimal composition ratio'
            })
        
        return clusters
    
    def _build_network(self, clusters):
        """构建研究网络"""
        nodes = []
        edges = []
        
        # 添加聚类节点
        for cluster in clusters:
            nodes.append({
                'id': f"cluster_{cluster['id']}",
                'type': 'cluster',
                'name': cluster['name'],
                'size': cluster['size']
            })
        
        # 添加聚类之间的边 (基于共同关键词)
        for i, c1 in enumerate(clusters):
            for j, c2 in enumerate(clusters):
                if i < j:
                    common_keywords = set(c1['keywords']) & set(c2['keywords'])
                    if common_keywords:
                        edges.append({
                            'source': f"cluster_{c1['id']}",
                            'target': f"cluster_{c2['id']}",
                            'weight': len(common_keywords)
                        })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def run(self):
        """运行主题聚类"""
        return self.cluster_topics()

def demo():
    """演示使用"""
    clusterer = TopicClusterer()
    clusterer.run()

if __name__ == "__main__":
    demo()
