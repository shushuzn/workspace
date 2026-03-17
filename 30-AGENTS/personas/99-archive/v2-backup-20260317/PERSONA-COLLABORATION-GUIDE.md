# 7-Persona Collaboration System v2.0

## Overview

Enhanced multi-persona collaboration system with inter-persona communication, conflict resolution, and real-time visualization.

**Version:** 2.0  
**Location:** `00-人格系统/`  
**Total Code:** 51 KB (3 tools)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  7-Persona Collaboration                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Planner  │──│Executor  │──│  Critic  │                  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                  │
│       │             │             │                         │
│       │  Messages   │             │  Score                  │
│       ▼             ▼             ▼                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Learner  │──│Innovator │──│   Meta   │                  │
│  └──────────┘  └──────────┘  │Cognition │                  │
│                              └────┬─────┘                  │
│                                   │                         │
│                              ┌────▼─────┐                  │
│                              │Coordinator│                  │
│                              │(Monitor)  │                  │
│                              └───────────┘                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Core Engine (`persona_collaboration.py` - 26.2 KB)

**Features:**
- Inter-persona messaging
- State tracking
- Conflict management
- Collaboration workflow
- Scoring system

**Key Classes:**
- `PersonaMessage` - Message with priority
- `PersonaState` - Internal state
- `Conflict` - Conflict record
- `PersonaCollaborationEngine` - Main engine

### 2. Web Dashboard (`persona_dashboard.py` - 16.9 KB)

**Features:**
- Real-time visualization
- Persona state cards
- Conflict tracking
- Message log
- Workload chart

**Endpoints:**
- `GET /` - Dashboard HTML
- `GET /api/state` - JSON state

### 3. Test Suite (`persona_tester.py` - 7.9 KB)

**Tests:**
- Message Sending ✅
- Conflict Resolution ✅
- Workflow Execution ✅
- Scoring System ✅
- State Persistence ✅

---

## Usage

### Run Collaboration Workflow

```bash
cd D:\OpenClaw\workspace
python 00-人格系统/persona_collaboration.py --run "Your task here"
```

### Visualize Collaboration Network

```bash
python 00-人格系统/persona_collaboration.py --visualize
```

### Start Web Dashboard

```bash
python 00-人格系统/persona_dashboard.py --serve --port 8083
```

Access at: http://localhost:8083

### Run Tests

```bash
python 00-人格系统/persona_tester.py --test
```

### Run Demo

```bash
python 00-人格系统/persona_tester.py --demo
```

---

## Collaboration Workflow

### Phase 1: Planning (Planner)
- Analyze task
- Create execution plan
- Assign steps to personas
- Send messages to Executor

### Phase 2: Execution (Executor)
- Execute plan steps
- Track progress
- Report completion
- Send messages to Critic

### Phase 3: Critical Review (Critic)
- Review output
- Score (≥85 to pass)
- Identify issues
- Send recommendations

### Phase 4: Learning (Learner)
- Extract lessons (if critic ≥85)
- Update memory
- Update knowledge graph
- Report to Meta-cognition

### Phase 5: Innovation (Innovator)
- Generate innovations
- Assess impact/feasibility
- Prioritize implementations
- Report to Planner

### Phase 6: Meta-cognition (Meta-cognition)
- Monitor system health
- Check persona states
- Detect issues
- Provide recommendations

### Continuous: Coordinator
- Monitor workload balance
- Detect imbalances
- Send coordination messages
- Ensure smooth collaboration

---

## Message System

### Priority Levels

| Level | Value | Use Case |
|-------|-------|----------|
| LOW | 1 | Status updates |
| NORMAL | 2 | Regular communication |
| HIGH | 3 | Important notifications |
| CRITICAL | 4 | Urgent issues |

### Message Structure

```json
{
  "id": "abc123",
  "sender": "planner",
  "receiver": "executor",
  "content": "Plan created for task...",
  "priority": 3,
  "timestamp": "2026-03-16T10:30:00",
  "read": false,
  "acted_upon": false
}
```

---

## Conflict Management

### Conflict Lifecycle

```
1. Emergence → 2. Detection → 3. Arbitration → 4. Resolution
```

### Severity Levels

| Level | Description | Action |
|-------|-------------|--------|
| low | Minor disagreement | Auto-resolve |
| medium | Significant difference | Meta-cognition arbitration |
| high | Major conflict | Immediate intervention |
| critical | System-threatening | Emergency protocol |

### Resolution Process

1. **Detection** - Meta-cognition or Coordinator detects
2. **Recording** - Create Conflict object
3. **Arbitration** - Meta-cognition evaluates
4. **Resolution** - Compromise or decision
5. **Learning** - Update collaboration scores

---

## Persona States

### Tracked Metrics

| Metric | Range | Description |
|--------|-------|-------------|
| Workload | 0-100% | Current task load |
| Confidence | 0-1 | Self-assessment |
| Collaboration Score | 0-1 | Teamwork effectiveness |
| Tasks Completed | count | Success count |
| Tasks Failed | count | Failure count |
| Messages Sent | count | Communication activity |
| Messages Received | count | Reception activity |
| Conflicts Involved | count | Conflict participation |

### State Persistence

**File:** `20-data-reports/persona_state.json`

**Auto-saved:** After each collaboration workflow

---

## Scoring System

