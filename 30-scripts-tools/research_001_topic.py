#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RESEARCH-001 Research Topic Generator
【研究主题生成器】

功能:
  - 生成研究主题 ideas
  - 分类整理
  - 优先级排序
"""
import json
import sys
from pathlib import Path
from datetime import datetime


RESEARCH_DIR = Path("60-DATA/research_001")


class ResearchTopicGenerator:
    """研究主题生成器"""
    
    def __init__(self):
        self.dir = RESEARCH_DIR
        self.dir.mkdir(parents=True, exist_ok=True)
    
    def generate_topics(self, category: str = None) -> list:
        """生成研究主题"""
        topics = [
            {"id": 1, "category": "ai", "topic": "LLM Context Optimization", "priority": "high"},
            {"id": 2, "category": "ai", "topic": "Multi-Agent Collaboration Patterns", "priority": "high"},
            {"id": 3, "category": "performance", "topic": "Tool Execution Caching Strategy", "priority": "medium"},
            {"id": 4, "category": "performance", "topic": "Workflow Parallelization", "priority": "medium"},
            {"id": 5, "category": "security", "topic": "Shell Command Safety Analysis", "priority": "high"},
            {"id": 6, "category": "automation", "topic": "Auto-Workflow Composition", "priority": "medium"},
            {"id": 7, "category": "visualization", "topic": "Real-time Progress Dashboard", "priority": "low"},
            {"id": 8, "category": "integration", "topic": "External API Standardization", "priority": "medium"},
        ]
        
        if category:
            topics = [t for t in topics if t["category"] == category]
        
        return topics
    
    def get_by_priority(self) -> dict:
        """按优先级分组"""
        topics = self.generate_topics()
        
        result = {"high": [], "medium": [], "low": []}
        for t in topics:
            result[t["priority"]].append(t)
        
        return result
    
    def save_topics(self) -> str:
        """保存主题到文件"""
        topics = self.generate_topics()
        
        file = self.dir / f"research_topics_{datetime.now().strftime('%Y%m%d')}.json"
        with open(file, "w", encoding="utf-8") as f:
            json.dump(topics, f, ensure_ascii=False, indent=2)
        
        return str(file)


def main():
    generator = ResearchTopicGenerator()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            topics = generator.generate_topics()
            print(json.dumps(topics, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--priority":
            result = generator.get_by_priority()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--save":
            file = generator.save_topics()
            print(f"Saved: {file}")
            return 0
    
    print("RESEARCH-001 Research Topic Generator")
    print("Usage:")
    print("  py research_001.py --list      # List all topics")
    print("  py research_001.py --priority  # Group by priority")
    print("  py research_001.py --save      # Save to file")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())