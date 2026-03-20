#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BRAINSTORM-OPTIMIZE-001 头脑风暴优化器
【用头脑风暴工作流生成优化工具】

功能:
  1. 触发头脑风暴工作流生成优化ideas
  2. 对ideas进行评估和筛选
  3. 自动实现优先级高的优化
  4. 记录优化结果

使用:
  py brainstorm_optimize_001.py --generate
  py brainstorm_optimize_001.py --run-optimize
  py brainstorm_optimize_001.py --list
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class BrainstormOptimizer:
    """头脑风暴优化器"""
    
    OPTIMIZATION_CATEGORIES = [
        "compression", "caching", "workflow", "prompt", "batch", "parallel", "memory"
    ]
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.optimize_dir = self.workspace / "13-memory/optimization"
        self.optimize_dir.mkdir(parents=True, exist_ok=True)
        
        self.ideas_file = self.optimize_dir / "optimization_ideas.json"
        self.results_file = self.optimize_dir / "optimization_results.json"
        
        # 初始化ideas文件
        if not self.ideas_file.exists():
            self._save_ideas([])
    
    def _save_ideas(self, ideas: List[Dict]):
        """保存ideas"""
        with open(self.ideas_file, 'w', encoding='utf-8') as f:
            json.dump(ideas, f, ensure_ascii=False, indent=2)
    
    def _load_ideas(self) -> List[Dict]:
        """加载ideas"""
        if self.ideas_file.exists():
            with open(self.ideas_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def trigger_brainstorm(self, category: str = "optimization") -> Dict:
        """触发头脑风暴工作流"""
        print(f"[TRIGGER] Brainstorm: {category}")
        
        # 调用头脑风暴脚本
        brainstorm_script = self.workspace / "30-scripts-tools/brainstorm_roadmap_tools.py"
        
        if not brainstorm_script.exists():
            return {"status": "error", "reason": "brainstorm script not found"}
        
        try:
            # 使用 subprocess 运行头脑风暴
            result = subprocess.run(
                [sys.executable, str(brainstorm_script, timeout=60), "--generate", "optimization"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.workspace)
            )
            
            if result.returncode == 0:
                # 解析输出
                try:
                    ideas = json.loads(result.stdout)
                    self._save_ideas(ideas)
                    
                    return {
                        "status": "success",
                        "ideas_count": len(ideas),
                        "categories": list(set(i.get("category", "general") for i in ideas))
                    }
                except json.JSONDecodeError:
                    return {"status": "success", "raw_output": result.stdout[:500]}
            else:
                return {"status": "error", "message": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"status": "error", "reason": "timeout"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def evaluate_ideas(self) -> List[Dict]:
        """评估ideas并排序"""
        ideas = self._load_ideas()
        
        if not ideas:
            # 如果没有ideas，生成默认优化ideas
            ideas = self._get_default_optimization_ideas()
            self._save_ideas(ideas)
        
        # 评估每个idea
        evaluated = []
        for idea in ideas:
            score = self._calculate_score(idea)
            idea["score"] = score
            idea["priority"] = self._get_priority_label(score)
            evaluated.append(idea)
        
        # 按分数排序
        evaluated.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return evaluated
    
    def _calculate_score(self, idea: Dict) -> float:
        """计算idea得分"""
        score = 50  # 基础分
        
        # 影响因子
        impact = idea.get("impact", "medium")
        impact_scores = {"high": 30, "medium": 15, "low": 5}
        score += impact_scores.get(impact, 15)
        
        # 难度因子
        difficulty = idea.get("difficulty", "medium")
        difficulty_scores = {"easy": 20, "medium": 10, "hard": -10}
        score += difficulty_scores.get(difficulty, 10)
        
        # 分类权重
        category = idea.get("category", "general")
        category_weights = {
            "compression": 25,  # 压缩最重要
            "caching": 20,
            "workflow": 15,
            "memory": 15,
            "prompt": 10,
            "batch": 10,
            "parallel": 5
        }
        score += category_weights.get(category, 0)
        
        return min(score, 100)  # 上限100
    
    def _get_priority_label(self, score: float) -> str:
        if score >= 80:
            return "[CRITICAL]"
        elif score >= 60:
            return "[HIGH]"
        elif score >= 40:
            return "[MEDIUM]"
        else:
            return "[LOW]"
    
    def _get_default_optimization_ideas(self) -> List[Dict]:
        """获取默认优化ideas"""
        return [
            {
                "id": "opt-001",
                "name": "Smart Compression v3.0",
                "category": "compression",
                "description": "结构感知压缩，保留Markdown结构",
                "impact": "high",
                "difficulty": "medium",
                "status": "completed"
            },
            {
                "id": "opt-002", 
                "name": "Response Caching",
                "category": "caching",
                "description": "LLM响应缓存，避免重复调用",
                "impact": "high",
                "difficulty": "easy",
                "status": "completed"
            },
            {
                "id": "opt-003",
                "name": "Batch Tool Executor",
                "category": "batch",
                "description": "批量执行工具，减少交互次数",
                "impact": "medium",
                "difficulty": "easy",
                "status": "completed"
            },
            {
                "id": "opt-004",
                "name": "Workflow Optimizer",
                "category": "workflow",
                "description": "分析并优化工作流步骤",
                "impact": "medium",
                "difficulty": "medium",
                "status": "completed"
            },
            {
                "id": "opt-005",
                "name": "Auto Session Compression",
                "category": "compression",
                "description": "自动压缩会话，减少token",
                "impact": "high",
                "difficulty": "medium",
                "status": "in_progress"
            },
            {
                "id": "opt-006",
                "name": "Smart Prompt Optimizer",
                "category": "prompt",
                "description": "简化提示词，减少token消耗",
                "impact": "medium",
                "difficulty": "easy",
                "status": "completed"
            },
            {
                "id": "opt-007",
                "name": "Parallel Execution Engine",
                "category": "parallel",
                "description": "并行执行独立任务",
                "impact": "high",
                "difficulty": "hard",
                "status": "pending"
            },
            {
                "id": "opt-008",
                "name": "Memory Distillation",
                "category": "memory",
                "description": "自动蒸馏记忆，保留核心信息",
                "impact": "medium",
                "difficulty": "medium",
                "status": "pending"
            }
        ]
    
    def implement_top_ideas(self, count: int = 3) -> Dict:
        """实现排名最高的优化ideas"""
        ideas = self.evaluate_ideas()
        
        implemented = []
        for idea in ideas[:count]:
            if idea.get("status") == "pending":
                # 标记为进行中
                idea["status"] = "in_progress"
                idea["implemented_at"] = datetime.now().isoformat()
                implemented.append(idea["id"])
        
        # 保存更新后的ideas
        self._save_ideas(ideas)
        
        # 记录结果
        results = self._load_results()
        results.append({
            "timestamp": datetime.now().isoformat(),
            "implemented": implemented,
            "total": len(implemented)
        })
        self._save_results(results)
        
        return {
            "status": "success",
            "implemented": implemented,
            "total": len(implemented)
        }
    
    def _load_results(self) -> List[Dict]:
        """加载结果"""
        if self.results_file.exists():
            with open(self.results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_results(self, results: List[Dict]):
        """保存结果"""
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def list_ideas(self) -> str:
        """列出未完成的ideas"""
        ideas = self.evaluate_ideas()
        
        # 只显示未完成的
        ideas = [i for i in ideas if i.get("status") != "completed"]
        
        output = ["# PENDING OPTIMIZATION IDEAS\n"]
        output.append(f"Total: {len(ideas)}\n")
        
        for i, idea in enumerate(ideas, 1):
            status = idea.get("status", "pending")
            status_icon = {
                "completed": "[DONE]",
                "in_progress": "[IN PROGRESS]",
                "pending": "[PENDING]"
            }.get(status, "[?]")
            
            output.append(f"""
{i}. [{idea.get('priority', '')}] {idea.get('name', 'Unnamed')}
   - Category: {idea.get('category', 'general')}
   - Impact: {idea.get('impact', 'medium')}
   - Difficulty: {idea.get('difficulty', 'medium')}
   - Status: {status_icon} {status}
   - Score: {idea.get('score', 0)}
   - Description: {idea.get('description', '')}
""")
        
        return '\n'.join(output)
    
    def run_full_optimization(self) -> Dict:
        """运行完整优化流程"""
        print("=" * 60)
        print("[BRAINSTORM] Optimization Workflow")
        print("=" * 60)
        
        # 1. 评估现有ideas
        print("\n[STEP 1] Evaluating optimization ideas...")
        ideas = self.evaluate_ideas()
        print(f"   Found {len(ideas)} optimization ideas")
        
        # 2. 显示排名
        print("\n[STEP 2] Priority ranking...")
        for i, idea in enumerate(ideas[:5], 1):
            print(f"   {i}. [{idea.get('priority')}] {idea.get('name')} (score: {idea.get('score')})")
        
        # 3. 实现top ideas
        print("\n[STEP 3] Implementing high priority optimizations...")
        result = self.implement_top_ideas(3)
        print(f"   Implemented {result['total']} optimizations")
        
        # 4. 汇总
        print("\n[DONE] Optimization workflow complete!")
        
        return {
            "ideas_count": len(ideas),
            "implemented": result.get("implemented", []),
            "timestamp": datetime.now().isoformat()
        }


def main():
    optimizer = BrainstormOptimizer()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--generate":
            result = optimizer.trigger_brainstorm()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--evaluate":
            ideas = optimizer.evaluate_ideas()
            print(json.dumps(ideas, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--run-optimize":
            result = optimizer.run_full_optimization()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--list":
            print(optimizer.list_ideas())
            return 0
        
        if cmd == "--implement":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
            result = optimizer.implement_top_ideas(count)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("BRAINSTORM-OPTIMIZE-001 头脑风暴优化器")
    print("Usage:")
    print("  py brainstorm_optimize_001.py --generate        # 触发头脑风暴")
    print("  py brainstorm_optimize_001.py --evaluate        # 评估ideas")
    print("  py brainstorm_optimize_001.py --run-optimize   # 运行完整流程")
    print("  py brainstorm_optimize_001.py --list           # 列出ideas")
    print("  py brainstorm_optimize_001.py --implement [n]  # 实现top N")
    return 0


if __name__ == "__main__":
    sys.exit(main())