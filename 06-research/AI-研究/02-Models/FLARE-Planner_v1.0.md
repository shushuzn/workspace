# FLARE Planner: Future-Aware Planning for Long-Horizon LLM Agents

**Version:** 1.0  
**Based on:** arXiv:2601.22311  
**Status:** Proposed  
**Last Updated:** 2026-03-23

---

## 核心问题

### 为什么推理不能规划？

LLM 在短程推理上表现优异，但难以维持长程规划的一致性行为。

**根本原因:**
- Step-wise reasoning = Step-wise greedy policy
- 每步选择局部最优，但累积后导致长程失败
- 早期行动必须考虑延迟后果，但贪婪策略忽视这一点

```
当前问题:
Task: 研究论文 → 分析 → 写报告 → 提交
问题: 一次性分解后，如果"分析"发现问题，"写报告"可能需要重做
```

---

## FLARE 核心思想

### 三个关键机制

| 机制 | 作用 | 实现 |
|------|------|------|
| **Future-aware Lookahead** | 考虑行动对未来步骤的影响 | 评估每步的延迟后果 |
| **Value Propagation** | 下游结果影响早期决策 | 反向传播未来价值 |
| **Limited Commitment** | 避免过早锁定 | 动态调整承诺程度 |

---

## 架构设计

### FLARE Planner 类

```python
class FLAREPlanner:
    def __init__(
        self,
        lookahead_steps: int = 3,        # 考虑未来几步
        value_propagation: bool = True,   # 启用价值传播
        commitment_threshold: float = 0.7 # 承诺阈值
    ):
        self.lookahead_steps = lookahead_steps
        self.value_propagation = value_propagation
        self.commitment_threshold = commitment_threshold
        self.action_history = []
        self.future_value_cache = {}
    
    def plan(self, task: str, max_iterations: int = 10) -> Plan:
        """主规划函数"""
        # 1. 生成初始行动序列
        actions = self.generate_initial_actions(task)
        
        # 2. 迭代优化
        for i in range(max_iterations):
            # 3. 评估未来影响
            future_impacts = self.evaluate_future_impacts(actions)
            
            # 4. 价值传播
            if self.value_propagation:
                propagated_values = self.propagate_values(actions, future_impacts)
            
            # 5. 有限承诺检查
            actions = self.apply_limited_commitment(actions, propagated_values)
            
            # 6. 检查是否收敛
            if self.is_converged(actions):
                break
        
        return Plan(actions=actions, metadata=self.future_value_cache)
```

---

## 核心算法

### 1. Future-Aware Lookahead

```python
def evaluate_future_impacts(self, actions: List[Action]) -> Dict[int, float]:
    """
    评估每个行动的未来影响
    返回: {action_index: impact_score}
    """
    impacts = {}
    n = len(actions)
    
    for i, action in enumerate(actions):
        # 考虑从当前行动到任务结束
        future_actions = actions[i+1:min(i+self.lookahead_steps+1, n)]
        
        # 评估当前行动如何影响未来行动的成功率
        impact = self.estimate_impact(action, future_actions)
        impacts[i] = impact
    
    return impacts

def estimate_impact(self, current: Action, future: List[Action]) -> float:
    """
    估算当前行动对未来的影响
    考虑:
    - 当前行动为未来行动创造的条件
    - 当前行动可能带来的风险
    - 当前行动的不可逆性
    """
    enabling_score = self.check_enabling_conditions(current, future)
    risk_score = self.assess_risk(current, future)
    irreversibility = self.check_irreversibility(current)
    
    # 影响 = 促进分数 * (1 - 风险) * (1 - 不可逆性)
    impact = enabling_score * (1 - risk_score) * (1 - irreversibility * 0.5)
    
    return impact
```

### 2. Value Propagation

