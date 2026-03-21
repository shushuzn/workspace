import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流进化系统 v1.0

功能：
1. 分析工作流执行历史
2. 计算步骤适应度
3. 生成进化建议
4. 应用进化变更

使用：
  py workflow_evolver.py --analyze
  py workflow_evolver.py --suggest
  py workflow_evolver.py --evolve
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict


class WorkflowEvolver:
    """工作流进化器"""

    def __init__(self, workflow_path: str = None):
        self.workspace = Path(__file__).parent.parent
        self.workflow_path = workflow_path or "flow-archive/20260318-universal-workflow-001/workflow.json"
        self.execution_log = self.workspace / "30-scripts-tools/tool_call_log.jsonl"
        self.evolution_log = self.workspace / "flow-archive/20260318-universal-workflow-001/evolution-log.jsonl"

    def load_workflow(self) -> Dict:
        """加载工作流"""
        with open(self.workspace / self.workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_execution_history(self, limit: int = 100) -> List[Dict]:
        """加载执行历史"""
        if not self.execution_log.exists():
            return []

        history = []
        with open(self.execution_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    history.append(entry)
                except (IOError, OSError, UnicodeDecodeError):
                    continue

        return history[-limit:]

    def analyze_step_performance(self) -> Dict:
        """分析步骤性能"""
        history = self.load_execution_history()
        workflow = self.load_workflow()

        # 按工具统计
        tool_stats = defaultdict(lambda: {
            'count': 0,
            'success': 0,
            'total_time': 0,
            'errors': []
        })

        for entry in history:
            tool_id = entry.get('tool_id', 'unknown')
            tool_stats[tool_id]['count'] += 1

            if entry.get('result') == 'success':
                tool_stats[tool_id]['success'] += 1

            if 'duration_seconds' in entry:
                tool_stats[tool_id]['total_time'] += entry['duration_seconds']

            if entry.get('result') == 'error':
                tool_stats[tool_id]['errors'].append(entry.get('error', 'unknown'))

        # 计算指标
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_entries': len(history),
            'tool_stats': {},
            'recommendations': []
        }

        for tool_id, stats in tool_stats.items():
            success_rate = stats['success'] / stats['count'] if stats['count'] > 0 else 0
            avg_time = stats['total_time'] / stats['count'] if stats['count'] > 0 else 0

            analysis['tool_stats'][tool_id] = {
                'count': stats['count'],
                'success_rate': round(success_rate, 3),
                'avg_time': round(avg_time, 2),
                'error_count': len(stats['errors'])
            }

            # 生成建议
            if success_rate < 0.8:
                analysis['recommendations'].append({
                    'type': 'reliability',
                    'tool': tool_id,
                    'issue': f"低成功率: {success_rate:.1%}",
                    'suggestion': '考虑替换或修复此工具'
                })

            if avg_time > 60:
                analysis['recommendations'].append({
                    'type': 'performance',
                    'tool': tool_id,
                    'issue': f"长执行时间: {avg_time:.1f}s",
                    'suggestion': '考虑优化或并行化'
                })

        return analysis

    def calculate_fitness(self, step: Dict, stats: Dict) -> float:
        """计算步骤适应度"""
        tool_id = step.get('tool_id', '')
        if not tool_id or tool_id == 'N/A':
            return 0.5  # 默认中等适应度

        tool_stat = stats.get(tool_id, {})

        # 权重
        w_success = 0.3
        w_time = 0.2
        w_value = 0.3
        w_mandatory = 0.2

        # 成功率得分
        success_score = tool_stat.get('success_rate', 0.9)

        # 时间得分 (越短越好)
        avg_time = tool_stat.get('avg_time', 30)
        time_score = max(0, 1 - avg_time / 120)  # 120s 为上限

        # 价值得分 (基于 mandatory)
        value_score = 1.0 if step.get('mandatory', False) else 0.7

        # 必要性得分
        mandatory_score = 1.0 if step.get('mandatory', False) else 0.8

        # 综合适应度
        fitness = (
            success_score * w_success +
            time_score * w_time +
            value_score * w_value +
            mandatory_score * w_mandatory
        )

        return round(fitness, 3)

    def suggest_evolution(self) -> Dict:
        """生成进化建议"""
        workflow = self.load_workflow()
        analysis = self.analyze_step_performance()

        suggestions = {
            'timestamp': datetime.now().isoformat(),
            'workflow_version': workflow.get('version', 'unknown'),
            'current_fitness': 0,
            'suggestions': [],
            'priority_order': []
        }

        # 计算每个步骤的适应度
        step_fitness = []
        steps = workflow.get('steps', [])

        for step in steps:
            fitness = self.calculate_fitness(step, analysis['tool_stats'])
            step_fitness.append({
                'step_id': step.get('step_id'),
                'name': step.get('name'),
                'fitness': fitness,
                'tool': step.get('tool_id')
            })

        # 按适应度排序
        step_fitness.sort(key=lambda x: x['fitness'])

        # 计算整体适应度
        suggestions['current_fitness'] = round(
            sum(s['fitness'] for s in step_fitness) / len(step_fitness), 3
        ) if step_fitness else 0

        # 生成进化建议
        for sf in step_fitness[:5]:  # 关注最低适应度的 5 个步骤
            if sf['fitness'] < 0.6:
                suggestions['suggestions'].append({
                    'priority': 'high',
                    'step_id': sf['step_id'],
                    'action': 'optimize',
                    'reason': f"低适应度: {sf['fitness']:.2f}",
                    'suggestion': f"优化或替换步骤 {sf['step_id']}: {sf['name']}"
                })
            elif sf['fitness'] < 0.75:
                suggestions['suggestions'].append({
                    'priority': 'medium',
                    'step_id': sf['step_id'],
                    'action': 'review',
                    'reason': f"中等适应度: {sf['fitness']:.2f}",
                    'suggestion': f"审查步骤 {sf['step_id']}: {sf['name']}"
                })

        # 检测可合并步骤
        for i, step in enumerate(steps[:-1]):
            next_step = steps[i + 1]
            if (not step.get('mandatory', False) and
                not next_step.get('mandatory', False) and
                step.get('estimated_time_seconds', 0) + next_step.get('estimated_time_seconds', 0) < 20):
                suggestions['suggestions'].append({
                    'priority': 'low',
                    'action': 'merge',
                    'steps': [step.get('step_id'), next_step.get('step_id')],
                    'reason': '连续可选短步骤',
                    'suggestion': f"考虑合并步骤 {step.get('step_id')} 和 {next_step.get('step_id')}"
                })

        # 优先级排序
        suggestions['priority_order'] = sorted(
            suggestions['suggestions'],
            key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('priority', 'low'), 2)
        )

        return suggestions

    def apply_evolution(self, auto: bool = False) -> Dict:
        """应用进化"""
        suggestions = self.suggest_evolution()

        result = {
            'timestamp': datetime.now().isoformat(),
            'applied': [],
            'skipped': [],
            'errors': []
        }

        if auto:
            # 自动应用低风险变更
            for suggestion in suggestions['priority_order']:
                if suggestion.get('priority') == 'low':
                    result['applied'].append(suggestion)
                    self._log_evolution(suggestion)
        else:
            # 需要人工确认
            result['skipped'] = suggestions['priority_order']

        return result

    def _log_evolution(self, suggestion: Dict):
        """记录进化日志"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'suggestion': suggestion
        }

        with open(self.evolution_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    def generate_report(self) -> str:
        """生成进化报告"""
        analysis = self.analyze_step_performance()
        suggestions = self.suggest_evolution()

        report = []
        report.append("=" * 70)
        report.append("工作流进化报告")
        report.append(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 70)
        report.append("")

        # 整体状态
        report.append("整体状态:")
        report.append(f"  当前版本: {suggestions['workflow_version']}")
        report.append(f"  整体适应度: {suggestions['current_fitness']:.1%}")
        report.append(f"  分析条目: {analysis['total_entries']}")
        report.append("")

        # 工具统计
        report.append("工具统计 (Top 10):")
        report.append("-" * 70)
        sorted_tools = sorted(
            analysis['tool_stats'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]

        for tool_id, stats in sorted_tools:
            report.append(
                f"  {tool_id:<30} "
                f"成功率: {stats['success_rate']:.1%}  "
                f"平均时间: {stats['avg_time']:.1f}s  "
                f"调用次数: {stats['count']}"
            )
        report.append("")

        # 进化建议
        report.append("进化建议:")
        report.append("-" * 70)
        for i, suggestion in enumerate(suggestions['priority_order'][:10], 1):
            priority = suggestion.get('priority', 'low')
            priority_display = {'high': '[高]', 'medium': '[中]', 'low': '[低]'}.get(priority, '[低]')
            report.append(f"  {i}. {priority_display} {suggestion['suggestion']}")
        report.append("")

        report.append("=" * 70)

        return "\n".join(report)


logging.basicConfig(level=logging.INFO)
def main():
    """主函数"""
    evolver = WorkflowEvolver()

    if len(sys.argv) < 2:
        # 默认生成报告
        print(evolver.generate_report())
        return

    command = sys.argv[1]

    if command == '--analyze':
        result = evolver.analyze_step_performance()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--suggest':
        result = evolver.suggest_evolution()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--evolve':
        auto = '--auto' in sys.argv
        result = evolver.apply_evolution(auto=auto)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--report':
        print(evolver.generate_report())

    else:
        print(f"未知命令: {command}")
        print("用法:")
        print("  py workflow_evolver.py --analyze   分析步骤性能")
        print("  py workflow_evolver.py --suggest   生成进化建议")
        print("  py workflow_evolver.py --evolve    应用进化")
        print("  py workflow_evolver.py --report    生成报告")


if __name__ == "__main__":
    main()