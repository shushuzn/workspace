#!/usr/bin/env python3
"""
学习者子代理 - 多子代理协同系统

角色：从经验学习、更新记忆
模型：qwen3.5-plus
权重：1.0
"""

import sys
import json
from datetime import datetime

class LearnerAgent:
    """学习者子代理"""
    
    def __init__(self):
        self.name = "学习者"
        self.role = "从经验学习、更新记忆"
        self.model = "qwen3.5-plus"
        self.weight = 1.0
        self.agent_id = f"learner-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def process(self, outputs: list, context: dict) -> dict:
        """
        从所有子代理输出中学习
        
        Args:
            outputs: 所有子代理输出
            context: 上下文信息
            
        Returns:
            学习结果
        """
        # 提取经验
        lessons = self._extract_lessons(outputs)
        
        # 生成记忆
        memories = self._generate_memories(lessons)
        
        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "role": self.role,
            "timestamp": datetime.now().isoformat(),
            "lessons_learned": lessons,
            "memories_created": memories,
            "recommendation": self._generate_recommendation(lessons),
            "confidence": 0.9
        }
        return result
    
    def _extract_lessons(self, outputs: list) -> list:
        """提取经验教训"""
        lessons = []
        
        for output in outputs:
            agent_name = output.get("agent_name", "unknown")
            
            # 从批判者提取
            if agent_name == "批判者":
                if output.get("score", 100) < 85:
                    lessons.append({
                        "type": "quality_issue",
                        "description": f"质量未达标：{output.get('score', 0)}分",
                        "issues": output.get("issues", [])
                    })
            
            # 从协调者提取
            if agent_name == "协调者":
                if output.get("health_check", {}).get("status") != "good":
                    lessons.append({
                        "type": "health_warning",
                        "description": output.get("health_check", {})
                    })
        
        return lessons
    
    def _generate_memories(self, lessons: list) -> list:
        """生成记忆"""
        memories = []
        for lesson in lessons:
            memory = {
                "id": f"mem-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": lesson["type"],
                "content": lesson["description"],
                "timestamp": datetime.now().isoformat()
            }
            memories.append(memory)
        return memories
    
    def _generate_recommendation(self, lessons: list) -> str:
        """生成改进建议"""
        if not lessons:
            return "无改进建议，表现良好"
        
        quality_issues = [l for l in lessons if l["type"] == "quality_issue"]
        health_issues = [l for l in lessons if l["type"] == "health_warning"]
        
        recommendations = []
        if quality_issues:
            recommendations.append("提高输出质量")
        if health_issues:
            recommendations.append("注意休息，避免过劳")
        
        return "；".join(recommendations) if recommendations else "继续保持"


def main():
    """主函数"""
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = json.loads(sys.stdin.read().strip())
    
    agent = LearnerAgent()
    result = agent.process(
        input_data.get("outputs", []),
        input_data.get("context", {})
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
