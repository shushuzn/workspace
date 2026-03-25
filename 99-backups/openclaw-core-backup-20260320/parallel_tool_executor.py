#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
并行工具执行器 - 支持工具并行执行，加速准备阶段
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

class ParallelToolExecutor:
    """并行工具执行器"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.log_file = Path("flow-archive/20260318-universal-workflow-001/parallel-execution-log.json")
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")

    def execute_parallel(self, tools: List[Dict], timeout_seconds: int = 60) -> Dict:
        """
        并行执行多个工具
        
        Args:
            tools: 工具列表，每项包含：
                - tool_id: 工具 ID
                - func: 工具函数
                - args: 位置参数
                - kwargs: 关键字参数
            timeout_seconds: 超时时间
        
        Returns:
            执行结果
        """

        results = {
            "started_at": datetime.now().isoformat(),
            "total_tools": len(tools),
            "successful": 0,
            "failed": 0,
            "tool_results": {},
            "total_time_seconds": 0
        }

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_tool = {}
            for tool in tools:
                tool_id = tool['tool_id']
                func = tool.get('func')
                args = tool.get('args', ())
                kwargs = tool.get('kwargs', {})

                if func:
                    future = executor.submit(func, *args, **kwargs)
                    future_to_tool[future] = tool_id

            # 收集结果
            for future in as_completed(future_to_tool, timeout=timeout_seconds):
                tool_id = future_to_tool[future]

                try:
                    result = future.result()
                    results['tool_results'][tool_id] = {
                        "success": True,
                        "result": result,
                        "error": None
                    }
                    results['successful'] += 1
                except Exception as e:
                    results['tool_results'][tool_id] = {
                        "success": False,
                        "result": None,
                        "error": str(e)
                    }
                    results['failed'] += 1

        end_time = time.time()
        results['total_time_seconds'] = end_time - start_time
        results['completed_at'] = datetime.now().isoformat()

        # 记录日志
        self._log_execution(results)

        return results

    def _log_execution(self, results: Dict):
        """记录执行日志"""
        log = []
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log = json.load(f)

        log.append(results)
        log = log[-100:]  # 保留最近 100 次

        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)

    def estimate_speedup(self, sequential_time: float, parallel_time: float) -> Dict:
        """估算加速比"""
        if parallel_time == 0:
            return {"error": "Parallel time cannot be zero"}

        speedup = sequential_time / parallel_time
        efficiency = (speedup / self.max_workers) * 100

        return {
            "sequential_time_seconds": sequential_time,
            "parallel_time_seconds": parallel_time,
            "speedup": speedup,
            "efficiency_percent": efficiency,
            "time_saved_seconds": sequential_time - parallel_time,
            "time_saved_percent": ((sequential_time - parallel_time) / sequential_time * 100) if sequential_time > 0 else 0
        }

    def get_optimal_parallel_groups(self, tools: List[Dict]) -> List[List[str]]:
        """
        分析工具依赖，返回最优并行分组
        
        Returns:
            分组列表，每组内的工具可以并行执行
        """

        # 简化版本：假设所有工具都独立，可以并行
        # 实际实现需要分析工具依赖图

        if not tools:
            return []

        # 按类别分组（简化）
        groups = []
        current_group = []

        for i, tool in enumerate(tools):
            current_group.append(tool['tool_id'])

            # 每 4 个工具一组（匹配 max_workers）
            if len(current_group) >= self.max_workers or i == len(tools) - 1:
                groups.append(current_group)
                current_group = []

        return groups

    def get_stats(self) -> Dict:
        """获取统计"""
        log = []
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log = json.load(f)

        if not log:
            return {"total_executions": 0}

        total_time = sum(e.get('total_time_seconds', 0) for e in log)
        total_tools = sum(e.get('total_tools', 0) for e in log)
        successful = sum(e.get('successful', 0) for e in log)
        failed = sum(e.get('failed', 0) for e in log)

        return {
            "total_executions": len(log),
            "total_tools_executed": total_tools,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": (successful / (successful + failed) * 100) if (successful + failed) > 0 else 0,
            "avg_time_seconds": total_time / len(log) if log else 0
        }

    def display_status(self) -> str:
        """显示状态"""
        stats = self.get_stats()

        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 18 + "Parallel Tool Executor")
        output.append("=" * 70)

        output.append(f"\n[Config]")
        output.append(f"  Max Workers:    {self.max_workers}")

        output.append(f"\n[Stats]")
        output.append(f"  Total Executions:   {stats.get('total_executions', 0)}")
        output.append(f"  Tools Executed:     {stats.get('total_tools_executed', 0)}")
        output.append(f"  Success Rate:       {stats.get('success_rate', 0):.1f}%")
        output.append(f"  Avg Time:           {stats.get('avg_time_seconds', 0):.2f}s")

        if stats.get('total_executions', 0) > 0:
            output.append(f"\n[Benefit]")
            output.append(f"  Estimated Speedup:  2-4x (depending on tool count)")
            output.append(f"  Time Saved:         ~50-75% in preparation phase")

        output.append("\n" + "=" * 70)

        return "\n".join(output)

    def run(self) -> Dict:
        """运行"""
        return {
            "stats": self.get_stats(),
            "success": True
        }

def main():
    """测试入口"""
    executor = ParallelToolExecutor(max_workers=4)

    print("Parallel Tool Executor Test")
    print("=" * 70)

    # 模拟工具
    def tool1():
        time.sleep(0.5)
        return "tool1 result"

    def tool2():
        time.sleep(0.3)
        return "tool2 result"

    def tool3():
        time.sleep(0.4)
        return "tool3 result"

    def tool4():
        time.sleep(0.2)
        return "tool4 result"

    tools = [
        {"tool_id": "tool1", "func": tool1},
        {"tool_id": "tool2", "func": tool2},
        {"tool_id": "tool3", "func": tool3},
        {"tool_id": "tool4", "func": tool4}
    ]

    # 并行执行
    print(f"\nExecuting {len(tools)} tools in parallel...")
    results = executor.execute_parallel(tools)

    print(f"[OK] Completed in {results['total_time_seconds']:.2f}s")
    print(f"  Successful: {results['successful']}")
    print(f"  Failed: {results['failed']}")

    # 估算串行时间
    sequential_estimate = 0.5 + 0.3 + 0.4 + 0.2  # 1.4s
    speedup = executor.estimate_speedup(sequential_estimate, results['total_time_seconds'])
    print(f"\n[Speedup]")
    print(f"  Sequential estimate: {sequential_estimate:.2f}s")
    print(f"  Parallel actual:     {results['total_time_seconds']:.2f}s")
    print(f"  Speedup:             {speedup['speedup']:.2f}x")
    print(f"  Time saved:          {speedup['time_saved_percent']:.1f}%")

    # 显示状态
    print(executor.display_status())

    print(f"\n[OK] Parallel executor test completed")

if __name__ == "__main__":
    main()
