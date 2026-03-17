"""
Generic Early Exit Framework
通用早退决策框架

Date: 2026-03-07
Author: Claw (@OpenClaw)
Version: v0.1.0
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class ExitReason(Enum):
    """早退原因"""
    THRESHOLD_MET = "threshold_met"      # 达到阈值
    CONVERGENCE = "convergence"           # 收敛
    BUDGET_EXHAUSTED = "budget_exhausted" # 预算耗尽
    MAX_ITERATIONS = "max_iterations"     # 最大迭代
    MANUAL = "manual"                     # 手动触发


@dataclass
class EarlyExitResult:
    """早退结果"""
    should_exit: bool
    reason: Optional[ExitReason]
    iteration: int
    value: Any
    metadata: Dict[str, Any]


class EarlyExitStrategy(ABC):
    """早退策略基类"""
    
    @abstractmethod
    def should_exit(self, value: Any, iteration: int) -> EarlyExitResult:
        """判断是否应该早退"""
        pass


class ThresholdStrategy(EarlyExitStrategy):
    """阈值策略 - 达到阈值即退出"""
    
    def __init__(self, threshold: float, min_iterations: int = 1):
        self.threshold = threshold
        self.min_iterations = min_iterations
    
    def should_exit(self, value: Any, iteration: int) -> EarlyExitResult:
        if iteration < self.min_iterations:
            return EarlyExitResult(
                should_exit=False,
                reason=None,
                iteration=iteration,
                value=value,
                metadata={}
            )
        
        if value >= self.threshold:
            return EarlyExitResult(
                should_exit=True,
                reason=ExitReason.THRESHOLD_MET,
                iteration=iteration,
                value=value,
                metadata={"threshold": self.threshold}
            )
        
        return EarlyExitResult(
            should_exit=False,
            reason=None,
            iteration=iteration,
            value=value,
            metadata={}
        )


class ConvergenceStrategy(EarlyExitStrategy):
    """收敛策略 - 值收敛即退出"""
    
    def __init__(self, tolerance: float, window_size: int = 3):
        self.tolerance = tolerance
        self.window_size = window_size
        self.history = []
    
    def should_exit(self, value: Any, iteration: int) -> EarlyExitResult:
        self.history.append(value)
        
        if len(self.history) < self.window_size:
            return EarlyExitResult(
                should_exit=False,
                reason=None,
                iteration=iteration,
                value=value,
                metadata={}
            )
        
        # 检查收敛
        recent = self.history[-self.window_size:]
        max_diff = max(recent) - min(recent)
        
        if max_diff <= self.tolerance:
            return EarlyExitResult(
                should_exit=True,
                reason=ExitReason.CONVERGENCE,
                iteration=iteration,
                value=value,
                metadata={
                    "tolerance": self.tolerance,
                    "window_size": self.window_size,
                    "max_diff": max_diff
                }
            )
        
        return EarlyExitResult(
            should_exit=False,
            reason=None,
            iteration=iteration,
            value=value,
            metadata={}
        )


class BudgetStrategy(EarlyExitStrategy):
    """预算策略 - 预算耗尽即退出"""
    
    def __init__(self, max_budget: float, cost_fn: Callable[[Any], float]):
        self.max_budget = max_budget
        self.cost_fn = cost_fn
        self.total_cost = 0.0
    
    def should_exit(self, value: Any, iteration: int) -> EarlyExitResult:
        cost = self.cost_fn(value)
        self.total_cost += cost
        
        if self.total_cost >= self.max_budget:
            return EarlyExitResult(
                should_exit=True,
                reason=ExitReason.BUDGET_EXHAUSTED,
                iteration=iteration,
                value=value,
                metadata={
                    "max_budget": self.max_budget,
                    "total_cost": self.total_cost,
                    "current_cost": cost
                }
            )
        
        return EarlyExitResult(
            should_exit=False,
            reason=None,
            iteration=iteration,
            value=value,
            metadata={"total_cost": self.total_cost}
        )


class EarlyExitEngine:
    """早退引擎 - 组合多个策略"""
    
    def __init__(self):
        self.strategies = []
    
    def add_strategy(self, strategy: EarlyExitStrategy, name: str):
        """添加策略"""
        self.strategies.append((name, strategy))
    
    def should_exit(self, value: Any, iteration: int) -> EarlyExitResult:
        """检查所有策略"""
        for name, strategy in self.strategies:
            result = strategy.should_exit(value, iteration)
            if result.should_exit:
                result.metadata["strategy_name"] = name
                return result
        
        return EarlyExitResult(
            should_exit=False,
            reason=None,
            iteration=iteration,
            value=value,
            metadata={}
        )
    
    def execute_with_early_exit(
        self,
        fn: Callable[[int], Any],
        max_iterations: int = 100
    ) -> EarlyExitResult:
        """执行函数并支持早退"""
        for i in range(max_iterations):
            value = fn(i)
            result = self.should_exit(value, i)
            
            if result.should_exit:
                return result
        
        return EarlyExitResult(
            should_exit=True,
            reason=ExitReason.MAX_ITERATIONS,
            iteration=max_iterations,
            value=None,
            metadata={"max_iterations": max_iterations}
        )


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("Generic Early Exit Framework - Demo")
    print("=" * 60)
    
    # 示例 1: 阈值策略
    print("\n[Example 1] Threshold Strategy")
    threshold_strategy = ThresholdStrategy(threshold=0.9, min_iterations=3)
    engine = EarlyExitEngine()
    engine.add_strategy(threshold_strategy, "threshold")
    
    def mock_fn(iteration):
        return 0.7 + (iteration / 10) * 0.3
    
    result = engine.execute_with_early_exit(mock_fn, max_iterations=20)
    print(f"Exit at iteration {result.iteration}")
    print(f"Reason: {result.reason}")
    print(f"Value: {result.value:.4f}")
    
    # 示例 2: 收敛策略
    print("\n[Example 2] Convergence Strategy")
    convergence_strategy = ConvergenceStrategy(tolerance=0.01, window_size=3)
    engine2 = EarlyExitEngine()
    engine2.add_strategy(convergence_strategy, "convergence")
    
    def converge_fn(iteration):
        return 1.0 / (iteration + 1)
    
    result2 = engine2.execute_with_early_exit(converge_fn, max_iterations=100)
    print(f"Exit at iteration {result2.iteration}")
    print(f"Reason: {result2.reason}")
    print(f"Value: {result2.value:.4f}")
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