### Individual Persona Score

```
Score = (Collaboration × 0.4) + 
        (1 - Conflicts/Total) × 0.3 + 
        (Completed/(Completed+Failed)) × 0.3
```

### Overall Collaboration Score

```
Overall = Average of all 7 persona scores
```

### Score Interpretation

| Score | Rating | Status |
|-------|--------|--------|
| 90-100 | Excellent | Optimal collaboration |
| 80-89 | Good | Effective teamwork |
| 70-79 | Fair | Room for improvement |
| <70 | Poor | Intervention needed |

---

## API Reference

### PersonaCollaborationEngine

```python
engine = PersonaCollaborationEngine()

# Send message
msg = engine.send_message(
    sender=PersonaRole.PLANNER,
    receiver=PersonaRole.EXECUTOR,
    content="Task details",
    priority=MessagePriority.HIGH
)

# Broadcast
engine.broadcast(
    sender=PersonaRole.COORDINATOR,
    content="Meeting in 5 minutes",
    exclude=[PersonaRole.META_COGNITION]
)

# Create conflict
conflict = engine.create_conflict(
    persona1=PersonaRole.PLANNER,
    persona2=PersonaRole.EXECUTOR,
    issue="Resource disagreement",
    severity='medium'
)

# Resolve conflict
resolved = engine.resolve_conflict(
    conflict_id=conflict.id,
    resolution="Agreed on distribution",
    arbitrator=PersonaRole.META_COGNITION
)

# Run workflow
result = engine.run_collaboration_workflow("Task description")

# Get scores
scores = engine.get_collaboration_score()
# Returns: {'overall': 87.5, 'by_persona': {...}, ...}

# Visualize
viz = engine.visualize_collaboration()
print(viz)
```

---

## State File Structure

```json
{
  "personas": {
    "planner": {
      "role": "planner",
      "workload": 45,
      "confidence": 0.85,
      "last_active": "2026-03-16T10:30:00",
      "tasks_completed": 12,
      "tasks_failed": 1,
      "collaboration_score": 0.88,
      "conflicts_involved": 2,
      "messages_sent": 24,
      "messages_received": 18
    },
    ...
  },
  "conflicts": [
    {
      "id": "abc123",
      "persona1": "planner",
      "persona2": "executor",
      "issue": "Resource allocation",
      "severity": "medium",
      "status": "resolved",
      "created_at": "2026-03-16T09:00:00",
      "resolved_at": "2026-03-16T09:15:00",
      "resolution": "Agreed on 70/30 split",
      "arbitrator": "meta_cognition"
    }
  ],
  "message_count": 156,
  "last_updated": "2026-03-16T10:30:00"
}
```

---

## Performance Metrics

### Collaboration Efficiency

- **Message Throughput:** ~50 messages/workflow
- **Conflict Resolution Time:** <1 minute (auto)
- **Workflow Duration:** ~5-10 minutes
- **State Save Frequency:** Per workflow

### Scalability

- **Max Message Queue:** Unlimited (FIFO)
- **Max Conflict History:** Unlimited (archivable)
- **Concurrent Workflows:** 1 (sequential by design)

---

## Best Practices

### 1. Monitor Workload Balance
- Keep workload variance <40%
- Coordinator auto-detects imbalance
- Redistribute if needed

### 2. Resolve Conflicts Quickly
- Auto-resolve low severity
- Escalate high severity immediately
- Document all resolutions

### 3. Maintain Communication
- Regular inter-persona messages
- Broadcast important updates
- Track message read status

### 4. Review Scores Regularly
- Check collaboration scores daily
- Investigate scores <70
- Celebrate scores >90

### 5. Persist State Frequently
- Auto-save after each workflow
- Backup state file regularly
- Archive old conflicts monthly

---

## Troubleshooting

### Issue: High Workload Imbalance

**Symptoms:** Workload variance >50%

**Solution:**
```python
# Coordinator sends rebalancing messages
engine.broadcast(
    PersonaRole.COORDINATOR,
    "Redistribute tasks",
    priority=MessagePriority.HIGH
)
```

### Issue: Frequent Conflicts

**Symptoms:** >5 conflicts/day

**Solution:**
1. Review conflict patterns
2. Adjust persona responsibilities
3. Improve communication protocols
4. Meta-cognition intervention

### Issue: Low Collaboration Scores

**Symptoms:** Overall score <70

**Solution:**
1. Identify low-scoring personas
2. Review message history
3. Check conflict involvement
4. Provide training/adjustment

---

## Future Enhancements

### Phase 3 (Planned)
- [ ] Machine learning for conflict prediction
- [ ] Adaptive messaging based on persona states
- [ ] Automated workload balancing
- [ ] Collaboration pattern mining
- [ ] Performance optimization recommendations

### Phase 4 (Vision)
- [ ] Multi-task collaboration
- [ ] External persona integration
- [ ] Distributed persona deployment
- [ ] Real-time collaboration analytics
- [ ] AI-assisted arbitration

---

## References

- **Location:** `00-人格系统/`
- **Documentation:** `00-人格系统/PERSONA-COLLABORATION-GUIDE.md`
- **State File:** `20-data-reports/persona_state.json`
- **Dashboard:** http://localhost:8083

---

*Last Updated:* 2026-03-16  
*Version:* 2.0  
*Status:* Production Ready ✅
