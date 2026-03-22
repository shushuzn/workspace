#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
头脑风暴工作流 - 统一入口
整合: 定义->发散->过滤->排序->行动
"""

import json
import sys
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class BrainstormWorkflow:
    """头脑风暴工作流"""
    
    STEPS = [
        {"id": 1, "name": "问题定义", "output": "topic"},
        {"id": 2, "name": "发散思维", "output": "ideas_raw"},
        {"id": 3, "name": "过滤筛选", "output": "ideas_filtered"},
        {"id": 4, "name": "排序规划", "output": "ideas_prioritized"},
        {"id": 5, "name": "行动计划", "output": "action_plan"},
    ]
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.output_dir = self.workspace / "flow-archive/brainstorm-current"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def get_status(self) -> Dict:
        """获取工作流状态"""
        files = {
            "topic": "brainstorm_topic.json",
            "ideas_raw": "brainstorm_ideas_raw.json",
            "ideas_filtered": "brainstorm_ideas_filtered.json",
            "ideas_prioritized": "brainstorm_ideas_prioritized.json",
            "action_plan": "brainstorm_action.json",
        }
        
        status = {"completed": [], "current_step": 1, "next_step": 1}
        
        for key, filename in files.items():
            filepath = self.output_dir / filename
            if filepath.exists():
                status["completed"].append(key)
        
        # 确定下一步
        for i, step in enumerate(self.STEPS):
            if step["output"] not in status["completed"]:
                status["next_step"] = step["id"]
                break
        
        return status
    
    def define_problem(self, topic: str) -> Dict:
        """步骤1: 定义问题"""
        result = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "keywords": self._extract_keywords(topic),
            "context": {
                "domain": self._guess_domain(topic),
                "urgency": "medium",
                "scope": "medium"
            }
        }
        
        output_file = self.output_dir / "brainstorm_topic.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        words = text.lower().split()
        keywords = [w for w in words if len(w) > 3][:10]
        return keywords
    
    def _guess_domain(self, text: str) -> str:
        """猜测领域"""
        text_lower = text.lower()
        domains = {
            "技术": ["python", "code", "api", "software", "系统", "技术"],
            "商业": ["business", "market", "产品", "用户", "增长"],
            "研究": ["research", "研究", "分析", "数据", "论文"],
            "创意": ["创意", "头脑风暴", "想法", "创新", "design"],
        }
        for domain, keywords in domains.items():
            if any(kw in text_lower for kw in keywords):
                return domain
        return "通用"
    
    def generate_ideas(self, count: int = 10, strategy: str = "template") -> Dict:
        """步骤2: 发散思维 - 生成创意"""
        topic_file = self.output_dir / "brainstorm_topic.json"
        if not topic_file.exists():
            return {"error": "请先定义问题 (step 1)"}
        
        with open(topic_file, 'r', encoding='utf-8') as f:
            topic_data = json.load(f)
        
        topic = topic_data.get("topic", "")
        keywords = topic_data.get("keywords", [])
        domain = topic_data.get("context", {}).get("domain", "通用")
        
        # 生成策略
        strategies = {
            "template": self._generate_by_template,
            "scamper": self._generate_by_scamper,
            "sixhats": self._generate_by_sixhats,
            "reverse": self._generate_by_reverse,
            "analogy": self._generate_by_analogy,
        }
        
        generator = strategies.get(strategy, strategies["template"])
        ideas = generator(topic, keywords, domain, count)
        
        result = {
            "topic": topic,
            "count": len(ideas),
            "ideas": ideas,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat()
        }
        
        output_file = self.output_dir / "brainstorm_ideas_raw.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    
    def _generate_by_template(self, topic: str, keywords: list, domain: str, count: int) -> list:
        """模板生成策略"""
        templates = [
            "使用{keyword}改进{topic}",
            "结合{keyword}和{topic}的解决方案",
            "自动化{topic}中的{keyword}流程",
            "为{topic}添加{keyword}功能",
            "通过{keyword}优化{topic}体验",
            "用{keyword}思维重构{topic}",
            "基于{keyword}的数据驱动{topic}",
            "开发{keyword}插件增强{topic}",
        ]
        
        ideas = []
        for i in range(count):
            template = random.choice(templates)
            kw = random.choice(keywords) if keywords else "新"
            idea = template.format(keyword=kw, topic=topic[:20])
            ideas.append(self._create_idea(i+1, idea))
        return ideas
    
    def _generate_by_scamper(self, topic: str, keywords: list, domain: str, count: int) -> list:
        """SCAMPER策略"""
        scamper_templates = {
            "S": ["简化{topic}：移除不必要的部分", "精简{topic}的流程"],
            "C": ["结合{topic}和{keyword}", "组合{topic}与现有系统"],
            "A": ["适配{keyword}到{topic}", "调整{topic}以适应新场景"],
            "M": ["修改{topic}的关键特性", "改变{topic}的工作方式"],
            "P": ["替代{topic}中的{keyword}", "用更优方案替换现有组件"],
            "E": ["消除{topic}的瓶颈", "移除{topic}中的冗余"],
            "R": ["反向思考{topic}：从结果倒推", "反转{topic}的流程顺序"],
        }
        
        ideas = []
        for i in range(count):
            letter = random.choice(list(scamper_templates.keys()))
            templates = scamper_templates[letter]
            template = random.choice(templates)
            kw = random.choice(keywords) if keywords else "新"
            idea = template.format(keyword=kw, topic=topic[:20])
            ideas.append(self._create_idea(i+1, idea, f"SCAMPER-{letter}"))
        return ideas
    
    def _generate_by_sixhats(self, topic: str, keywords: list, domain: str, count: int) -> list:
        """六顶思考帽策略"""
        hats = {
            "白": ("客观事实", "根据数据分析{topic}的现状"),
            "红": ("情感直觉", "直觉上对{topic}的感受如何？"),
            "黑": ("批判思维", "分析{topic}的潜在风险和缺点"),
            "黄": ("乐观思维", "探索{topic}的价值和收益"),
            "绿": ("创意思维", "为{topic}想出全新的解决方案"),
            "蓝": ("控制思维", "如何系统地推进{topic}？"),
        }
        
        ideas = []
        for i, (hat, (desc, template)) in enumerate(hats.items()):
            if i >= count:
                break
            idea_text = template.format(topic=topic[:20], keyword=random.choice(keywords) if keywords else "新")
            ideas.append(self._create_idea(i+1, f"[{hat}帽] {idea_text}", desc))
        return ideas
    
    def _generate_by_reverse(self, topic: str, keywords: list, domain: str, count: int) -> list:
        """逆向思维策略"""
        reverses = [
            "如果不解决{topic}会怎样？",
            "{topic}的反面是什么？",
            "{topic}最糟糕的情况是什么？",
            "如何让{topic}完全失败？",
            "打破{topic}常规的方法？",
        ]
        
        ideas = []
        for i in range(count):
            template = random.choice(reverses)
            idea = template.format(topic=topic[:20], keyword=random.choice(keywords) if keywords else "新")
            ideas.append(self._create_idea(i+1, idea, "逆向思维"))
        return ideas
    
    def _generate_by_analogy(self, topic: str, keywords: list, domain: str, count: int) -> list:
        """类比思维策略"""
        analogies = [
            "像{keyword}一样处理{topic}",
            "借鉴{keyword}的成功经验到{topic}",
            "{keyword}和{topic}的共同点是什么？",
            "把{topic}比作{keyword}",
        ]
        
        analogies.extend([
            "自然界中什么像{topic}？",
            "其他行业如何解决类似问题？",
            "历史上的案例如何借鉴？",
        ])
        
        ideas = []
        for i in range(count):
            template = random.choice(analogies)
            kw = random.choice(keywords) if keywords else "新"
            idea = template.format(topic=topic[:20], keyword=kw)
            ideas.append(self._create_idea(i+1, idea, "类比思维"))
        return ideas
    
    def _create_idea(self, id: int, title: str, technique: str = "模板") -> dict:
        """创建创意对象"""
        return {
            "id": id,
            "title": title,
            "technique": technique,
            "score": random.randint(5, 9),
            "feasibility": random.randint(4, 8),
            "impact": random.randint(5, 9),
        }
    
    def filter_ideas(self, keep_count: int = 5) -> Dict:
        """步骤3: 过滤筛选"""
        ideas_file = self.output_dir / "brainstorm_ideas_raw.json"
        if not ideas_file.exists():
            return {"error": "请先生成创意 (step 2)"}
        
        with open(ideas_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # 按评分排序
        ideas = raw_data.get("ideas", [])
        ideas.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # 取前N个
        filtered = ideas[:keep_count]
        
        result = {
            "original_count": len(ideas),
            "kept_count": len(filtered),
            "ideas": filtered,
            "timestamp": datetime.now().isoformat()
        }
        
        output_file = self.output_dir / "brainstorm_ideas_filtered.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    
    def prioritize_ideas(self) -> Dict:
        """步骤4: 排序规划"""
        filtered_file = self.output_dir / "brainstorm_ideas_filtered.json"
        if not filtered_file.exists():
            return {"error": "请先过滤创意 (step 3)"}
        
        with open(filtered_file, 'r', encoding='utf-8') as f:
            filtered_data = json.load(f)
        
        ideas = filtered_data.get("ideas", [])
        
        # 计算综合评分
        for idea in ideas:
            idea["total_score"] = (
                idea.get("score", 5) * 0.4 +
                idea.get("feasibility", 5) * 0.3 +
                idea.get("impact", 5) * 0.3
            )
        
        ideas.sort(key=lambda x: x.get("total_score", 0), reverse=True)
        
        # 添加优先级
        for i, idea in enumerate(ideas):
            idea["priority"] = i + 1
        
        result = {
            "count": len(ideas),
            "ideas": ideas,
            "timestamp": datetime.now().isoformat()
        }
        
        output_file = self.output_dir / "brainstorm_ideas_prioritized.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    
    def generate_action_plan(self) -> Dict:
        """步骤5: 行动计划"""
        prioritized_file = self.output_dir / "brainstorm_ideas_prioritized.json"
        if not prioritized_file.exists():
            return {"error": "请先排序创意 (step 4)"}
        
        with open(prioritized_file, 'r', encoding='utf-8') as f:
            prioritized_data = json.load(f)
        
        ideas = prioritized_data.get("ideas", [])
        
        actions = []
        for idea in ideas:
            actions.append({
                "priority": idea.get("priority", 0),
                "title": idea.get("title", ""),
                "score": round(idea.get("total_score", 0), 1),
                "status": "pending",
                "next_action": f"开始实施: {idea.get('title', '')[:30]}..."
            })
        
        result = {
            "total_ideas": len(actions),
            "actions": actions,
            "timestamp": datetime.now().isoformat()
        }
        
        output_file = self.output_dir / "brainstorm_action.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
    
    def export_to_markdown(self) -> str:
        """导出为Markdown格式"""
        action_file = self.output_dir / "brainstorm_action.json"
        if not action_file.exists():
            return "# 行动计划\n\n请先完成头脑风暴流程。"
        
        with open(action_file, 'r', encoding='utf-8') as f:
            action_data = json.load(f)
        
        md = ["# 头脑风暴行动计划\n"]
        md.append(f"生成时间: {action_data.get('timestamp', '')}\n")
        md.append("---\n")
        
        for action in action_data.get('actions', []):
            md.append(f"## P{action['priority']}. {action['title']}\n")
            md.append(f"- **评分**: {action['score']}")
            md.append(f"- **状态**: {action['status']}")
            md.append(f"- **下一步**: {action['next_action']}\n")
        
        return "\n".join(md)
    
    def export_to_markdown_file(self) -> Dict:
        """导出到文件"""
        md = self.export_to_markdown()
        output_file = self.output_dir / "brainstorm_action.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md)
        return {"status": "success", "file": str(output_file)}
    
    def run_full(self, topic: str, ideas_count: int = 10, keep_count: int = 5) -> Dict:
        """运行完整工作流"""
        print(f"\n{'='*50}")
        print(f"头脑风暴工作流: {topic}")
        print(f"{'='*50}")
        
        results = {}
        
        # Step 1: 定义
        print("\n[1/5] 定义问题...")
        results["define"] = self.define_problem(topic)
        print(f"  主题: {topic}")
        print(f"  关键词: {results['define'].get('keywords', [])[:5]}")
        
        # Step 2: 发散
        print(f"\n[2/5] 发散思维 (生成{ideas_count}个创意)...")
        results["diverge"] = self.generate_ideas(ideas_count)
        print(f"  生成创意: {results['diverge'].get('count', 0)}个")
        
        # Step 3: 过滤
        print(f"\n[3/5] 过滤筛选 (保留{keep_count}个)...")
        results["filter"] = self.filter_ideas(keep_count)
        print(f"  保留创意: {results['filter'].get('kept_count', 0)}个")
        
        # Step 4: 排序
        print("\n[4/5] 排序规划...")
        results["prioritize"] = self.prioritize_ideas()
        print(f"  排序完成")
        
        # Step 5: 行动
        print("\n[5/5] 行动计划...")
        results["action"] = self.generate_action_plan()
        print(f"  行动项: {results['action'].get('total_ideas', 0)}个")
        
        print(f"\n{'='*50}")
        print("完成! 结果保存在 flow-archive/brainstorm-current/")
        print(f"{'='*50}")
        
        return results


def main():
    """主入口"""
    workflow = BrainstormWorkflow()
    
    if len(sys.argv) < 2:
        # 默认显示状态
        status = workflow.get_status()
        print("\n头脑风暴工作流状态:")
        print(f"  已完成: {len(status['completed'])}/5")
        print(f"  下一步: Step {status['next_step']}")
        print("\n用法:")
        print("  py brainstorm_workflow.py --status          # 查看状态")
        print("  py brainstorm_workflow.py --run <topic>    # 运行完整流程")
        print("  py brainstorm_workflow.py --step <n>       # 运行指定步骤")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "--status":
        status = workflow.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif cmd == "--run":
        if len(sys.argv) < 3:
            print("请提供主题: py brainstorm_workflow.py --run <主题>")
            return
        topic = " ".join(sys.argv[2:])
        workflow.run_full(topic)
    
    elif cmd == "--step":
        if len(sys.argv) < 3:
            print("请提供步骤号: py brainstorm_workflow.py --step <1-5>")
            return
        step = int(sys.argv[2])
        
        if step == 1:
            topic = input("请输入主题: ") if sys.argv[3:] else "默认主题"
            if not sys.argv[3:]:
                topic = "改进工作流效率"
            result = workflow.define_problem(topic)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif step == 2:
            result = workflow.generate_ideas(10)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif step == 3:
            result = workflow.filter_ideas(5)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif step == 4:
            result = workflow.prioritize_ideas()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif step == 5:
            result = workflow.generate_action_plan()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("步骤号错误: 1-5")
    
    else:
        print(f"未知命令: {cmd}")
        print("用法: py brainstorm_workflow.py [--status|--run|--step]")


if __name__ == "__main__":
    main()
