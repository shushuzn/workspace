# HiMAC: Hierarchical Macro-Micro Learning

**Version:** 1.0  
**Based on:** arXiv:2603.00977  
**Status:** Proposed  
**Last Updated:** 2026-03-23

---

## 核心问题

### 现有方案的局限

| 方法 | 问题 |
|------|------|
| 平面自回归策略 | 高层推理和低层动作混在一个 token 序列中 |
| 单一策略网络 | 长程任务效率低，错误累积严重 |

### HiMAC 解决方案

```
HiMAC = Macro-Level + Micro-Level

Macro (规划层):
  └── Blueprint Generation (蓝图生成)
      - 生成结构化规划
      - 目标分解

Micro (执行层):
  └── Goal-Conditioned Action Execution
      - 根据目标条件执行
      - 反馈调整
```

---

## 核心机制

### 1. 层次分解

```python
class HiMACExecutor:
    def plan(self, task: str) -> Blueprint:
        # Macro: 生成结构化 blueprint
        blueprint = self.generate_blueprint(task)
        
        # Micro: 按蓝图逐步执行
        for subgoal in blueprint.subgoals:
            self.execute_subgoal(subgoal)
```

### 2. Critic-Free 优化

```python
class HierarchicalPolicyOptimizer:
    """
    不需要外部 critic，使用相对优势估计
    """
    def optimize(self, planner_actions, executor_actions):
        # 计算 planner 和 executor 的相对优势
        planner_advantage = self.estimate_planner_advantage(planner_actions)
        executor_advantage = self.estimate_executor_advantage(executor_actions)
        
        return planner_advantage + executor_advantage
```

### 3. 迭代共同进化

```
Planner 探索 ←→ Executor 适应
     ↑_________________________↓
```

---

## 与 FLARE 集成

HiMAC 可以与 FLARE 结合：

```
HiMAC (层次结构) + FLARE (未来感知)
                    ↓
┌─────────────────────────────────────┐
│  Macro-Level: FLARE Blueprint       │
│  - 考虑未来 N 步影响                 │
│  - 价值传播到早期决策                 │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│  Micro-Level: Goal-Conditioned Exec  │
│  - Subgoal 检查                      │
│  - 失败时触发 FLARE.replan()          │
└─────────────────────────────────────┘
```

---

## 关联文件

- `30-scripts-tools/05-AI-RESEARCH/himac_executor.py` - 实现代码
- `06-research/AI-研究/02-Models/HiMAC-Architecture_v1.0.md` - 本文档

---

## 参考

- Jin et al. "HiMAC: Hierarchical Macro-Micro Learning for Long-Horizon LLM Agents" arXiv:2603.00977
