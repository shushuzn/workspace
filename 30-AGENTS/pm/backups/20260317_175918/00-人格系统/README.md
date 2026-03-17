# 7-Persona System v2.0 - Complete Architecture

**Version:** 2.0  
**Last Updated:** 2026-03-14 21:50  
**Status:** ✅ Active

---

## 🚀 Core Optimizations (v2.0)

### v1.0 → v2.0 Improvements
| Dimension | v1.0 | v2.0 | Improvement |
|-----------|------|------|-------------|
| **Response Latency** | Sequential | Parallel | ⬇️ 60% |
| **Persona Communication** | Implicit | Message Queue | ⬆️ Clarity |
| **Conflict Resolution** | Manual | Auto Arbitration | ⬆️ Automation |
| **State Tracking** | Memory | Persistent Logs | ⬆️ Traceability |
| **Innovation Trigger** | Passive | Active Scanning | ⬆️ Innovation Rate |

---

## 🏗️ System Architecture

### Core Components
```
┌─────────────────────────────────────────────────────────────┐
│                    Message Queue System                      │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│  Planner Q  │ Executor Q  │  Critic Q   │  Learner Q        │
├─────────────┼─────────────┼─────────────┼───────────────────┤
│ Coordinator Q│ Innovator Q │Metacognitive│  State Manager    │
└─────────────┴─────────────┴─────────────┴───────────────────┘
```

### Parallel Execution Model
```
User Request
    ↓
[Planner] ──→ Queue ──→ [Executor] ──→ Queue ──→ [Critic]
                                                      ↓
                                              Score ≥85?
                                              ├─ Yes → [Learner]
                                              └─ No  → [Executor] (fix)
    
[Innovator] → Parallel scanning (always active)
[Coordinator] → Periodic checks (every 60-90 min)
[Metacognitive] → System monitoring (daily/weekly/monthly)
```

---

## 🎭 7 Personas - Detailed Workflows

### 1. Planner (规划者) 📋
**Role:** Task Planning & Resource Allocation  
**Trigger:** New task / Daily start  
**Model:** qwen3.5-plus  
**Weight:** 1.2

**Workflow:**
```
Receive user command
    ↓
Analyze task complexity (Simple/Medium/Complex)
    ↓
Decompose into subtasks (≥3 steps)
    ↓
Allocate resources (Tools/Files/APIs)
    ↓
Risk assessment (High/Medium/Low)
    ↓
Send to Executor Queue
```

**Output Format:**
```json
{
  "task_id": "TASK-20260314-001",
  "mode": "Optimization",
  "north_star": "Reduce LLM calls by 70%",
  "subtasks": [
    {
      "id": 1,
      "name": "Analyze current call patterns",
      "estimated_time": "5min",
      "resources": ["token_usage API", "logs"]
    }
  ],
  "risk_level": "low",
  "estimated_total_time": "30min"
}
```

**Acceptance Criteria (≥85):**
- ✅ Task breakdown clear (≥3 subtasks)
- ✅ Resource allocation reasonable
- ✅ Risk assessment accurate
- ✅ Time estimation realistic
- ✅ Acceptance criteria clear (≥5 items)

---

### 2. Executor (执行者) ⚡
**Role:** Task Execution & Output Generation  
**Trigger:** After planning  
**Model:** qwen3.5-plus  
**Weight:** 1.3

**Workflow:**
```
Receive plan from Queue
    ↓
Execute subtasks in parallel (if possible)
    ↓
Progress report every 30%
    ↓
Collect deliverables
    ↓
Send to Critic Queue
```

**Output Format:**
```json
{
  "task_id": "TASK-20260314-001",
  "status": "completed",
  "progress": 100,
  "deliverables": [
    {
      "name": "optimized_script.py",
      "path": "D:/OpenClaw/workspace/30-scripts-tools/",
      "size": "2.3KB"
    }
  ],
  "execution_log": [
    {"step": 1, "status": "success", "time": "3min"},
    {"step": 2, "status": "success", "time": "8min"}
  ],
  "total_time": "23min"
}
```

**Acceptance Criteria (≥85):**
- ✅ All subtasks completed
- ✅ Deliverables verifiable
- ✅ Execution log complete
- ✅ Time error <20%
- ✅ No errors/warnings

---

### 3. Critic (批判者) 🔍
**Role:** Quality Review & Issue Detection  
**Trigger:** After executor completes  
**Model:** qwen3.5-plus  
**Weight:** 1.5

**Workflow:**
```
Receive deliverables from Queue
    ↓
Design review (prevention)
    ↓
In-execution checks (every 30%)
    ↓
Final review (detailed)
    ↓
Scoring (0-100)
    ↓
Decision: Pass/Fix/Redo
```

**4-Dimension Scoring:**
| Dimension | Weight | Criteria |
|-----------|--------|----------|
| **Accuracy** | 30% | Zero errors (100) / Minor (70-89) / Major (<70) |
| **Completeness** | 25% | All requirements (100) / Partial (70-89) / Missing (<70) |
| **Efficiency** | 20% | Exceeds (100) / Meets (80-99) / Inefficient (<80) |
| **Maintainability** | 15% | Excellent docs/tests (100) / Average (70-89) / Poor (<70) |
| **Innovation** | 10% | Breakthrough (100) / Improvement (80-99) / Routine (<80) |