```python
def propagate_values(
    self, 
    actions: List[Action], 
    future_impacts: Dict[int, float]
) -> Dict[int, float]:
    """
    反向传播未来价值到早期行动
    """
    n = len(actions)
    propagated = {}
    
    # 从后向前传播
    for i in range(n - 1, -1, -1):
        if i == n - 1:
            # 最后一个行动的价值 = 直接影响
            propagated[i] = future_impacts.get(i, 0.0)
        else:
            # 当前行动价值 = 直接影响 + 未来价值的一部分
            direct = future_impacts.get(i, 0.0)
            future_value = propagated[i + 1] * 0.7  # 折扣因子
            
            # 当前行动对下游的影响系数
            downstream_coefficient = self.calculate_downstream_coefficient(
                actions[i], actions[i+1:]
            )
            
            propagated[i] = direct + downstream_coefficient * future_value
    
    return propagated

def calculate_downstream_coefficient(
    self, 
    current: Action, 
    downstream: List[Action]
) -> float:
    """
    计算当前行动对下游行动的影响系数
    """
    if not downstream:
        return 0.0
    
    # 关键行动 (为下游创造条件) 系数高
    if self.is_enabling_action(current, downstream):
        return 0.9
    
    # 例行行动系数中等
    if self.is_routine_action(current):
        return 0.5
    
    # 探索行动系数低但正值
    if self.is_exploration_action(current):
        return 0.3
    
    return 0.5  # 默认
```

### 3. Limited Commitment

```python
def apply_limited_commitment(
    self, 
    actions: List[Action], 
    propagated_values: Dict[int, float]
) -> List[Action]:
    """
    有限承诺机制：避免过早锁定某些行动
    """
    committed = []
    
    for i, action in enumerate(actions):
        value = propagated_values.get(i, 0.0)
        
        if value >= self.commitment_threshold:
            # 高价值行动 → 完全承诺
            action.commitment_level = "full"
            action.locked = True
        elif value >= self.commitment_threshold * 0.6:
            # 中等价值行动 → 柔性承诺
            action.commitment_level = "soft"
            action.locked = False
        else:
            # 低价值行动 → 保持灵活
            action.commitment_level = "flexible"
            action.locked = False
        
        committed.append(action)
    
    return committed

def should_replan(self, action: Action, execution_result) -> bool:
    """
    检查是否需要重新规划
    """
    if action.locked:
        return False  # 已承诺的行动不轻易重规划
    
    # 检查执行结果是否符合预期
    expected_outcome = action.expected_outcome
    actual_outcome = execution_result.actual_outcome
    
    # 如果偏差超过阈值，需要重规划
    deviation = self.calculate_deviation(expected_outcome, actual_outcome)
    return deviation > 0.3
```

---

## 与现有系统集成

### 集成点

| 现有模块 | 集成方式 |
|----------|----------|
| autonomous_research_agent.py | 替换一次性任务分解为 FLARE 迭代规划 |
| workflow_manager.py | 使用 FLAREPlanner 替代简单任务分解 |
| memory_distiller_v2.py | FLARE 评估记忆压缩的长期价值 |

### 集成示例

```python
# 在 autonomous_research_agent.py 中
from flare_planner import FLAREPlanner

class ResearchAgent:
    def __init__(self):
        self.planner = FLAREPlanner(
            lookahead_steps=3,
            value_propagation=True,
            commitment_threshold=0.7
        )
    
    def research_task(self, task: str):
        # 使用 FLARE 规划
        plan = self.planner.plan(task)
        
        for action in plan.actions:
            if not action.locked and self.should_replan(action, result):
                # 动态重规划
                plan = self.planner.replan(action, remaining_task)
            
            self.execute_action(action)
```

---

## 实现状态

| 组件 | 状态 | 说明 |
|------|------|------|
| FLAREPlanner 类 | ✅ 已完成 | 核心框架 |
| evaluate_future_impacts | ✅ 已完成 | 未来影响评估 |
| propagate_values | ✅ 已完成 | 价值传播 |
| apply_limited_commitment | ✅ 已完成 | 有限承诺 |
| Integration | ⏳ 待集成 | 需要与现有系统对接 |

---

## 关联文件

- `30-scripts-tools/05-AI-RESEARCH/flare_planner.py` - 实现代码
- `06-research/AI-研究/02-Models/FLARE-Planner_v1.0.md` - 本文档

---

## 参考

- Wang et al. "Why Reasoning Fails to Plan: A Planning-Centric Analysis of Long-Horizon Decision Making in LLM Agents" arXiv:2601.22311
