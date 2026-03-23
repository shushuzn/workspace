"""
性能分析器
"""

import time
from typing import Dict, List
from collections import defaultdict


class PerformanceProfiler:
    """
    性能分析器
    
    功能:
    - 操作计时
    - 统计分析
    - 性能报告
    """

    def __init__(self):
        self.timers: Dict[str, float] = {}
        self.metrics: Dict[str, List[float]] = defaultdict(list)

    def start_timer(self, operation: str):
        """开始计时"""
        self.timers[operation] = time.time()

    def end_timer(self, operation: str) -> float:
        """结束计时"""
        if operation not in self.timers:
            return 0.0

        duration = time.time() - self.timers[operation]
        del self.timers[operation]

        self.metrics[operation].append(duration)
        return duration

    def get_stats(self, operation: str) -> Dict:
        """获取统计"""
        if operation not in self.metrics:
            return {'count': 0}

        durations = self.metrics[operation]

        return {
            'count': len(durations),
            'total': sum(durations),
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations),
        }

    def report(self) -> str:
        """生成性能报告"""
        if not self.metrics:
            return "No metrics recorded"

        lines = ["Performance Report", "=" * 50]

        for operation, durations in sorted(self.metrics.items()):
            stats = self.get_stats(operation)
            lines.append(
                f"{operation:25s}: {stats['avg']:.4f}s avg "
                f"({stats['min']:.4f}-{stats['max']:.4f}s, n={stats['count']})"
            )

        lines.append("=" * 50)

        # 总计
        total_time = sum(sum(d) for d in self.metrics.values())
        lines.append(f"Total time: {total_time:.4f}s")

        return "\n".join(lines)

    def reset(self):
        """重置统计"""
        self.timers.clear()
        self.metrics.clear()

    def __repr__(self):
        total_ops = sum(len(d) for d in self.metrics.values())
        return f"PerformanceProfiler(operations={total_ops})"