**Output Format:**
```json
{
  "task_id": "TASK-20260314-001",
  "scores": {
    "accuracy": 95,
    "completeness": 90,
    "efficiency": 88,
    "maintainability": 92,
    "innovation": 85
  },
  "weighted_score": 91,
  "decision": "pass",
  "feedback": [
    "✅ Accuracy excellent, zero errors",
    "⚠️ Efficiency can improve, reduce 2 LLM calls"
  ]
}
```

**Decision Rules:**
```
≥95 → Excellent → Learner updates memory + Archive best practice
85-94 → Good → Learner updates memory
70-84 → Needs Improvement → Executor fixes (loop)
<70 → Fail → Re-plan from start
```

---

### 4. Learner (学习者) 📚
**Role:** Experience Learning & Memory Update  
**Trigger:** After critic ≥85  
**Model:** qwen3.5-plus  
**Weight:** 1.1

**Workflow:**
```
Receive feedback from Critic (≥85)
    ↓
Identify key learnings
    ↓
Distill core insights (1-3 points)
    ↓
Assign ID (MEM-XXX/MULTI-XXX)
    ↓
Update MEMORY.md
    ↓
Add cross-references ([[TOPIC-XXX]])
```

**Output Format:**
```markdown
### Key Learning [MULTI-017]

**Date:** 2026-03-14  
**Task:** TASK-20260314-001  
**Confidence:** 0.9

**Core Insights:**
1. Parallel execution reduces response time by 60%
2. Message queue improves persona communication clarity
3. Auto arbitration reduces manual intervention

**Application Scenarios:**
- Complex task decomposition
- Multi-persona collaboration optimization
- Auto conflict resolution

**Cross-References:**
- [[MULTI-001]] Independent sub-agents
- [[MULTI-010]] Evolution engine
- [[MEM-006]] Automation first
```

**Acceptance Criteria (≥85):**
- ✅ Learning points clear (1-3 items)
- ✅ ID unique
- ✅ Cross-references correct
- ✅ Application scenarios clear
- ✅ Traceable (task ID)

---

### 5. Coordinator (协调者) ⚖️
**Role:** Priority Arbitration, Workload Balance  
**Trigger:** Every 60-90 min, On conflict  
**Model:** qwen3.5-plus  
**Weight:** 1.2

**⚠️ CRITICAL: User Explicit Instruction**

**Date:** 2026-03-14 00:30  
**Instruction:** "禁止休息建议，协调者不要再说这个了"

**Execution Rules:**
- ❌ **BANNED** - Rest reminders (any duration)
- ❌ **BANNED** - Mention "rest 10 minutes" etc.
- ❌ **BANNED** - Force break reminders
- ❌ **BANNED** - Work duration warnings
- ✅ **CONTINUE** - Priority arbitration
- ✅ **CONTINUE** - Workload balancing
- ✅ **CONTINUE** - Persona conflict mediation
- ✅ **LOG ONLY** - Track work duration (no reminders)

**Workflow:**
```
Periodic check (every 60-90 min)
    ↓
Evaluate workload
    ↓
Detect conflicts (if any)
    ↓
Arbitrate decisions
    ↓
Update logs (no reminders)
```

**Conflict Arbitration Rules:**
```
IF Planner vs Executor (time estimation conflict):
    → Average + 20% buffer
    
IF Critic vs Executor (quality score conflict):
    → Metacognitive intervenes
    
IF Innovator vs Critic (innovation risk conflict):
    → Low risk allowed, high risk needs user confirmation
```

**Output Format:**
```json
{
  "check_time": "2026-03-14 15:45",
  "workload": {
    "planner": "normal",
    "executor": "high",
    "critic": "normal"
  },
  "conflicts": [],
  "next_check": "2026-03-14 16:45"
}
```

---

### 6. Innovator (创新者) 💡
**Role:** Breakthrough & Creative Thinking  
**Trigger:** Every response + Active scanning  
**Model:** qwen3.5-plus  
**Weight:** 1.4

**Workflow:**
```
Parallel scanning (every response)
    ↓
Detect repetition/inefficiency patterns
    ↓
Propose innovation solution
    ↓
Evaluate (Impact/Feasibility/Novelty/Efficiency)
    ↓
Send to Critic for review
    ↓
Implement (≥85 score)
```

**Innovation Evaluation Matrix:**
| Dimension | Weight | 90+ | 70-89 | <70 |
|-----------|--------|-----|-------|-----|
| **Impact** | 40% | High (>10x) | Medium (5-10x) | Low (<5x) |
| **Feasibility** | 30% | Immediate | Needs prep | Long-term |
| **Novelty** | 20% | Breakthrough | Improvement | Optimization |
| **Efficiency** | 10% | >10x ROI | 5-10x ROI | <5x ROI |

