#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Divergent Tool - 头脑风暴发散工具
特色：不评判、重数量、跨领域、快速联想

双环模式：发散环 (D1-D5)
时间盒：30 分钟
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path

# 真实 arXiv API 集成
try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError:
    ARXIV_AVAILABLE = False
    print("Warning: arxiv library not installed, using fallback mode")


class DivergentBrainstorm:
    """头脑风暴发散工具 - 快速生成大量想法"""
    
    def __init__(self, topic, time_limit=30):
        self.topic = topic
        self.time_limit = time_limit  # 分钟
        self.ideas = []
        self.keywords = []
        self.start_time = datetime.now()
    
    def step_d1_trigger_inspiration(self, sources=['arxiv', 'github', 'news']):
        """
        Step D1: 灵感触发 (5 分钟)
        快速扫描信息源，记录关键词/概念/趋势
        """
        print(f"\n{'='*60}")
        print(f"Step D1: 灵感触发 (5 分钟)")
        print(f"{'='*60}")
        
        keywords = []
        
        # 真实 arXiv API 获取
        if ARXIV_AVAILABLE and 'arxiv' in sources:
            print(f"\n[arXiv] 搜索真实论文...")
            try:
                client = arxiv.Client()
                search = arxiv.Search(
                    query=self.topic,
                    max_results=5,
                    sort_by=arxiv.SortCriterion.SubmittedDate
                )
                
                for result in client.results(search):
                    # 提取关键词
                    title_keywords = result.title.lower().split()
                    abstract_keywords = result.summary.lower().split()
                    
                    # 过滤常见词
                    stop_words = {'the', 'a', 'an', 'and', 'or', 'of', 'in', 'to', 'for', 'is', 'are'}
                    keywords.extend([w for w in title_keywords + abstract_keywords 
                                    if len(w) > 3 and w not in stop_words])
                    
                    print(f"  [OK] {result.entry_id.split('/')[-1]}: {result.title[:60]}...")
                    
            except Exception as e:
                print(f"  [WARN] arXiv API error: {e}")
        
        # 去重并保存
        self.keywords = list(set(keywords))[:50]
        print(f"\n收集关键词：{len(self.keywords)} 个")
        
        return self.keywords
    
    def step_d2_free_association(self, depth=5):
        """
        Step D2: 联想爆发 (10 分钟)
        自由联想：A→B→C→... 链式联想
        """
        print(f"\n{'='*60}")
        print(f"Step D2: 联想爆发 (10 分钟)")
        print(f"{'='*60}")
        
        if not self.keywords:
            print("⚠ 无关键词，先执行 D1")
            return []
        
        ideas = []
        
        # 从每个关键词出发进行联想
        for keyword in self.keywords[:10]:  # 限制前 10 个关键词
            chain = [keyword]
            current = keyword
            
            # 链式联想 (depth 层)
            for i in range(depth):
                # 简单联想：添加相关后缀/前缀
                suffixes = ['系统', '框架', '优化', '增强', '自动化', '智能', '分析', '平台']
                prefixes = ['自适应', '分布式', '实时', '多模态', '端到端', '基于']
                
                if random.random() > 0.5:
                    next_concept = f"{random.choice(prefixes)}{current}"
                else:
                    next_concept = f"{current}{random.choice(suffixes)}"
                
                chain.append(next_concept)
                current = next_concept
            
            # 生成想法
            idea = f"{keyword} → {' → '.join(chain[1:])}"
            ideas.append({
                'idea': idea,
                'origin': keyword,
                'chain_length': len(chain),
                'type': 'association'
            })
        
        self.ideas.extend(ideas)
        print(f"生成联想想法：{len(ideas)} 个")
        
        return ideas
    
    def step_d3_forced_connection(self, num_connections=10):
        """
        Step D3: 强制连接 (5 分钟)
        随机组合不相关概念，突破常规思维
        """
        print(f"\n{'='*60}")
        print(f"Step D3: 强制连接 (5 分钟)")
        print(f"{'='*60}")
        
        if len(self.keywords) < 2:
            print("⚠ 关键词不足，无法进行强制连接")
            return []
        
        ideas = []
        
        for i in range(num_connections):
            # 随机选择两个不相关关键词
            k1, k2 = random.sample(self.keywords, 2)
            
            # 生成连接想法
            connection_templates = [
                f"如果{k1}遇到{k2}会怎样？",
                f"基于{k1}的{k2}系统",
                f"{k1}驱动的{k2}方法",
                f"{k1}与{k2}的融合框架",
                f"用{k2}优化{k1}"
            ]
            
            idea_text = random.choice(connection_templates)
            ideas.append({
                'idea': idea_text,
                'concepts': [k1, k2],
                'type': 'forced_connection'
            })
        
        self.ideas.extend(ideas)
        print(f"生成强制连接想法：{len(ideas)} 个")
        
        return ideas
    
    def step_d4_reverse_thinking(self, num_reversals=10):
        """
        Step D4: 逆向思考 (5 分钟)
        反向假设，挑战默认前提
        """
        print(f"\n{'='*60}")
        print(f"Step D4: 逆向思考 (5 分钟)")
        print(f"{'='*60}")
        
        ideas = []
        
        # 常见前提假设
        assumptions = [
            "需要大量数据",
            "需要人工干预",
            "需要复杂模型",
            "需要长时间训练",
            "需要专业设备",
            "需要专家知识",
            "需要高计算资源",
            "需要完整流程"
        ]
        
        for assumption in assumptions[:num_reversals]:
            # 逆向思考
            reversed_idea = f"如果不{assumption}会怎样？"
            ideas.append({
                'idea': reversed_idea,
                'challenged_assumption': assumption,
                'type': 'reverse_thinking'
            })
        
        self.ideas.extend(ideas)
        print(f"生成逆向思考想法：{len(ideas)} 个")
        
        return ideas
    
    def step_d5_quick_capture(self, output_file=None):
        """
        Step D5: 快速记录 (5 分钟)
        结构化记录所有想法，生成想法池 JSON
        """
        print(f"\n{'='*60}")
        print(f"Step D5: 快速记录 (5 分钟)")
        print(f"{'='*60}")
        
        # 生成想法池
        idea_pool = {
            "topic": self.topic,
            "generated_at": datetime.now().isoformat(),
            "time_limit_minutes": self.time_limit,
            "total_ideas": len(self.ideas),
            "keywords": self.keywords,
            "ideas_by_type": {
                "association": [i for i in self.ideas if i.get('type') == 'association'],
                "forced_connection": [i for i in self.ideas if i.get('type') == 'forced_connection'],
                "reverse_thinking": [i for i in self.ideas if i.get('type') == 'reverse_thinking']
            },
            "statistics": {
                "association_count": len([i for i in self.ideas if i.get('type') == 'association']),
                "forced_connection_count": len([i for i in self.ideas if i.get('type') == 'forced_connection']),
                "reverse_thinking_count": len([i for i in self.ideas if i.get('type') == 'reverse_thinking'])
            }
        }
        
        # 保存文件
        if output_file is None:
            output_dir = Path("flow-archive/20260318-universal-workflow-001")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"divergent-brainstorm-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(idea_pool, f, indent=2, ensure_ascii=False)
        
        print(f"想法池已保存：{output_file}")
        print(f"总想法数：{len(self.ideas)} 个")
        
        return idea_pool
    
    def run(self, output_file=None):
        """运行完整发散流程"""
        print(f"\n{'#'*60}")
        print(f"# 头脑风暴发散环 - {self.topic}")
        print(f"# 时间限制：{self.time_limit} 分钟")
        print(f"{'#'*60}")
        
        start = time.time()
        
        # 执行 5 个步骤
        self.step_d1_trigger_inspiration()
        self.step_d2_free_association()
        self.step_d3_forced_connection()
        self.step_d4_reverse_thinking()
        result = self.step_d5_quick_capture(output_file)
        
        elapsed = time.time() - start
        print(f"\n发散环完成，用时：{elapsed:.1f} 秒")
        
        return result


def main():
    """主函数"""
    import sys
    
    topic = sys.argv[1] if len(sys.argv) > 1 else "AI agent autonomy"
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    brainstorm = DivergentBrainstorm(topic)
    result = brainstorm.run(output_file)
    
    print(f"\n发散环完成:")
    print(f"  总想法数：{result['total_ideas']}")
    print(f"  关键词数：{len(result['keywords'])}")


if __name__ == "__main__":
    main()
