#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工具监控器 - 监控工具调用成功率、自动重试、fallback
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable
import traceback

class ToolMonitor:
    """工具监控器"""

    def __init__(self):
        self.log_file = Path("flow-archive/20260318-universal-workflow-001/tool-monitor-log.json")
        self.stats_file = Path("flow-archive/20260318-universal-workflow-001/tool-stats.json")
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict:
        """加载统计数据"""

        if self.stats_file.exists():
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "retry_count": 0,
            "fallback_count": 0,
            "tools": {}
        }

    def _save_stats(self):
        """保存统计数据"""

        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def call_tool(self, tool_id: str, tool_func: Callable,
                  args: tuple = (), kwargs: dict = None,
                  max_retries: int = 3,
                  fallback_func: Callable = None,
                  timeout_seconds: int = 60) -> Dict:
        """
        调用工具并监控
        
        Args:
            tool_id: 工具 ID
            tool_func: 工具函数
            args: 位置参数
            kwargs: 关键字参数
            max_retries: 最大重试次数
            fallback_func: fallback 函数
            timeout_seconds: 超时时间
        
        Returns:
            调用结果
        """

        kwargs = kwargs or {}
        start_time = datetime.now()

        # 初始化工具统计
        if tool_id not in self.stats['tools']:
            self.stats['tools'][tool_id] = {
                "calls": 0,
                "successes": 0,
                "failures": 0,
                "retries": 0,
                "fallbacks": 0,
                "avg_duration_ms": 0,
                "last_error": None
            }

        tool_stats = self.stats['tools'][tool_id]
        tool_stats['calls'] += 1
        self.stats['total_calls'] += 1

        result = {
            "tool_id": tool_id,
            "success": False,
            "result": None,
            "error": None,
            "retries": 0,
            "fallback_used": False,
            "duration_ms": 0
        }

        # 重试循环
        for attempt in range(max_retries + 1):
            try:
                # 调用工具
                tool_result = tool_func(*args, **kwargs)

                # 成功
                result['success'] = True
                result['result'] = tool_result
                tool_stats['successes'] += 1
                self.stats['successful_calls'] += 1

                break

            except Exception as e:
                error_msg = str(e)
                result['error'] = error_msg
                tool_stats['last_error'] = error_msg

                if attempt < max_retries:
                    # 重试
                    tool_stats['retries'] += 1
                    self.stats['retry_count'] += 1
                    result['retries'] += 1
                else:
                    # 所有重试失败
                    tool_stats['failures'] += 1
                    self.stats['failed_calls'] += 1

                    # 尝试 fallback
                    if fallback_func:
                        try:
                            fallback_result = fallback_func(*args, **kwargs)
                            result['success'] = True
                            result['result'] = fallback_result
                            result['fallback_used'] = True
                            tool_stats['fallbacks'] += 1
                            self.stats['fallback_count'] += 1
                        except Exception as fallback_error:
                            result['error'] = f"Original: {error_msg}, Fallback: {str(fallback_error)}"
                    else:
                        result['error'] = error_msg

        # 计算耗时
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        result['duration_ms'] = duration_ms

        # 更新平均耗时
        calls = tool_stats['calls']
        tool_stats['avg_duration_ms'] = (
            (tool_stats['avg_duration_ms'] * (calls - 1) + duration_ms) / calls
        )

        # 记录日志
        self._log_call(result)

        # 保存统计
        self._save_stats()

        return result

    def _log_call(self, result: Dict):
        """记录调用日志"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            **result
        }

        # 读取或创建日志
        log = []
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log = json.load(f)

        # 添加新条目
        log.append(log_entry)

        # 只保留最近 1000 条
        log = log[-1000:]

        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)

    def get_health_report(self) -> Dict:
        """获取健康报告"""

        total = self.stats['total_calls']
        success = self.stats['successful_calls']

        success_rate = (success / total * 100) if total > 0 else 0

        return {
            "total_calls": total,
            "successful_calls": success,
            "failed_calls": self.stats['failed_calls'],
            "success_rate": success_rate,
            "retry_count": self.stats['retry_count'],
            "fallback_count": self.stats['fallback_count'],
            "tools": self.stats['tools']
        }

    def display_status(self) -> str:
        """显示监控状态"""

        report = self.get_health_report()

        output = []
        output.append("\n" + "=" * 80)
        output.append(" " * 25 + "Tool Monitor Status")
        output.append("=" * 80)

        output.append(f"\n[Overall Stats]")
        output.append(f"  Total Calls:      {report['total_calls']}")
        output.append(f"  Successful:       {report['successful_calls']}")
        output.append(f"  Failed:           {report['failed_calls']}")
        output.append(f"  Success Rate:     {report['success_rate']:.1f}%")
        output.append(f"  Retries:          {report['retry_count']}")
        output.append(f"  Fallbacks:        {report['fallback_count']}")

        # 工具详情
        if report['tools']:
            output.append(f"\n[Tool Details]")
            for tool_id, stats in report['tools'].items():
                tool_rate = (stats['successes'] / stats['calls'] * 100) if stats['calls'] > 0 else 0
                output.append(f"\n  {tool_id}:")
                output.append(f"    Calls: {stats['calls']}")
                output.append(f"    Success Rate: {tool_rate:.1f}%")
                output.append(f"    Avg Duration: {stats['avg_duration_ms']:.1f}ms")
                if stats['last_error']:
                    output.append(f"    Last Error: {stats['last_error'][:50]}")

        output.append("=" * 80)

        return "\n".join(output)

    def run(self) -> Dict:
        """运行监控"""

        return {
            "report": self.get_health_report(),
            "success": True
        }

def main():
    """测试入口"""
    monitor = ToolMonitor()

    # 测试：模拟工具调用
    def sample_tool(x, y):
        return x + y

    def fallback_tool(x, y):
        return x * y

    print("Tool Monitor Test")
    print("=" * 80)

    # 成功调用
    result1 = monitor.call_tool("add-tool", sample_tool, args=(2, 3))
    print(f"\nTest 1 (success): {result1['success']}")

    # 失败调用（模拟异常）
    def failing_tool(x, y):
        raise Exception("Simulated failure")

    result2 = monitor.call_tool(
        "failing-tool",
        failing_tool,
        args=(2, 3),
        max_retries=2,
        fallback_func=fallback_tool
    )
    print(f"Test 2 (fallback): {result2['success']}, fallback={result2['fallback_used']}")

    # 显示状态
    print(monitor.display_status())

    print(f"\n[OK] Monitor test completed")

if __name__ == "__main__":
    main()
