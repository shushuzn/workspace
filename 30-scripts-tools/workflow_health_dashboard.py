#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流健康度仪表板 - 可视化展示工作流执行健康度
指标：合规率、效率趋势、质量评分、问题预警
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class WorkflowHealthDashboard:
    """工作流健康度仪表板"""
    
    def __init__(self):
        self.history_file = Path("flow-archive/20260318-universal-workflow-001/execution-history.json")
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
        self.dashboard_file = Path("flow-archive/20260318-universal-workflow-001/health-dashboard.json")
    
    def load_history(self) -> List[Dict]:
        """加载执行历史"""
        
        if not self.history_file.exists():
            return []
        
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_metrics(self) -> Dict:
        """计算健康度指标"""
        
        history = self.load_history()
        
        if not history:
            return {
                "total_tasks": 0,
                "compliance_rate": 0,
                "avg_completion_time": 0,
                "quality_score": 0,
                "trend": "stable"
            }
        
        # 总任务数
        total_tasks = len(history)
        
        # 合规率（完成率 100% 的任务比例）
        compliant_tasks = sum(1 for h in history if h.get('progress', {}).get('completion_rate', 0) >= 100)
        compliance_rate = (compliant_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 平均完成时间（估算）
        completion_times = [h.get('progress', {}).get('completed', 0) for h in history]
        avg_completion = sum(completion_times) / len(completion_times) if completion_times else 0
        
        # 质量评分（基于完成步骤数）
        quality_scores = [h.get('progress', {}).get('completion_rate', 0) for h in history]
        quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # 趋势分析
        if len(history) >= 3:
            recent = [h.get('progress', {}).get('completion_rate', 0) for h in history[-3:]]
            if recent[-1] > recent[0] + 10:
                trend = "improving"
            elif recent[-1] < recent[0] - 10:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "total_tasks": total_tasks,
            "compliance_rate": compliance_rate,
            "avg_completion_time": avg_completion,
            "quality_score": quality_score,
            "trend": trend
        }
    
    def get_warnings(self) -> List[Dict]:
        """生成问题预警"""
        
        warnings = []
        metrics = self.calculate_metrics()
        
        # 合规率预警
        if metrics['compliance_rate'] < 80:
            warnings.append({
                "level": "high",
                "type": "compliance",
                "message": "Compliance rate below 80%",
                "action": "Review workflow enforcement"
            })
        elif metrics['compliance_rate'] < 100:
            warnings.append({
                "level": "medium",
                "type": "compliance",
                "message": "Compliance rate below 100%",
                "action": "Check missing steps"
            })
        
        # 质量预警
        if metrics['quality_score'] < 70:
            warnings.append({
                "level": "high",
                "type": "quality",
                "message": "Quality score below 70",
                "action": "Review quality gates"
            })
        
        # 趋势预警
        if metrics['trend'] == "declining":
            warnings.append({
                "level": "medium",
                "type": "trend",
                "message": "Performance declining",
                "action": "Investigate root cause"
            })
        
        return warnings
    
    def display_dashboard(self) -> str:
        """显示仪表板"""
        
        metrics = self.calculate_metrics()
        warnings = self.get_warnings()
        
        output = []
        output.append("\n" + "=" * 80)
        output.append(" " * 20 + "Workflow Health Dashboard")
        output.append("=" * 80)
        
        # 核心指标
        output.append("\n[Core Metrics]")
        output.append(f"  Total Tasks:        {metrics['total_tasks']}")
        output.append(f"  Compliance Rate:    {metrics['compliance_rate']:.1f}%")
        output.append(f"  Quality Score:      {metrics['quality_score']:.1f}/100")
        output.append(f"  Avg Completion:     {metrics['avg_completion_time']:.1f} steps")
        output.append(f"  Trend:              {metrics['trend'].upper()}")
        
        # 健康度等级
        health_score = (metrics['compliance_rate'] + metrics['quality_score']) / 2
        if health_score >= 95:
            health_level = "EXCELLENT"
            health_icon = "[OK]"
        elif health_score >= 80:
            health_level = "GOOD"
            health_icon = "[OK]"
        elif health_score >= 60:
            health_level = "FAIR"
            health_icon = "[WARN]"
        else:
            health_level = "POOR"
            health_icon = "[FAIL]"
        
        output.append(f"\n[Health Status]")
        output.append(f"  Score: {health_score:.1f}/100 - {health_level} {health_icon}")
        
        # 预警信息
        if warnings:
            output.append(f"\n[Warnings] ({len(warnings)} issues)")
            for w in warnings:
                level_mark = "[!!]" if w['level'] == 'high' else "[!]"
                output.append(f"  {level_mark} [{w['type'].upper()}] {w['message']}")
                output.append(f"       Action: {w['action']}")
        else:
            output.append(f"\n[Warnings] None")
        
        # 加载当前状态
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            output.append(f"\n[Current Task]")
            output.append(f"  Task: {state.get('task', 'N/A')}")
            output.append(f"  Status: {state.get('status', 'unknown')}")
            
            progress = state.get('completed_steps', [])
            output.append(f"  Completed Steps: {len(progress)}")
        
        output.append("=" * 80)
        
        # 保存仪表板数据
        dashboard_data = {
            "generated_at": datetime.now().isoformat(),
            "metrics": metrics,
            "warnings": warnings,
            "health_score": health_score,
            "health_level": health_level
        }
        
        with open(self.dashboard_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
        
        return "\n".join(output)
    
    def run(self) -> Dict:
        """运行仪表板"""
        
        metrics = self.calculate_metrics()
        warnings = self.get_warnings()
        health_score = (metrics['compliance_rate'] + metrics['quality_score']) / 2
        
        return {
            "metrics": metrics,
            "warnings": warnings,
            "health_score": health_score,
            "success": True
        }

def main():
    """测试入口"""
    dashboard = WorkflowHealthDashboard()
    
    print("Workflow Health Dashboard")
    print("=" * 80)
    
    # 运行并显示
    result = dashboard.run()
    print(dashboard.display_dashboard())
    
    print(f"\n[OK] Dashboard generated")
    print(f"[OK] Health Score: {result['health_score']:.1f}/100")

if __name__ == "__main__":
    main()
