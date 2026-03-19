#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具自学习能力 - 自主学习和掌握新工具
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ToolSelfLearner:
    """工具自学习能力"""
    
    def __init__(self):
        self.tool_knowledge_file = Path("13-memory/tool_knowledge.json")
        self.learning_log_file = Path("13-memory/tool_learning_log.json")
        self.registry_file = Path("30-scripts-tools/tools_registry.json")
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """加载工具知识"""
        if self.tool_knowledge_file.exists():
            with open(self.tool_knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "known_tools": {},      # 已知工具知识
            "tool_patterns": {},    # 工具使用模式
            "learning_history": [], # 学习历史
            "stats": {
                "tools_learned": 0,
                "patterns_discovered": 0,
                "successful_uses": 0,
                "failed_uses": 0
            }
        }
    
    def learn_tool(self, tool_id: str, tool_info: Dict) -> Dict:
        """学习新工具
        
        Args:
            tool_id: 工具 ID
            tool_info: 工具信息 (从 registry 获取)
        """
        # 检查是否已学习
        if tool_id in self.knowledge["known_tools"]:
            return {"status": "skipped", "reason": "Already learned"}
        
        # 分析工具
        analysis = self._analyze_tool(tool_id, tool_info)
        
        # 存储知识
        knowledge_entry = {
            "tool_id": tool_id,
            "learned_at": datetime.now().isoformat(),
            "category": tool_info.get("category", "unknown"),
            "description": tool_info.get("description", ""),
            "file_path": tool_info.get("file_path", ""),
            "usage_patterns": [],
            "best_practices": [],
            "common_errors": [],
            "compatibility": [],  # 与其他工具的兼容性
            "last_used": None,
            "use_count": 0,
            "success_rate": 100
        }
        
        # 添加分析结果
        knowledge_entry.update(analysis)
        
        self.knowledge["known_tools"][tool_id] = knowledge_entry
        self.knowledge["stats"]["tools_learned"] += 1
        
        # 记录学习历史
        self.knowledge["learning_history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "learn_tool",
            "tool_id": tool_id,
            "result": "success"
        })
        
        self._save_knowledge()
        
        return {"status": "success", "tool_id": tool_id, "analysis": analysis}
    
    def _analyze_tool(self, tool_id: str, tool_info: Dict) -> Dict:
        """分析工具特性"""
        analysis = {
            "complexity": self._estimate_complexity(tool_info),
            "risk_level": self._estimate_risk(tool_info),
            "dependencies": self._extract_dependencies(tool_info),
            "input_requirements": [],
            "output_format": "",
            "side_effects": []
        }
        
        # 基于类别估计
        category = tool_info.get("category", "")
        
        if category in ["compression", "documentation"]:
            analysis["risk_level"] = "low"
        elif category in ["git", "workflow"]:
            analysis["risk_level"] = "medium"
        elif category in ["system", "network"]:
            analysis["risk_level"] = "high"
        
        # 基于描述提取输入要求
        description = tool_info.get("description", "").lower()
        
        if "file" in description or "path" in description:
            analysis["input_requirements"].append("file_path")
        if "text" in description or "content" in description:
            analysis["input_requirements"].append("text_content")
        if "config" in description or "settings" in description:
            analysis["input_requirements"].append("configuration")
        
        return analysis
    
    def _estimate_complexity(self, tool_info: Dict) -> str:
        """估计工具复杂度"""
        description = tool_info.get("description", "")
        
        # 简单关键词
        simple_keywords = ["get", "list", "show", "read", "check"]
        # 复杂关键词
        complex_keywords = ["create", "generate", "transform", "compile", "deploy"]
        
        desc_lower = description.lower()
        
        if any(kw in desc_lower for kw in complex_keywords):
            return "medium"
        elif any(kw in desc_lower for kw in simple_keywords):
            return "low"
        else:
            return "medium"
    
    def _estimate_risk(self, tool_info: Dict) -> str:
        """估计工具风险等级"""
        description = tool_info.get("description", "").lower()
        file_path = tool_info.get("file_path", "").lower()
        
        # 高风险操作
        high_risk = ["delete", "remove", "destroy", "format", "execute", "run"]
        # 中风险操作
        medium_risk = ["write", "save", "commit", "push", "update", "modify"]
        
        if any(kw in description for kw in high_risk):
            return "high"
        elif any(kw in description for kw in medium_risk):
            return "medium"
        else:
            return "low"
    
    def _extract_dependencies(self, tool_info: Dict) -> List[str]:
        """提取工具依赖"""
        dependencies = []
        
        file_path = tool_info.get("file_path", "")
        if file_path:
            tool_file = Path(file_path)
            if tool_file.exists():
                # 读取文件分析 import
                try:
                    with open(tool_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取 import
                    imports = re.findall(r'^import\s+(\w+)', content, re.MULTILINE)
                    from_imports = re.findall(r'^from\s+(\w+)\s+import', content, re.MULTILINE)
                    
                    dependencies = list(set(imports + from_imports))
                    # 过滤标准库
                    std_libs = ['json', 'os', 'sys', 'pathlib', 'datetime', 're', 'typing']
                    dependencies = [d for d in dependencies if d not in std_libs]
                except:
                    pass
        
        return dependencies
    
    def learn_from_usage(self, tool_id: str, success: bool, context: Dict = None) -> Dict:
        """从使用中学习
        
        Args:
            tool_id: 工具 ID
            success: 是否成功
            context: 使用上下文
        """
        if tool_id not in self.knowledge["known_tools"]:
            # 先学习工具
            self._auto_learn_unknown_tool(tool_id)
        
        # 更新使用统计
        tool = self.knowledge["known_tools"][tool_id]
        tool["last_used"] = datetime.now().isoformat()
        tool["use_count"] += 1
        
        if success:
            self.knowledge["stats"]["successful_uses"] += 1
        else:
            self.knowledge["stats"]["failed_uses"] += 1
        
        # 更新成功率
        total = tool["use_count"]
        if total > 0:
            # 简化计算
            tool["success_rate"] = max(0, 100 - (self.knowledge["stats"]["failed_uses"] * 5))
        
        # 记录使用模式
        if context:
            pattern = {
                "timestamp": datetime.now().isoformat(),
                "context": context,
                "success": success
            }
            tool["usage_patterns"].append(pattern)
        
        # 记录学习历史
        self.knowledge["learning_history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "use_tool",
            "tool_id": tool_id,
            "success": success
        })
        
        self._save_knowledge()
        
        return {"status": "success", "use_count": tool["use_count"]}
    
    def _auto_learn_unknown_tool(self, tool_id: str):
        """自动学习未知工具"""
        if not self.registry_file.exists():
            return
        
        with open(self.registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        if tool_id in registry.get("tools", {}):
            tool_info = registry["tools"][tool_id]
            self.learn_tool(tool_id, tool_info)
    
    def get_recommendation(self, task: str) -> List[Dict]:
        """根据任务推荐工具
        
        Args:
            task: 任务描述
        """
        recommendations = []
        task_lower = task.lower()
        
        for tool_id, knowledge in self.knowledge["known_tools"].items():
            # 匹配描述
            description = knowledge.get("description", "").lower()
            
            # 简单关键词匹配
            task_words = task_lower.split()
            match_count = sum(1 for word in task_words if word in description)
            
            if match_count > 0:
                recommendations.append({
                    "tool_id": tool_id,
                    "match_score": match_count,
                    "success_rate": knowledge.get("success_rate", 100),
                    "category": knowledge.get("category", "unknown")
                })
        
        # 按匹配度和成功率排序
        recommendations.sort(key=lambda x: (x["match_score"], x["success_rate"]), reverse=True)
        
        return recommendations[:5]
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.knowledge["stats"]
    
    def _save_knowledge(self):
        """保存知识"""
        with open(self.tool_knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    def display_status(self) -> str:
        """显示状态"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 25 + "Tool Self-Learner")
        output.append("=" * 70)
        
        output.append(f"\n[Statistics]")
        output.append(f"  Tools Learned:      {stats['tools_learned']}")
        output.append(f"  Patterns Discovered: {stats['patterns_discovered']}")
        output.append(f"  Successful Uses:    {stats['successful_uses']}")
        output.append(f"  Failed Uses:        {stats['failed_uses']}")
        
        if stats['successful_uses'] + stats['failed_uses'] > 0:
            total = stats['successful_uses'] + stats['failed_uses']
            success_rate = (stats['successful_uses'] / total) * 100
            output.append(f"  Overall Success:    {success_rate:.1f}%")
        
        output.append(f"\n[Known Tools]")
        for tool_id, knowledge in list(self.knowledge["known_tools"].items())[:10]:
            output.append(f"  - {tool_id} ({knowledge.get('category', 'unknown')})")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)

def main():
    """测试入口"""
    learner = ToolSelfLearner()
    
    print("Tool Self-Learner Test")
    print("=" * 70)
    
    # 显示状态
    print(learner.display_status())
    
    # 测试：从 registry 学习工具
    print("\n[Learning Tools from Registry]")
    
    registry_file = Path("30-scripts-tools/tools_registry.json")
    if registry_file.exists():
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        # 学习前 5 个工具
        tools_learned = 0
        for tool_id, tool_info in list(registry.get("tools", {}).items())[:5]:
            result = learner.learn_tool(tool_id, tool_info)
            if result["status"] == "success":
                tools_learned += 1
                print(f"  Learned: {tool_id}")
        
        print(f"  Total learned: {tools_learned}")
    
    # 测试：从使用中学习
    print("\n[Learning from Usage]")
    result = learner.learn_from_usage("task_decomposer", success=True, context={"task": "decompose project"})
    print(f"  Usage recorded: {result}")
    
    # 测试：推荐工具
    print("\n[Tool Recommendation]")
    task = "compress session memory"
    recommendations = learner.get_recommendation(task)
    print(f"  Task: {task}")
    print(f"  Recommendations: {[r['tool_id'] for r in recommendations]}")
    
    print(f"\n[OK] Tool self-learner test completed")

if __name__ == "__main__":
    main()
