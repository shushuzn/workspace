#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper Classification and Annotation
论文分类标注 (Level 2)
"""

import os
import json
from pathlib import Path
from datetime import datetime

class PaperClassifier:
    """论文分类器"""

    def __init__(self):
        self.input_file = Path(r"D:\obsidian\Vault\Arxiv\daily\2026\03\2026-03-05\papers.json")
        self.output_dir = Path(r"D:\obsidian\Vault\Arxiv\daily\2026\03\2026-03-05\classified")

        # 分类关键词
        self.material_keywords = {
            'oxide': ['oxide', 'LLZO', 'LATP', 'LLTO', 'garnet', 'perovskite'],
            'sulfide': ['sulfide', 'LGPS', 'LPS', 'argyrodite', 'thiophosphate'],
            'polymer': ['polymer', 'PEO', 'PVDF', 'PAN', 'polyethylene oxide'],
            'composite': ['composite', 'hybrid', 'ceramic-polymer']
        }

        self.method_keywords = {
            'synthesis': ['sol-gel', 'hydrothermal', 'ball milling', 'synthesis'],
            'characterization': ['XRD', 'SEM', 'TEM', 'XPS', 'characterization'],
            'testing': ['EIS', 'CV', 'cycling', 'electrochemical'],
            'computation': ['DFT', 'calculation', 'simulation', 'machine learning']
        }

        self.application_keywords = {
            'solid-state battery': ['solid-state', 'all-solid', 'ASSB'],
            'Li-ion battery': ['Li-ion', 'LIB', 'lithium-ion'],
            'Li-S battery': ['Li-S', 'lithium-sulfur'],
            'Li-air battery': ['Li-air', 'lithium-air']
        }

    def classify_paper(self, paper):
        """分类单篇论文"""
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        text = title + ' ' + abstract

        # 材料体系分类
        material_class = self._classify(text, self.material_keywords)

        # 研究方法分类
        method_class = self._classify_multi(text, self.method_keywords)

        # 应用领域分类
        application_class = self._classify(text, self.application_keywords)

        # 关键词提取
        keywords = self._extract_keywords(text)

        # 重要性评分
        importance_score = self._calculate_importance(paper)

        # 相关性评分
        relevance_score = self._calculate_relevance(material_class, method_class)

        return {
            'arxiv_id': paper['arxiv_id'],
            'classification': {
                'material_system': material_class,
                'research_method': method_class,
                'application': application_class
            },
            'keywords': keywords,
            'importance_score': importance_score,
            'relevance_score': relevance_score,
            'tags': self._generate_tags(importance_score, relevance_score)
        }

    def _classify(self, text, keywords_dict):
        """单一分类"""
        best_match = 'other'
        best_count = 0

        for category, keywords in keywords_dict.items():
            count = sum(1 for kw in keywords if kw in text)
            if count > best_count:
                best_count = count
                best_match = category

        return best_match

    def _classify_multi(self, text, keywords_dict):
        """多重分类"""
        matches = []
        for category, keywords in keywords_dict.items():
            count = sum(1 for kw in keywords if kw in text)
            if count > 0:
                matches.append(category)
        return matches if matches else ['other']

    def _extract_keywords(self, text):
        """提取关键词"""
        all_keywords = []
        for keywords_dict in [self.material_keywords, self.method_keywords, self.application_keywords]:
            for category, keywords in keywords_dict.items():
                for kw in keywords:
                    if kw in text and kw not in all_keywords:
                        all_keywords.append(kw)
        return all_keywords[:10]  # 最多 10 个关键词

    def _calculate_importance(self, paper):
        """计算重要性评分"""
        score = 5.0  # 基础分

        # 高影响力期刊/会议
        # TODO: 根据 arXiv 类别调整

        # 关键词匹配度
        text = paper.get('title', '').lower() + ' ' + paper.get('abstract', '').lower()
        important_keywords = ['solid-state', 'high conductivity', 'interface', 'composite']
        for kw in important_keywords:
            if kw in text:
                score += 1.0

        return min(10.0, score)

    def _calculate_relevance(self, material_class, method_class):
        """计算相关性评分"""
        score = 5.0

        # 固态电解质相关
        if material_class in ['oxide', 'sulfide', 'polymer', 'composite']:
            score += 3.0

        # 实验方法相关
        if 'synthesis' in method_class or 'testing' in method_class:
            score += 2.0

        return min(10.0, score)

    def _generate_tags(self, importance, relevance):
        """生成标签"""
        tags = []
        if importance >= 8.0:
            tags.append('high-importance')
        if relevance >= 8.0:
            tags.append('high-relevance')
        if importance >= 7.0 and relevance >= 7.0:
            tags.append('must-read')
        return tags

    def run(self):
        """运行分类"""
        print("=" * 60)
        print("Paper Classification (Level 2)")
        print("=" * 60)

        # 读取论文
        print(f"\n[1/3] Loading papers...")
        with open(self.input_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        print(f"  Loaded {len(papers)} papers")

        # 分类
        print(f"\n[2/3] Classifying papers...")
        classified_papers = []
        for paper in papers:
            classified = self.classify_paper(paper)
            classified_papers.append(classified)
        print(f"  Classified {len(classified_papers)} papers")

        # 保存
        print(f"\n[3/3] Saving classified papers...")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 按材料体系分类保存
        by_material = {}
        for paper in classified_papers:
            material = paper['classification']['material_system']
            if material not in by_material:
                by_material[material] = []
            by_material[material].append(paper)

        for material, papers in by_material.items():
            output_file = self.output_dir / f"by_material/{material}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(papers, f, indent=2, ensure_ascii=False)
            print(f"  Saved {len(papers)} papers to {material}.json")

        # 保存总文件
        total_file = self.output_dir / "all_classified.json"
        with open(total_file, 'w', encoding='utf-8') as f:
            json.dump(classified_papers, f, indent=2, ensure_ascii=False)
        print(f"  Saved all to all_classified.json")

        print("\n" + "=" * 60)
        print("[COMPLETE]")
        print("=" * 60)

def demo():
    """演示使用"""
    classifier = PaperClassifier()
    classifier.run()

if __name__ == "__main__":
    demo()
