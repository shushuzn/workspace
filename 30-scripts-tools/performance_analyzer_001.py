#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
性能瓶颈分析器 - 自动识别工作流瓶颈步骤
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

class PerformanceAnalyzer:
    """性能瓶颈分析器"""
    
    def __init__(self):
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
        self.history_file = Path("flow-archive/20260318-universal-workflow-001/execution-history.json")
        self.report_file = Path("flow-archive/20260318-universal-workflow-001/performance-report.json")
    
    def load_history(self) -> List[Dict]:
        """加载执行历史"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def analyze_step_performance(self) -> Dict:
        """分析步骤性能"""
        history = self.load_history()
        
        if not history:
            return {"error": "No execution history available"}
        
        # 统计每个步骤的耗时
        step_times = defaultdict(list)
        step_success = defaultdict(int)
        step_total = defaultdict(int)
        
        for execution in history:
            steps = execution.get('step_times', {})
            for step_id, step_data in steps.items():
                if 'duration_seconds' in step_data:
                    step_times[step_id].append(step_data['duration_seconds'])
                
                step_total[step_id] += 1
                if step_data.get('success', False):
                    step_success[step_id] += 1
        
        # 计算统计
        analysis = {}
        for step_id in step_times:
            times = step_times[step_id]
            analysis[step_id] = {
                "avg_time_seconds": sum(times) / len(times),
                "min_time_seconds": min(times),
                "max_time_seconds": max(times),
                "total_executions": len(times),
                "success_rate": (step_success[step_id] / step_total[step_id] * 100) if step_total[step_id] > 0 else 0
            }
        
        # 识别瓶颈（最慢的步骤）
        bottlenecks = sorted(
            analysis.items(),
            key=lambda x: x[1]['avg_time_seconds'],
            reverse=True
        )[:5]
        
        return {
            "total_executions": len(history),
            "step_analysis": analysis,
            "bottlenecks": [
                {"step_id": step_id, **data}
                for step_id, data in bottlenecks
            ],
            "recommendations": self._generate_recommendations(bottlenecks)
        }
    
    def _generate_recommendations(self, bottlenecks: List) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if bottlenecks:
            slowest = bottlenecks[0]
            step_id = slowest[0]
            avg_time = slowest[1]['avg_time_seconds']
            
            if avg_time > 60:
                recommendations.append(
                    f"Step {step_id} is very slow (avg {avg_time:.1f}s). Consider optimization."
                )
            elif avg_time > 30:
                recommendations.append(
                    f"Step {step_id} is moderately slow (avg {avg_time:.1f}s). Review for improvements."
                )
        
        # 检查成功率低的步骤
        analysis = self.analyze_step_performance().get('step_analysis', {})
        for step_id, data in analysis.items():
            if data.get('success_rate', 100) < 90:
                recommendations.append(
                    f"Step {step_id} has low success rate ({data['success_rate']:.1f}%). Investigate failures."
                )
        
        return recommendations
    
    def analyze_workflow_trend(self) -> Dict:
        """分析工作流趋势"""
        history = self.load_history()
        
        if len(history) < 2:
            return {"error": "Need at least 2 executions for trend analysis"}
        
        # 按时间排序
        sorted_history = sorted(
            history,
            key=lambda x: x.get('completed_at', '')
        )
        
        # 计算总耗时趋势
        total_times = []
        for execution in sorted_history[-10:]:  # 最近 10 次
            start = execution.get('started_at')
            end = execution.get('completed_at')
            if start and end:
                try:
                    start_dt = datetime.fromisoformat(start)
                    end_dt = datetime.fromisoformat(end)
                    total_times.append((end_dt - start_dt).total_seconds())
                except (Exception,):
                    pass
        
        if len(total_times) < 2:
            return {"error": "Insufficient timing data"}
        
        # 计算趋势
        avg_first_half = sum(total_times[:len(total_times)//2]) / (len(total_times)//2)
        avg_second_half = sum(total_times[len(total_times)//2:]) / (len(total_times) - len(total_times)//2)
        
        trend = "improving" if avg_second_half < avg_first_half else "degrading"
        improvement = ((avg_first_half - avg_second_half) / avg_first_half * 100) if avg_first_half > 0 else 0
        
        return {
            "total_executions_analyzed": len(total_times),
            "avg_time_first_half_seconds": avg_first_half,
            "avg_time_second_half_seconds": avg_second_half,
            "trend": trend,
            "improvement_percent": abs(improvement)
        }
    
    def generate_report(self, report_type: str = "full") -> Dict:
        """生成性能报告"""
        step_analysis = self.analyze_step_performance()
        trend_analysis = self.analyze_workflow_trend()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "report_type": report_type,
            "step_performance": step_analysis,
            "trend": trend_analysis,
            "summary": {
                "total_executions": step_analysis.get('total_executions', 0),
                "bottleneck_count": len(step_analysis.get('bottlenecks', [])),
                "trend_direction": trend_analysis.get('trend', 'unknown'),
                "top_bottleneck": step_analysis.get('bottlenecks', [{}])[0].get('step_id') if step_analysis.get('bottlenecks') else None
            }
        }
        
        # 保存报告
        with open(self.report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def display_status(self) -> str:
        """显示状态"""
        report = self.generate_report()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 20 + "Performance Analyzer")
        output.append("=" * 70)
        
        summary = report.get('summary', {})
        output.append(f"\n[Overview]")
        output.append(f"  Total Executions:  {summary.get('total_executions', 0)}")
        output.append(f"  Bottlenecks Found: {summary.get('bottleneck_count', 0)}")
        output.append(f"  Trend:             {summary.get('trend_direction', 'unknown').upper()}")
        
        bottlenecks = report.get('step_performance', {}).get('bottlenecks', [])
        if bottlenecks:
            output.append(f"\n[Top Bottlenecks]")
            for i, bn in enumerate(bottlenecks[:3], 1):
                output.append(f"  {i}. Step {bn['step_id']}: {bn['avg_time_seconds']:.1f}s avg")
        
        recommendations = report.get('step_performance', {}).get('recommendations', [])
        if recommendations:
            output.append(f"\n[Recommendations]")
            for rec in recommendations[:3]:
                output.append(f"  - {rec}")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)
    
    def run(self) -> Dict:
        """运行分析"""
        return {
            "report": self.generate_report(),
            "success": True
        }

def main():
    """测试入口"""
    analyzer = PerformanceAnalyzer()
    
    print("Performance Analyzer Test")
    print("=" * 70)
    
    # 生成报告
    report = analyzer.generate_report()
    print(f"\n[OK] Report generated at: {report['generated_at']}")
    
    # 显示状态
    print(analyzer.display_status())
    
    print(f"\n[OK] Analyzer test completed")

if __name__ == "__main__":
    main()
