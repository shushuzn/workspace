#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
跨会话记忆管理器 - 持久化记忆跨越多个会话
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class CrossSessionMemory:
    """跨会话记忆管理器"""
    
    def __init__(self):
        self.memory_file = Path("13-memory/cross_session_memory.json")
        self.short_term_file = Path("13-memory/session_temp.json")
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 记忆结构
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """加载长期记忆"""
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "facts": [],          # 事实性记忆
            "skills": [],         # 技能记忆
            "preferences": [],    # 用户偏好
            "projects": [],       # 项目记忆
            "lessons": [],        # 经验教训
            "goals": [],          # 目标记忆
            "metadata": {
                "total_memories": 0,
                "last_session": None
            }
        }
    
    def add_memory(self, category: str, content: str, metadata: Dict = None) -> Dict:
        """添加记忆
        
        Args:
            category: 记忆类别 (facts/skills/preferences/projects/lessons/goals)
            content: 记忆内容
            metadata: 附加元数据
        """
        if category not in self.memory:
            return {"error": f"Invalid category: {category}"}
        
        memory_entry = {
            "id": f"{category}_{len(self.memory[category]) + 1}",
            "content": content,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "access_count": 0,
            "importance": metadata.get("importance", 5),  # 1-10
            "tags": metadata.get("tags", []),
            "session_id": metadata.get("session_id", None)
        }
        
        self.memory[category].append(memory_entry)
        self.memory["last_updated"] = datetime.now().isoformat()
        self.memory["metadata"]["total_memories"] += 1
        
        # 保存
        self._save_memory()
        
        return {"status": "success", "memory_id": memory_entry["id"]}
    
    def get_memories(self, category: str = None, tags: List[str] = None, limit: int = 10) -> List[Dict]:
        """获取记忆
        
        Args:
            category: 记忆类别 (可选)
            tags: 标签过滤 (可选)
            limit: 返回数量限制
        """
        results = []
        
        categories = [category] if category else ["facts", "skills", "preferences", "projects", "lessons", "goals"]
        
        for cat in categories:
            if cat not in self.memory:
                continue
            
            for memory in self.memory[cat]:
                # 标签过滤
                if tags and not any(tag in memory.get("tags", []) for tag in tags):
                    continue
                
                # 更新访问记录
                memory["last_accessed"] = datetime.now().isoformat()
                memory["access_count"] += 1
                
                results.append({
                    "category": cat,
                    **memory
                })
        
        # 按重要性排序
        results.sort(key=lambda x: x.get("importance", 5), reverse=True)
        
        return results[:limit]
    
    def search_memories(self, query: str) -> List[Dict]:
        """搜索记忆"""
        results = []
        query_lower = query.lower()
        
        for category in ["facts", "skills", "preferences", "projects", "lessons", "goals"]:
            for memory in self.memory.get(category, []):
                content = memory.get("content", "").lower()
                tags = " ".join(memory.get("tags", [])).lower()
                
                if query_lower in content or query_lower in tags:
                    memory["last_accessed"] = datetime.now().isoformat()
                    memory["access_count"] += 1
                    
                    results.append({
                        "category": category,
                        **memory
                    })
        
        return results
    
    def transfer_from_short_term(self) -> Dict:
        """从短期记忆转移到长期记忆"""
        if not self.short_term_file.exists():
            return {"status": "skipped", "reason": "No short-term memory"}
        
        with open(self.short_term_file, 'r', encoding='utf-8') as f:
            short_term = json.load(f)
        
        transferred = {
            "facts": 0,
            "lessons": 0,
            "skills": 0
        }
        
        # 转移决策
        if "decisions" in short_term:
            for decision in short_term["decisions"]:
                self.add_memory("facts", decision, {"importance": 7, "tags": ["decision"]})
                transferred["facts"] += 1
        
        # 转移经验教训
        if "lessons" in short_term:
            for lesson in short_term["lessons"]:
                self.add_memory("lessons", lesson, {"importance": 8, "tags": ["lesson"]})
                transferred["lessons"] += 1
        
        # 转移工具创建
        if "tools" in short_term:
            for tool in short_term["tools"]:
                self.add_memory("skills", f"Created tool: {tool}", {"importance": 6, "tags": ["tool"]})
                transferred["skills"] += 1
        
        self._save_memory()
        
        return {"status": "success", "transferred": transferred}
    
    def get_summary(self) -> Dict:
        """获取记忆摘要"""
        return {
            "total_memories": self.memory["metadata"]["total_memories"],
            "by_category": {
                "facts": len(self.memory["facts"]),
                "skills": len(self.memory["skills"]),
                "preferences": len(self.memory["preferences"]),
                "projects": len(self.memory["projects"]),
                "lessons": len(self.memory["lessons"]),
                "goals": len(self.memory["goals"])
            },
            "last_updated": self.memory["last_updated"],
            "last_session": self.memory["metadata"].get("last_session")
        }
    
    def _save_memory(self):
        """保存记忆"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def display_status(self) -> str:
        """显示状态"""
        summary = self.get_summary()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 25 + "Cross-Session Memory")
        output.append("=" * 70)
        
        output.append(f"\n[Overview]")
        output.append(f"  Total Memories:     {summary['total_memories']}")
        output.append(f"  Last Updated:       {summary['last_updated']}")
        
        output.append(f"\n[By Category]")
        for category, count in summary['by_category'].items():
            output.append(f"  {category:15} {count}")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)

def main():
    """测试入口"""
    memory = CrossSessionMemory()
    
    print("Cross-Session Memory Test")
    print("=" * 70)
    
    # 显示状态
    print(memory.display_status())
    
    # 测试：添加记忆
    print("\n[Adding Memories]")
    result1 = memory.add_memory("facts", "AI Agent has 28 tools", {"importance": 7, "tags": ["tools", "stats"]})
    print(f"  Fact: {result1}")
    
    result2 = memory.add_memory("lessons", "Always compress session before git commit", {"importance": 8, "tags": ["workflow"]})
    print(f"  Lesson: {result2}")
    
    result3 = memory.add_memory("goals", "Achieve AAI-5 autonomy by end of 2026", {"importance": 9, "tags": ["goal", "autonomy"]})
    print(f"  Goal: {result3}")
    
    # 测试：获取记忆
    print("\n[Retrieving Memories]")
    memories = memory.get_memories(limit=5)
    for mem in memories:
        print(f"  [{mem['category']}] {mem['content']} (importance: {mem['importance']})")
    
    # 测试：搜索
    print("\n[Searching for 'tools']")
    results = memory.search_memories("tools")
    print(f"  Found {len(results)} results")
    
    # 更新状态
    summary = memory.get_summary()
    print(f"\n[Summary]")
    print(f"  Total: {summary['total_memories']} memories")
    
    print(f"\n[OK] Cross-session memory test completed")

if __name__ == "__main__":
    main()
