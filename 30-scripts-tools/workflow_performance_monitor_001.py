import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流性能监控器 v1.0

功能：
1. 记录步骤执行时间
2. 对比预估时间 vs 实际时间
3. 识别性能瓶颈
4. 生成性能趋势报告

使用：
  py workflow_performance_monitor.py --start
  py workflow_performance_monitor.py --record --step 7 --time 45
  py workflow_performance_monitor.py --report
  py workflow_performance_monitor.py --trend
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class WorkflowPerformanceMonitor:
    """工作流性能监控器"""

    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.perf_log = self.workspace / "flow-archive/20260318-universal-workflow-001/performance-log.jsonl"
        self.current_session = None

    def start_session(self, session_id: str = None, workflow_id: str = None) -> None:
        """开始性能监控会话"""
        self.current_session = {
            'session_id': session_id or f"session-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'workflow_id': workflow_id or "20260318-universal-workflow-001",
            'started_at': datetime.now().isoformat(),
            'steps': []
        }
        return self.current_session

    def record_step(self, step_id: int, step_name: str, actual_time: float,
                    estimated_time: int = None, status: str = "completed") -> None:
        """记录步骤执行"""
        if not self.current_session:
            self.start_session()

        variance = 0
        if estimated_time:
            variance = actual_time - estimated_time

        step_record = {
            'step_id': step_id,
            'step_name': step_name,
            'actual_time': round(actual_time, 2),
            'estimated_time': estimated_time,
            'variance': round(variance, 2),
            'status': status,
            'timestamp': datetime.now().isoformat()
        }

        self.current_session['steps'].append(step_record)

        # 立即写入日志
        self._write_session()

        return step_record

    def _write_session(self) -> None:
        """写入会话日志"""
        if not self.current_session:
            return

        log_entry = self.current_session.copy()
        log_entry['recorded_at'] = datetime.now().isoformat()

        with open(self.perf_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def load_history(self, limit: int = 30) -> List[Dict]:
        """加载历史性能数据"""
        if not self.perf_log.exists():
            return []

        history = []
        with open(self.perf_log, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    history.append(entry)
                except (IOError, OSError, UnicodeDecodeError):
                    continue

        return history[-limit:]

    def analyze_performance(self) -> Dict:
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py workflow_performance_monitor_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_performance_monitor_001.py

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

分析性能数据"""
        history = self.load_history()

        if not history:
            return {'status': 'no_data', 'message': 'No performance data available'}

        # 按步骤聚合
        step_stats = defaultdict(lambda: {
            'count': 0,
            'total_actual': 0,
            'total_estimated': 0,
            'variances': []
        })

        for session in history:
            for step in session.get('steps', []):
                step_id = step.get('step_id')
                step_stats[step_id]['count'] += 1
                step_stats[step_id]['total_actual'] += step.get('actual_time', 0)

                est = step.get('estimated_time')
                if est:
                    step_stats[step_id]['total_estimated'] += est

                var = step.get('variance', 0)
                if var:
                    step_stats[step_id]['variances'].append(var)

        # 计算统计
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_sessions': len(history),
            'step_analysis': [],
            'bottlenecks': [],
            'optimizations': []
        }

        for step_id, stats in step_stats.items():
            avg_actual = stats['total_actual'] / stats['count'] if stats['count'] > 0 else 0
            avg_estimated = stats['total_estimated'] / stats['count'] if stats['count'] > 0 else 0

            avg_variance = sum(stats['variances']) / len(stats['variances']) if stats['variances'] else 0

            step_info = {
                'step_id': step_id,
                'executions': stats['count'],
                'avg_actual': round(avg_actual, 2),
                'avg_estimated': round(avg_estimated, 2) if avg_estimated > 0 else 'N/A',
                'avg_variance': round(avg_variance, 2),
                'variance_pct': round(avg_variance / avg_estimated * 100, 1) if avg_estimated > 0 else 0
            }

            analysis['step_analysis'].append(step_info)

            # 识别瓶颈：实际时间超过预估 20% 以上
            if avg_variance > 5 and stats['count'] >= 2:
                analysis['bottlenecks'].append({
                    'step_id': step_id,
                    'reason': f'实际时间 {avg_actual:.1f}s > 预估 {avg_estimated:.1f}s',
                    'suggestion': f'优化步骤 {step_id} 或调整预估时间'
                })

            # 识别优化：实际时间低于预估 20% 以上
            if avg_variance < -5 and stats['count'] >= 2:
                analysis['optimizations'].append({
                    'step_id': step_id,
                    'reason': f'实际时间 {avg_actual:.1f}s < 预估 {avg_estimated:.1f}s',
                    'suggestion': f'可减少步骤 {step_id} 预估时间'
                })

        # 排序
        analysis['step_analysis'].sort(key=lambda x: x['avg_actual'], reverse=True)

        return analysis

    def get_trend(self, step_id: int = None, days: int = 7) -> Dict:
        """获取性能趋势"""
        history = self.load_history(limit=100)

        # 过滤日期
        cutoff = datetime.now() - timedelta(days=days)
        recent = []

        for session in history:
            try:
                started = datetime.fromisoformat(session.get('started_at', ''))
                if started >= cutoff:
                    recent.append(session)
            except (Exception,):
                continue

        if not recent:
            return {'status': 'no_data', 'message': f'No data in last {days} days'}

        # 提取步骤时间
        step_times = defaultdict(list)

        for session in recent:
            for step in session.get('steps', []):
                sid = step.get('step_id')
                if step_id and sid != step_id:
                    continue
                step_times[sid].append(step.get('actual_time', 0))

        # 计算趋势
        trend = {
            'step_id': step_id,
            'days': days,
            'sessions': len(recent),
            'data_points': {}
        }

        for sid, times in step_times.items():
            if len(times) < 2:
                continue

            first_half = times[:len(times)//2]
            second_half = times[len(times)//2:]

            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)

            change_pct = ((avg_second - avg_first) / avg_first * 100) if avg_first > 0 else 0

            trend['data_points'][str(sid)] = {
                'avg_first_half': round(avg_first, 2),
                'avg_second_half': round(avg_second, 2),
                'change_pct': round(change_pct, 1),
                'trend': 'improving' if change_pct < -5 else ('degrading' if change_pct > 5 else 'stable')
            }

        return trend

    def generate_report(self) -> str:
        """生成性能报告"""
        analysis = self.analyze_performance()

        report = []
        report.append("=" * 70)
        report.append("工作流性能分析报告")
        report.append(f"时间: {analysis.get('timestamp', datetime.now().isoformat())}")
        report.append("=" * 70)
        report.append("")

        if analysis.get('status') == 'no_data':
            report.append("[无数据] 暂无性能数据")
            return "\n".join(report)

        # 总体统计
        report.append(f"总会话数: {analysis['total_sessions']}")
        report.append("")

        # 步骤分析
        report.append("步骤性能 (按实际时间排序):")
        report.append("-" * 70)
        report.append(f"{'步骤':<6} {'执行次数':<8} {'平均实际':<10} {'平均预估':<10} {'差异':<10}")
        report.append("-" * 70)

        for step in analysis['step_analysis']:
            est_display = f"{step['avg_estimated']}s" if step['avg_estimated'] != 'N/A' else 'N/A'
            var_sign = '+' if step['avg_variance'] > 0 else ''
            report.append(
                f"{step['step_id']:<6} {step['executions']:<8} "
                f"{step['avg_actual']:<10} {est_display:<10} "
                f"{var_sign}{step['avg_variance']}s"
            )

        report.append("")

        # 瓶颈
        if analysis['bottlenecks']:
            report.append("性能瓶颈:")
            for bn in analysis['bottlenecks']:
                report.append(f"  [!] 步骤 {bn['step_id']}: {bn['reason']}")
                report.append(f"      建议: {bn['suggestion']}")
            report.append("")

        # 优化建议
        if analysis['optimizations']:
            report.append("可优化项:")
            for opt in analysis['optimizations']:
                report.append(f"  [*] 步骤 {opt['step_id']}: {opt['reason']}")
            report.append("")

        report.append("=" * 70)

        return "\n".join(report)


logging.basicConfig(level=logging.INFO)
def main() -> None:
    """主函数"""
    monitor = WorkflowPerformanceMonitor()

    if len(sys.argv) < 2:
        print(monitor.generate_report())
        return

    command = sys.argv[1]

    if command == '--start':
        session = monitor.start_session()
        print(f"监控会话已启动: {session['session_id']}")

    elif command == '--record':
        if len(sys.argv) >= 5:
            step_id = int(sys.argv[2])
            step_name = sys.argv[3]
            actual_time = float(sys.argv[4])
            estimated_time = int(sys.argv[5]) if len(sys.argv) > 5 else None

            result = monitor.record_step(step_id, step_name, actual_time, estimated_time)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("用法: --record <step_id> <step_name> <actual_time> [estimated_time]")

    elif command == '--report':
        print(monitor.generate_report())

    elif command == '--trend':
        step_id = int(sys.argv[2]) if len(sys.argv) > 2 else None
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        result = monitor.get_trend(step_id, days)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif command == '--analyze':
        result = monitor.analyze_performance()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        print(f"未知命令: {command}")
        print("用法:")
        print("  py workflow_performance_monitor.py --start           启动监控")
        print("  py workflow_performance_monitor.py --record          记录步骤")
        print("  py workflow_performance_monitor.py --report          生成报告")
        print("  py workflow_performance_monitor.py --trend           趋势分析")


if __name__ == "__main__":
    main()