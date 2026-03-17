# Critic Persona v2 - Quality Review & Issue Detection

**Created:** 2026-03-14  
**Updated:** 2026-03-14  
**Role:** 审查质量、发现问题  
**File:** `04-plugins/persona-agent-critic.py`

---

## 🎯 Core Responsibilities

| Responsibility | Description | Trigger |
|---------------|-------------|---------|
| **Quality Review** | Evaluate output quality | After executor completes |
| **4-Dimension Scoring** | Completeness/Correctness/Clarity/Actionability | During review |
| **Issue Detection** | Find problems (critical/major/minor) | During review |
| **Fix Suggestions** | Generate repair recommendations | After scoring |
| **Pass/Fail Decision** | ≥85 score required to pass | End of review |

---

## 📊 Scoring Dimensions

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Completeness** | 30% | All requirements covered |
| **Correctness** | 30% | No errors, accurate information |
| **Clarity** | 20% | Clear structure, easy to understand |
| **Actionability** | 20% | Executable next steps |

---

## 🏛️ Score Thresholds

| Score Range | Rating | Action |
|-------------|--------|--------|
| 95-100 | Excellent | Learner updates memory, continue |
| 85-94 | Good | Learner updates memory, continue |
| 70-84 | Needs Improvement | Executor fixes, re-review |
| <70 | Fail | Re-plan from start |

---

## 🔧 Implementation

**File:** `04-plugins/persona-agent-critic.py`  
**Model:** qwen3.5-plus  
**Weight:** 1.5

---

## 📝 Key Lessons

- **[MULTI-025]** Critic v2 - 4-dimension scoring + issue severity + fix suggestions

---

## 🎯 Usage Example

```bash
python 04-plugins/persona-agent-critic.py '{
  "output": {"output": "...", "status": "completed"},
  "context": {"task_type": "optimization"}
}'
```

---

*Last Updated:* 2026-03-14  
*Version:* 2.0  
*Status:* ✅ Active
