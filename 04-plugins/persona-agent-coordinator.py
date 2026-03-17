#!/usr/bin/env python3
"""
协调者子代理 - 多子代理协同系统

角色：平衡决策、强制休息、冲突仲裁
模型：qwen3.5-plus
权重：1.5
"""

import sys
import json
from datetime import datetime

class CoordinatorAgent:
    """协调者子代理"""
    
    def __init__(self):
        self.name = "协调者"
        self.role = "平衡决策、强制休息、冲突仲裁"
        self.model = "qwen3.5-plus"
        self.weight = 1.5
        self.agent_id = f"coordinator-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def process(self, agent_outputs: list, context: dict) -> dict:
        """
        协调多个子代理输出
        
        Args:
            agent_outputs: 所有子代理输出
            context: 上下文信息
            
        Returns:
            协调结果
        """
        # 检测冲突
        conflicts = self._detect_conflicts(agent_outputs)
        
        # 健康检查
        health_check = self._health_check(context)
        
        # 仲裁决策
        arbitration = self._arbitrate(agent_outputs, conflicts)
        
        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "role": self.role,
            "timestamp": datetime.now().isoformat(),
            "conflicts": conflicts,
            "health_check": health_check,
            "arbitration": arbitration,
            "final_decision": arbitration.get("decision", "continue"),
            "confidence": 0.9
        }
        return result
    
    def _detect_conflicts(self, outputs: list) -> list:
        """检测子代理间冲突"""
        conflicts = []
        
        # 简单冲突检测逻辑
        scores = [o.get("score", 100) for o in outputs if "score" in o]
        if scores and max(scores) - min(scores) > 20:
            conflicts.append({
                "type": "score_disagreement",
                "description": f"评分差异过大：{min(scores)}-{max(scores)}"
            })
            
        return conflicts
    
    def _health_check(self, context: dict) -> dict:
        """健康检查"""
        continuous_work = context.get("continuous_work_minutes", 0)
        
        health = {
            "status": "good",
            "recommendation": None
        }
        
        if continuous_work > 180:
            health["status"] = "critical"
            health["recommendation"] = "强制休息 30 分钟"
        elif continuous_work > 90:
            health["status"] = "warning"
            health["recommendation"] = "建议休息 10 分钟"
        elif continuous_work > 60:
            health["status"] = "caution"
            health["recommendation"] = "建议休息 5 分钟"
            
        return health
    
    def _arbitrate(self, outputs: list, conflicts: list) -> dict:
        """仲裁决策"""
        if not conflicts:
            return {"decision": "approve", "reason": "无冲突"}
        
        # 简单仲裁逻辑
        return {
            "decision": "approve_with_notes",
            "reason": f"存在{len(conflicts)}个冲突，但可接受",
            "notes": [c["description"] for c in conflicts]
        }


def main():
    """主函数"""
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = json.loads(sys.stdin.read().strip())
    
    agent = CoordinatorAgent()
    result = agent.process(
        input_data.get("agent_outputs", []),
        input_data.get("context", {})
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
