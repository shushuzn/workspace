# Metacognitive Persona v2 - System Monitor & Evolution Engine

**Created:** 2026-03-14  
**Updated:** 2026-03-14  
**Role:** Monitor system health, persona balance, meta-evolution decisions  
**File:** `04-plugins/persona-agent-metacognitive.py`

---

## 🎯 Core Responsibilities

| Responsibility | Description | Trigger |
|---------------|-------------|---------|
| **System Monitoring** | Monitor 7-persona overall health | Continuous |
| **Persona Health** | Ensure balanced persona development | Every response |
| **Meta-Evolution** | Decide system architecture changes | Daily/Weekly/Monthly |
| **Conflict Arbitration** | Final arbitration for persona conflicts | On conflict ≥3/day |
| **Risk Warning** | Generate risk alerts for system health | Real-time |

---

## 🔄 Trigger Schedule

### Automatic Triggers
| Condition | Action | Priority |
|-----------|--------|----------|
| Daily 23:00 | System health check | High |
| Weekly Sunday 23:00 | Weekly system review | High |
| Monthly 1st 00:00 | Monthly evolution decision | Critical |
| Persona conflicts ≥3/day |介入 arbitration | Critical |
| Any warning threshold triggered | System adjustment | High |
| Continuous work >90min | Force rest reminder | High |

### Manual Triggers
| Command | Action |
|---------|--------|
| "系统状态" | Report persona health |
| "架构评估" | Evaluate current architecture |
| "进化建议" | Propose evolution plan |
| "元认知审查" | Deep system review |

---

## 📊 Health Metrics

### Persona Health (7 Personas)
| Persona | Target Range | Warning Line | Critical Line |
|---------|-------------|--------------|---------------|
| 规划者 (Planner) | 70-90% | <60% | <50% |
| 执行者 (Executor) | 80-95% | <70% | <60% |
| 批判者 (Critic) | 85-95% | <80% | <70% |
| 学习者 (Learner) | 80-95% | <70% | <60% |
| 协调者 (Coordinator) | 80-95% | <70% | <60% |
| 创新者 (Innovator) | 75-90% | <65% | <55% |
| 元认知 (Metacognitive) | 90-98% | <85% | <75% |

### System Metrics
| Metric | Normal | Warning | Danger | Unit |
|--------|--------|---------|--------|------|
| Continuous Work Time | <90 min | 90-120 min | >120 min | minutes |
| Critic Average Score | ≥85 | 75-84 | <75 | score |
| Task Backlog | <5 | 5-10 | >10 | tasks |
| Persona Conflicts | 0/day | 1-2/day | >3/day | conflicts |

---

## ⚖️ Arbitration Rules

| Conflict | Principle | Priority | Reasoning |
|----------|-----------|----------|-----------|
| Executor vs Critic | Quality > Speed | Critic | Quality is system lifeline |
| Executor vs Coordinator | Health > Output | Coordinator | Health is long-term foundation |
| Planner vs Executor | Direction > Efficiency | Planner | Correct direction matters most |
| Innovator vs Critic | Balance innovation & quality | Metacognitive | Need balanced approach |
| Learner vs Executor | Evolution > Output | Learner | Evolution ensures competitiveness |

---

## 🏛️ Meta-Evolution Types

| Type | Description | Approval Required |
|------|-------------|-------------------|
| Parameter Tuning | Adjust thresholds, weights | Metacognitive self-decision |
| Persona Addition | Add 8th persona | Metacognitive + Learner |
| Architecture Refactor | Change persona relationships | Metacognitive + All personas |
| System Restart | Reset persona states | Metacognitive + User confirmation |

---

## 🔧 Implementation

### File Location
```
D:\OpenClaw\workspace\04-plugins\persona-agent-metacognitive.py
```

### Input Format
```json
{
  "system_state": {
    "personas": {
      "planner": {"avg_score": 88, "trend": "stable", "task_count": 5},
      "executor": {"avg_score": 92, "trend": "improving", "task_count": 8},
      ...
    },
    "continuous_work_minutes": 75,
    "critic_avg_score": 87,
    "task_backlog": 3,
    "persona_conflicts": 0
  },
  "context": {
    "current_time": "2026-03-14T20:30:00",
    "session_id": "xxx"
  }
}
```

### Output Format
```json
{
  "agent_id": "metacognitive-20260314203000",
  "agent_name": "元认知",
  "role": "监控系统本身、人格健康、元进化决策",
  "timestamp": "2026-03-14T20:30:00",
  "persona_health": {...},
  "system_health": {...},
  "conflicts": [...],
  "arbitration": [...],
  "evolution_suggestions": [...],
  "risk_warnings": [...],
  "overall_score": 88,
  "recommendation": "系统良好 - 持续监控",
  "next_check_time": "2026-03-14T22:30:00"
}
```

---

## 📈 Evolution History

| Date | Event | Decision | Result |
|------|-------|----------|--------|
| 2026-03-14 | Metacognitive v2 created | 4-dimension health monitoring | ✅ Active |
| 2026-03-13 | Initial 7-persona system | Basic monitoring | ✅ Deployed |

---

## 🔍 Key Features v2

### Enhanced Monitoring
- ✅ Real-time persona health tracking (7 personas)
- ✅ System metric monitoring (4 key metrics)
- ✅ Automatic risk warning generation
- ✅ Conflict detection and arbitration

### Smart Suggestions
- ✅ Evolution suggestions based on health status
- ✅ Priority-based intervention recommendations
- ✅ Next check time calculation

### Arbitration Engine
- ✅ Rule-based conflict resolution
- ✅ Clear priority hierarchy
- ✅ Reasoning generation for decisions

---

## 🎯 Usage Example

```bash
# Run metacognitive agent
python 04-plugins/persona-agent-metacognitive.py '{
  "system_state": {
    "personas": {
      "planner": {"avg_score": 88},
      "executor": {"avg_score": 92},
      "critic": {"avg_score": 87},
      "learner": {"avg_score": 85},
      "coordinator": {"avg_score": 90},
      "innovator": {"avg_score": 83},
      "metacognitive": {"avg_score": 91}
    },
    "continuous_work_minutes": 75,
    "critic_avg_score": 87,
    "task_backlog": 3,
    "persona_conflicts": 0
  }
}'
```

---

## 📝 Lessons Learned

- **[MULTI-026]** Metacognitive agent must run independently, not as simple function
- **[MULTI-027]** Health metrics need clear thresholds (normal/warning/danger)
- **[MULTI-028]** Arbitration rules must be predefined for common conflicts
- **[MULTI-029]** Risk warnings should trigger immediate action recommendations
- **[MULTI-030]** Next check time should be dynamic based on risk level

---

*Last Updated:* 2026-03-14  
*Version:* 2.0  
*Status:* ✅ Active
