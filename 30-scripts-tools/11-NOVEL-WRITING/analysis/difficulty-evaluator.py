#!/usr/bin/env python3
"""
Difficulty Evaluator - 问题难度评估器
根据问题复杂度自动路由到合适的模型

功能:
1. 多维度难度评分
2. 模式匹配快速路由
3. 缓存相同/相似问题
4. 指标收集与分析

使用:
python difficulty-evaluator.py --query "你的问题"
"""

import argparse
import hashlib
import json
import re
import yaml
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime

class DifficultyEvaluator:
    def __init__(self, config_path: str = "config/difficulty-evaluator.yaml"):
        self.config = self._load_config(config_path)
        self.cache = {}
        self.metrics = []

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def _calculate_complexity(self, query: str) -> float:
        """计算问题复杂度 (0-1)"""
        # 句子数量
        sentences = len(re.split(r'[.!?。！？]', query))

        # 问题数量
        questions = query.count('?') + query.count('？')

        # 连接词数量 (表示多步推理)
        connectors = len(re.findall(r'(并且 | 或者 | 如果 | 那么 | 因为 | 所以 | 但是 | 然而)', query))

        # 长度因子
        length_factor = min(len(query) / 500, 1.0)

        # 复杂度评分
        complexity = (
            0.3 * min(sentences / 5, 1.0) +
            0.2 * min(questions / 3, 1.0) +
            0.3 * min(connectors / 5, 1.0) +
            0.2 * length_factor
        )

        return min(complexity, 1.0)

    def _calculate_domain_knowledge(self, query: str) -> float:
        """计算领域知识深度需求 (0-1)"""
        # 专业术语检测
        technical_terms = [
            '算法', '架构', '模型', '神经网络', '向量', '矩阵',
            'API', 'SDK', '微服务', '容器', 'Kubernetes',
            '量子', '相对论', '热力学', '微积分',
            '宪法', '法理', '判例', '诉讼'
        ]

        term_count = sum(1 for term in technical_terms if term in query.lower())
        return min(term_count / 5, 1.0)

    def _calculate_reasoning_depth(self, query: str) -> float:
        """计算推理深度需求 (0-1)"""
        # 推理关键词
        reasoning_patterns = [
            r'为什么.*会',
            r'如何.*影响',
            r'比较.*和.*的',
            r'分析.*原因',
            r'评估.*效果',
            r'预测.*趋势',
            r'设计.*方案',
            r'优化.*策略'
        ]

        matches = sum(1 for pattern in reasoning_patterns if re.search(pattern, query))
        return min(matches / 3, 1.0)

    def _calculate_context_length_factor(self, query: str, context_length: int = 0) -> float:
        """计算上下文长度因子 (0-1)"""
        # 基于查询长度和附加上下文
        total_length = len(query) + context_length
        return min(total_length / 10000, 1.0)

    def _pattern_match_routing(self, query: str) -> str:
        """基于模式匹配的快速路由"""
        routing_rules = self.config.get('routing_rules', {})

        # 检查简单模式
        easy_patterns = routing_rules.get('easy_patterns', [])
        for pattern in easy_patterns:
            if pattern in query:
                return 'easy'

        # 检查困难模式
        hard_patterns = routing_rules.get('hard_patterns', [])
        for pattern in hard_patterns:
            if re.search(pattern, query):
                return 'hard'

        return 'medium'

    def evaluate(self, query: str, context_length: int = 0) -> Tuple[str, Dict]:
        """
        评估问题难度并返回推荐模型
        
        Returns:
            Tuple[model_name, evaluation_details]
        """
        # 检查缓存
        cache_key = hashlib.md5(f"{query}:{context_length}".encode()).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 多维度评分
        complexity = self._calculate_complexity(query)
        domain_knowledge = self._calculate_domain_knowledge(query)
        reasoning_depth = self._calculate_reasoning_depth(query)
        context_factor = self._calculate_context_length_factor(query, context_length)

        # 权重计算
        weights = self.config.get('evaluator', {})
        w_complexity = weights.get('complexity_weight', 0.3)
        w_domain = weights.get('domain_knowledge_weight', 0.25)
        w_reasoning = weights.get('reasoning_depth_weight', 0.3)
        w_context = weights.get('context_length_weight', 0.15)

        # 综合评分
        total_score = (
            w_complexity * complexity +
            w_domain * domain_knowledge +
            w_reasoning * reasoning_depth +
            w_context * context_factor
        )

        # 模式匹配快速路由
        pattern_route = self._pattern_match_routing(query)

        # 确定难度级别
        thresholds = self.config.get('evaluator', {})
        easy_threshold = thresholds.get('easy_threshold', 0.3)
        medium_threshold = thresholds.get('medium_threshold', 0.6)

        if pattern_route == 'easy' or total_score <= easy_threshold:
            difficulty = 'easy'
            model = self.config.get('models', {}).get('easy_model', 'bailian/MiniMax-M2.5')
        elif pattern_route == 'hard' or total_score > medium_threshold:
            difficulty = 'hard'
            model = self.config.get('models', {}).get('hard_model', 'bailian/qwen3-max-2026-01-23')
        else:
            difficulty = 'medium'
            model = self.config.get('models', {}).get('medium_model', 'bailian/qwen3.5-plus')

        # 评估详情
        details = {
            'difficulty': difficulty,
            'score': total_score,
            'dimensions': {
                'complexity': complexity,
                'domain_knowledge': domain_knowledge,
                'reasoning_depth': reasoning_depth,
                'context_length': context_factor
            },
            'pattern_route': pattern_route,
            'recommended_model': model,
            'timestamp': datetime.now().isoformat()
        }

        # 缓存结果
        self.cache[cache_key] = (model, details)

        # 记录指标
        self.metrics.append(details)

        return model, details

    def get_metrics(self) -> Dict:
        """获取评估指标统计"""
        if not self.metrics:
            return {}

        total = len(self.metrics)
        easy_count = sum(1 for m in self.metrics if m['difficulty'] == 'easy')
        medium_count = sum(1 for m in self.metrics if m['difficulty'] == 'medium')
        hard_count = sum(1 for m in self.metrics if m['difficulty'] == 'hard')

        return {
            'total_evaluations': total,
            'difficulty_distribution': {
                'easy': easy_count,
                'medium': medium_count,
                'hard': hard_count
            },
            'easy_percentage': easy_count / total * 100,
            'medium_percentage': medium_count / total * 100,
            'hard_percentage': hard_count / total * 100,
            'estimated_cost_savings': f"{easy_count * 70 + medium_count * 30}%"  # 估算
        }