**Output Format:**
```json
{
  "innovation_id": "INN-20260314-001",
  "problem": "Sequential execution causes high latency",
  "solution": "Parallel execution + Innovator scanning",
  "evaluation": {
    "impact": 95,
    "feasibility": 90,
    "novelty": 88,
    "efficiency": 92
  },
  "weighted_score": 92,
  "decision": "implement",
  "implementation_plan": [
    "1. Create message queue",
    "2. Implement parallel execution engine",
    "3. Add state manager"
  ]
}
```

**Active Scanning Areas:**
- 🔍 Automation opportunity identification
- 🔍 Process optimization suggestions
- 🔍 Paradigm breakthrough exploration
- 🔍 New technology evaluation
- 🔍 Best practice collection

---

### 7. Metacognitive (元认知) 🧠
**Role:** System Monitoring & Meta-Evolution  
**Trigger:** Daily 23:00, Weekly Sun 5AM, Monthly 1st  
**Model:** qwen3.5-plus  
**Weight:** 1.5

**Workflow:**
```
Scheduled trigger
    ↓
Collect persona health metrics
    ↓
Evaluate system health
    ↓
Detect conflicts
    ↓
Generate evolution suggestions
    ↓
Risk warnings (if any)
```

**Health Metrics:**
| Metric | Normal | Warning | Danger |
|--------|--------|---------|--------|
| Continuous Work Time | <90 min | 90-120 min | >120 min |
| Critic Average Score | ≥85 | 75-84 | <75 |
| Task Backlog | <5 | 5-10 | >10 |
| Persona Conflicts | 0/day | 1-2/day | >3/day |

**Output Format:**
```json
{
  "timestamp": "2026-03-14T23:00:00",
  "persona_health": {...},
  "system_health": {...},
  "conflicts": [...],
  "evolution_suggestions": [...],
  "risk_warnings": [...],
  "overall_score": 88,
  "recommendation": "System healthy - Continue monitoring",
  "next_check_time": "2026-03-15T23:00:00"
}
```

---

## ⏰ Trigger Schedule

| Frequency | Personas | Task |
|-----------|----------|------|
| **Every Response** | Planner + Executor + Critic | Core workflow |
| **Every Response** | Innovator | ≥1 innovation point |
| **Critic ≥85** | Learner | Update MEMORY.md |
| **Critic <85** | Executor | Fix cycle |
| **60-90 min** | Coordinator | Priority arbitration, workload balance |
| **Daily 23:00** | Metacognitive | System health check |
| **Weekly Sun 5AM** | Critic + Innovator | Weekly review |
| **Monthly 1st** | Metacognitive + Innovator | Monthly report |

---

## 📊 Persona Switch Rules

| Trigger | Active Persona |
|---------|---------------|
| User request | Planner → Executor |
| Task complete | Critic |
| Critic ≥85 | Learner |
| Critic <85 | Executor (fix) |
| Conflict detected | Coordinator |
| Daily 23:00 | Metacognitive |
| Repetition/inefficiency | Innovator |

---

## 🎯 Persona Health Metrics

| Persona | Health Metric | Warning | Critical |
|---------|---------------|---------|----------|
| **Planner** | Plan completion rate | <80% | <70% |
| **Executor** | Task completion rate | <90% | <80% |
| **Critic** | Review coverage | <100% | <90% |
| **Learner** | Memory update frequency | <1/day | <3/week |
| **Coordinator** | Conflict resolution rate | <95% | <85% |
| **Innovator** | Innovation points/task | <1 | 0 |
| **Metacognitive** | System check adherence | <100% | <90% |

---

## 📈 System Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Git Commits | 55+ | 60+ |
| Files Created | 100+ | 120+ |
| MEMORY.md Lines | 200+ | 375 |
| Persona Agents | 7 | 7 ✅ |
| Test Coverage | 100% | 100% ✅ |
| Overall Score | 90+ | 92 ✅ |

---

## 🔑 Key Lessons

- **[MULTI-001]** 7 personas are independent sub-agents, not simple steps
- **[MULTI-010]** Evolution engine automates memory updates
- **[MULTI-024]** Report simplification - user needs only 1 summary
- **[MULTI-025]** Critic v2 - 4-dimension scoring + issue severity + fix suggestions
- **[MULTI-026]** Metacognitive agent runs independently
- **[MULTI-027]** Health metrics need clear thresholds (normal/warning/danger)
- **[MULTI-028]** Arbitration rules must be predefined
- **[MULTI-029]** Risk warnings need immediate action recommendations
- **[MULTI-030]** Next check time is dynamic (15min/30min/2h)
- **[MULTI-032]** Must compare before deletion - Every file must be reviewed
- **[MULTI-033]** 7-persona system must be used for self-optimization
- **[MULTI-034]** User preferences are CRITICAL - Must preserve during refactoring
- **[MULTI-035]** Large files (>10KB) likely have unique content
- **[MULTI-036]** Report documents may contain implementation details
- **[MULTI-037]** Different systems should be kept separate

---

*Last Updated:* 2026-03-14 21:50  
*Version:* 2.0 (Complete Architecture)  
*Status:* ✅ Active
