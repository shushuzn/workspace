#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Lake Management
数据湖管理
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

class DataLake:
    """数据湖管理系统"""
    
    def __init__(self):
        self.workspace = Path(r"D:\OpenClaw\workspace")
        self.data_lake_dir = self.workspace / 'data-lake'
        
        # 数据湖分层
        self.layers = {
            'raw': self.data_lake_dir / 'raw',
            'processed': self.data_lake_dir / 'processed',
            'curated': self.data_lake_dir / 'curated',
            'analytics': self.data_lake_dir / 'analytics'
        }
    
    def initialize(self):
        """初始化数据湖"""
        print("Initializing data lake...")
        
        for layer_name, layer_path in self.layers.items():
            layer_path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {layer_path}")
        
        print("Data lake initialized")
    
    def ingest_raw_data(self, date_str: str):
        """摄入原始数据 (Level 1)"""
        print(f"\nIngesting raw data for {date_str}...")
        
        source_file = self.workspace / 'obsidian-vault' / 'Arxiv' / 'daily' / date_str / 'raw' / 'papers.json'
        if not source_file.exists():
            print(f"  Source file not found: {source_file}")
            return False
        
        target_dir = self.layers['raw'] / date_str
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_file = target_dir / 'papers.json'
        shutil.copy2(source_file, target_file)
        
        print(f"  Copied to: {target_file}")
        return True
    
    def ingest_processed_data(self, date_str: str):
        """摄入处理后的数据 (Level 2-4)"""
        print(f"\nIngesting processed data for {date_str}...")
        
        # Level 2: 分类数据
        level2_file = self.workspace / 'obsidian-vault' / 'Arxiv' / 'daily' / date_str / 'classified' / 'all_classified.json'
        if level2_file.exists():
            target_dir = self.layers['processed'] / date_str
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(level2_file, target_dir / 'classified.json')
            print(f"  Level 2: Copied")
        
        # Level 3: 趋势数据
        level3_file = self.workspace / 'obsidian-vault' / 'Arxiv' / 'daily' / date_str / 'trends' / 'trends.json'
        if level3_file.exists():
            target_dir = self.layers['processed'] / date_str
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(level3_file, target_dir / 'trends.json')
            print(f"  Level 3: Copied")
        
        # Level 4: 聚类数据
        level4_file = self.workspace / 'obsidian-vault' / 'Arxiv' / 'daily' / date_str / 'clusters' / 'clusters.json'
        if level4_file.exists():
            target_dir = self.layers['processed'] / date_str
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(level4_file, target_dir / 'clusters.json')
            print(f"  Level 4: Copied")
    
    def ingest_curated_data(self, date_str: str):
        """摄入精选数据 (Level 5-6)"""
        print(f"\nIngesting curated data for {date_str}...")
        
        # Level 5: 报告
        level5_file = self.workspace / 'reports' / f'AUTO-RESEARCH-REPORT-{date_str}.md'
        if level5_file.exists():
            target_dir = self.layers['curated'] / date_str
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(level5_file, target_dir / 'report.md')
            print(f"  Level 5: Copied")
        
        # Level 6: 知识图谱
        level6_file = self.workspace / 'knowledge-graph' / 'materials-kg.json'
        if level6_file.exists():
            target_dir = self.layers['curated'] / date_str
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(level6_file, target_dir / 'knowledge-graph.json')
            print(f"  Level 6: Copied")
    
    def generate_analytics(self):
        """生成分析数据"""
        print(f"\nGenerating analytics...")
        
        analytics = {
            'generated_at': datetime.now().isoformat(),
            'total_dates': 0,
            'total_papers': 0,
            'by_date': []
        }
        
        # 统计各层数据
        for date_dir in sorted(self.layers['raw'].iterdir()):
            if date_dir.is_dir():
                raw_file = date_dir / 'papers.json'
                if raw_file.exists():
                    with open(raw_file, 'r', encoding='utf-8') as f:
                        papers = json.load(f)
                    
                    analytics['total_dates'] += 1
                    analytics['total_papers'] += len(papers)
                    analytics['by_date'].append({
                        'date': date_dir.name,
                        'papers': len(papers)
                    })
        
        # 保存分析数据
        analytics_dir = self.layers['analytics']
        analytics_dir.mkdir(parents=True, exist_ok=True)
        
        analytics_file = analytics_dir / 'summary.json'
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(analytics, f, indent=2, ensure_ascii=False)
        
        print(f"  Analytics saved to: {analytics_file}")
        print(f"  Total dates: {analytics['total_dates']}")
        print(f"  Total papers: {analytics['total_papers']}")
    
    def run(self, date_str: str = None):
        """运行数据湖管理"""
        from datetime import datetime
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        print("=" * 60)
        print("Data Lake Management")
        print("=" * 60)
        
        # 初始化数据湖
        print(f"\n[1/5] Initializing data lake...")
        self.initialize()
        
        # 摄入原始数据
        print(f"\n[2/5] Ingesting raw data...")
        self.ingest_raw_data(date_str)
        
        # 摄入处理数据
        print(f"\n[3/5] Ingesting processed data...")
        self.ingest_processed_data(date_str)
        
        # 摄入精选数据
        print(f"\n[4/5] Ingesting curated data...")
        self.ingest_curated_data(date_str)
        
        # 生成分析
        print(f"\n[5/5] Generating analytics...")
        self.generate_analytics()
        
        print("\n" + "=" * 60)
        print("[COMPLETE]")
        print("=" * 60)

def demo():
    """演示使用"""
    lake = DataLake()
    lake.run()

if __name__ == "__main__":
    demo()
