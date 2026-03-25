#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feedback Loop System
反馈循环系统
"""

import json
from pathlib import Path
from datetime import datetime

class FeedbackLoop:
    """反馈循环系统"""

    def __init__(self):
        self.workflows_dir = Path(r"D:\OpenClaw\workspace\workflows")
        self.config_dir = Path(r"D:\OpenClaw\workspace\config")

    def collect_feedback(self, level: int, feedback_data: dict):
        """收集反馈"""
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'data': feedback_data
        }

        # 保存反馈
        feedback_file = self.workflows_dir / f"feedback_level_{level}.json"
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback, f, indent=2, ensure_ascii=False)

        return feedback

    def apply_feedback_level6_to_level2(self, level6_data: dict):
        """Level 6 (知识图谱) → Level 2 (分类标注) 反馈"""
        feedback = []

        # 从知识图谱发现新关键词
        if 'entities' in level6_data:
            new_keywords = []
            for entity in level6_data['entities']:
                if entity.get('type') == 'keyword':
                    new_keywords.append(entity['name'])

            if new_keywords:
                feedback.append({
                    'type': 'new_keywords',
                    'source': 'level_6',
                    'target': 'level_2',
                    'data': {'keywords': new_keywords},
                    'action': 'update_keyword_dictionary'
                })

        # 从知识图谱发现新关系
        if 'relations' in level6_data:
            new_relations = []
            for relation in level6_data['relations']:
                if relation.get('type') == 'related_to':
                    new_relations.append({
                        'source': relation['source'],
                        'target': relation['target']
                    })

            if new_relations:
                feedback.append({
                    'type': 'new_relations',
                    'source': 'level_6',
                    'target': 'level_2',
                    'data': {'relations': new_relations},
                    'action': 'update_relation_rules'
                })

        return feedback

    def apply_feedback_level5_to_level3(self, level5_data: dict):
        """Level 5 (报告生成) → Level 3 (趋势分析) 反馈"""
        feedback = []

        # 从报告发现分析偏差
        if 'analysis_bias' in level5_data:
            feedback.append({
                'type': 'analysis_bias',
                'source': 'level_5',
                'target': 'level_3',
                'data': level5_data['analysis_bias'],
                'action': 'adjust_analysis_parameters'
            })

        # 从报告发现新趋势
        if 'new_trends' in level5_data:
            feedback.append({
                'type': 'new_trends',
                'source': 'level_5',
                'target': 'level_3',
                'data': level5_data['new_trends'],
                'action': 'update_trend_detection'
            })

        return feedback

    def update_configuration(self, feedback: list):
        """根据反馈更新配置"""
        for fb in feedback:
            if fb['type'] == 'new_keywords':
                # 更新 Level 2 关键词词典
                keyword_file = self.workflows_dir / '02-paper-classification' / 'keywords.yaml'
                if keyword_file.exists():
                    with open(keyword_file, 'r', encoding='utf-8') as f:
                        keywords = yaml.safe_load(f)

                    # 添加新关键词
                    for keyword in fb['data']['keywords']:
                        if keyword not in keywords:
                            keywords.append(keyword)

                    with open(keyword_file, 'w', encoding='utf-8') as f:
                        yaml.dump(keywords, f)

            elif fb['type'] == 'analysis_bias':
                # 更新 Level 3 分析参数
                config_file = self.workflows_dir / '03-trend-analysis' / 'config.yaml'
                if config_file.exists():
                    # 调整分析参数
                    pass

        return True

    def run(self, date_str: str = None):
        """运行反馈循环"""
        from datetime import datetime
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        print("=" * 60)
        print("Feedback Loop System")
        print("=" * 60)

        # 收集 Level 6 反馈
        print(f"\n[1/4] Collecting Level 6 feedback...")
        level6_file = self.workflows_dir.parent / 'knowledge-graph' / 'research-network.json'
        if level6_file.exists():
            with open(level6_file, 'r', encoding='utf-8') as f:
                level6_data = json.load(f)

            feedback_6_to_2 = self.apply_feedback_level6_to_level2(level6_data)
            print(f"  Level 6 → Level 2: {len(feedback_6_to_2)} feedback items")
        else:
            print(f"  Level 6 data not found")
            feedback_6_to_2 = []

        # 收集 Level 5 反馈
        print(f"\n[2/4] Collecting Level 5 feedback...")
        level5_file = self.workflows_dir.parent / 'reports' / f'AUTO-RESEARCH-REPORT-{date_str}.md'
        if level5_file.exists():
            # 简单解析报告，提取反馈
            feedback_5_to_3 = []
            print(f"  Level 5 → Level 3: {len(feedback_5_to_3)} feedback items")
        else:
            print(f"  Level 5 report not found")
            feedback_5_to_3 = []

        # 应用反馈
        print(f"\n[3/4] Applying feedback...")
        all_feedback = feedback_6_to_2 + feedback_5_to_3
        if all_feedback:
            self.update_configuration(all_feedback)
            print(f"  Applied {len(all_feedback)} feedback items")
        else:
            print(f"  No feedback to apply")

        # 保存反馈记录
        print(f"\n[4/4] Saving feedback records...")
        feedback_record = {
            'date': date_str,
            'feedback_6_to_2': feedback_6_to_2,
            'feedback_5_to_3': feedback_5_to_3,
            'total': len(all_feedback)
        }

        feedback_dir = self.workflows_dir.parent / 'feedback'
        feedback_dir.mkdir(parents=True, exist_ok=True)

        feedback_file = feedback_dir / f'feedback_{date_str}.json'
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(feedback_record, f, indent=2, ensure_ascii=False)
        print(f"  Saved to: {feedback_file}")

        print("\n" + "=" * 60)
        print("[COMPLETE]")
        print("=" * 60)

def demo():
    """演示使用"""
    feedback = FeedbackLoop()
    feedback.run()

if __name__ == "__main__":
    demo()