def main():
    parser = argparse.ArgumentParser(description='Difficulty Evaluator')
    parser.add_argument('--query', '-q', required=True, help='要评估的问题')
    parser.add_argument('--config', '-c', default='config/difficulty-evaluator.yaml', help='配置文件路径')
    parser.add_argument('--context-length', '-l', type=int, default=0, help='上下文长度')
    parser.add_argument('--metrics', '-m', action='store_true', help='显示历史指标')

    args = parser.parse_args()

    evaluator = DifficultyEvaluator(args.config)

    if args.metrics:
        metrics = evaluator.get_metrics()
        print(json.dumps(metrics, indent=2, ensure_ascii=False))
    else:
        model, details = evaluator.evaluate(args.query, args.context_length)

        print(f"📊 难度评估结果")
        print(f"{'=' *50}")
        print(f"推荐模型：{model}")
        print(f"难度级别：{details['difficulty']}")
        print(f"综合评分：{details['score']:.2f}")
        print(f"\n维度评分:")
        for dim, score in details['dimensions'].items():
            bar = '█' * int(score * 10) + '░' * (10 - int(score * 10))
            print(f"  {dim:20s}: [{bar}] {score:.2f}")
        print(f"\n模式匹配：{details['pattern_route']}")

if __name__ == '__main__':
    main()
