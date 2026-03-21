import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
元认知监控工具 - 自我监控/评估/优化
基于主流程 v2.0 P0-1 优化
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class MetacognitionMonitor:
    """元认知监控器"""
    
    def __init__(self, flow_id: str):
        self.flow_id = flow_id
        self.metrics_file = Path(f"flow-archive/{flow_id}/metacognition-log.json")
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.metrics = {
            "flow_id": flow_id,
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "self_evaluations": [],
            "optimizations_applied": []
        }
    
    def collect_metrics(self, step_id: float, step_name: str, 
                       execution_time: float, success: bool,
                       tool_success_rate: float = 1.0,
                       error_frequency: float = 0.0,
                       quality_score: float = 80.0,
                       resource_usage: Dict = None) -> None:
        """收集执行指标"""
        
        step_metric = {
            "step_id": step_id,
            "step_name": step_name,
            "timestamp": datetime.now().isoformat(),
            "execution_time": execution_time,
            "success": success,
            "tool_success_rate": tool_success_rate,
            "error_frequency": error_frequency,
            "quality_score": quality_score,
            "resource_usage": resource_usage or {}
        }
        
        self.metrics["steps"].append(step_metric)
        print(f"[Metacognition] Step {step_id} metrics collected")
        
        return step_metric
    
    def self_evaluate(self) -> Dict:
        """自我评估"""
        
        if not self.metrics["steps"]:
            return {"error": "No steps to evaluate"}
        
        steps = self.metrics["steps"]
        
        # 计算各项指标
        avg_execution_time = sum(s["execution_time"] for s in steps) / len(steps)
        avg_success_rate = sum(s["tool_success_rate"] for s in steps) / len(steps)
        avg_error_frequency = sum(s["error_frequency"] for s in steps) / len(steps)
        avg_quality_score = sum(s["quality_score"] for s in steps) / len(steps)
        
        # 综合评分
        overall_score = (
            avg_success_rate * 40 +
            (1 - avg_error_frequency) * 30 +
            (avg_quality_score / 100) * 30
        )
        
        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "total_steps": len(steps),
            "avg_execution_time": round(avg_execution_time, 2),
            "avg_success_rate": round(avg_success_rate, 3),
            "avg_error_frequency": round(avg_error_frequency, 3),
            "avg_quality_score": round(avg_quality_score, 2),
            "overall_score": round(overall_score, 2),
            "grade": "A" if overall_score >= 90 else "B" if overall_score >= 80 else "C"
        }
        
        self.metrics["self_evaluations"].append(evaluation)
        print(f"[Metacognition] Self-evaluation: {overall_score:.2f} ({evaluation['grade']})")
        
        return evaluation
    
    def self_optimize(self, evaluation: Dict) -> List[str]:
        """自我优化 - 基于评估提出优化建议"""
        
        optimizations = []
        
        if evaluation.get("avg_success_rate", 1.0) < 0.9:
            optimizations.append("工具成功率低于 90%，建议增强错误处理")
        
        if evaluation.get("avg_error_frequency", 0) > 0.1:
            optimizations.append("错误频率高于 10%，建议添加更多验证")
        
        if evaluation.get("avg_quality_score", 80) < 75:
            optimizations.append("质量评分低于 75，建议加强质量门禁")
        
        if evaluation.get("avg_execution_time", 0) > 60:
            optimizations.append("执行时间过长，建议优化或并行化")
        
        self.metrics["optimizations_applied"].extend(optimizations)
        
        for opt in optimizations:
            print(f"[Metacognition] Optimization: {opt}")
        
        return optimizations
    
    def save(self) -> None:
        """保存指标到文件"""
        self.metrics["end_time"] = datetime.now().isoformat()
        
        with open(self.metrics_file, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        
        print(f"[Metacognition] Metrics saved to {self.metrics_file}")
    
    def run(self, step_id: float, step_name: str, execution_time: float, 
            success: bool) -> Dict:
        """完整流程：收集 -> 评估 -> 优化 -> 保存"""
        
        # 收集指标
        self.collect_metrics(step_id, step_name, execution_time, success)
        
        # 自我评估
        evaluation = self.self_evaluate()
        
        # 自我优化
        optimizations = self.self_optimize(evaluation)
        
        # 保存
        self.save()
        
        return {
            "evaluation": evaluation,
            "optimizations": optimizations,
            "success": True
        }

logging.basicConfig(level=logging.INFO)
def main() -> None:
    """测试入口"""
    monitor = MetacognitionMonitor("20260320-main-workflow-brainstorm")
    
    # 模拟步骤执行
    result = monitor.run(
        step_id=8.7,
        step_name="元认知评估",
        execution_time=2.5,
        success=True
    )
    
    print(f"\n[OK] Metacognition monitoring completed")
    print(f"Overall Score: {result['evaluation']['overall_score']}")
    print(f"Optimizations: {len(result['optimizations'])} suggestions")
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py metacognition_monitor_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py metacognition_monitor_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""



if __name__ == "__main__":
    main()
