# 元认知监控器 v2.0 设计文档

**任务:** 增强 metacognition_monitor.py 不确定性评估  
**日期:** 2026-03-20  
**工作流:** 20260318-universal-workflow-001

---

## 核心改动

### 1. 新增输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `uncertainty_index` | float (0-1) | 不确定性指数 |
| `confidence_level` | string | 置信等级: high/medium/low |
| `recommended_action` | string | 推荐行动 |

### 2. 不确定性评估算法

```
uncertainty_index = 
  task_ambiguity × 0.3 +
  context_gap × 0.25 + 
  (1 - historical_similarity) × 0.2 +
  risk_level × 0.25
```

### 3. 决策逻辑

| 确定性 | 置信等级 | 推荐行动 |
|--------|----------|----------|
| > 80% | high | `execute_directly` |
| 50-80% | medium | `propose_and_confirm` |
| < 50% | low | `wait_for_input` |

### 4. 输入参数

```python
{
  'task_complexity': float,      # 0-1, 任务复杂度
  'success_rate': float,         # 0-1, 历史成功率
  'user_satisfaction': float,    # 0-1, 用户满意度
  'task_ambiguity': float,       # 0-1, 任务模糊度
  'context_gap': float,          # 0-1, 上下文缺失度
  'historical_similarity': float,# 0-1, 历史相似度
  'risk_level': float            # 0-1, 风险等级
}
```

### 5. 输出示例

```json
{
  "consciousness_score": 0.72,
  "uncertainty_index": 0.25,
  "confidence_level": "high",
  "recommended_action": "execute_directly",
  "metacognition_report": "...",
  "timestamp": "2026-03-20T07:43:24"
}
```

---

## 工作流集成

### 步骤 9 更新

更新 `workflow.json` 中步骤 9 的 outputs:

```json
{
  "step_id": 9,
  "name": "元认知评估",
  "outputs": [
    "consciousness_score",
    "metacognition_report",
    "uncertainty_index",
    "confidence_level",
    "recommended_action"
  ]
}
```

### 下游影响

- `embedded_critic.py` 可读取 `recommended_action`
- `workflow_enforcer` 可根据 `confidence_level` 调整验证强度
- 高风险操作（`wait_for_input`）自动触发用户确认流程

---

## 实现位置

由于当前工作流系统无独立 Python 工具，此设计可由外部 tool_executor 实现，或作为规范文档指导后续开发。

**设计完成时间:** 2026-03-20 07:43 UTC