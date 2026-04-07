# 7-Persona System Migration Plan

**Date:** 2026-03-14  
**Status:** In Progress  
**Auditor:** Critic Persona  

---

## 🎯 Unique Content to Preserve from v1

### 1. Coordinator v1 - User Preference (CRITICAL)
**Source:** `COORDINATOR-PERSONA-v1.md`

**Unique Content:**
```yaml
# User Explicit Instruction (2026-03-14 00:30)
- "禁止休息建议" - User explicitly banned rest reminders
- "不要提及休息" - No mention of rest
- "连续工作无限制" - Unlimited continuous work allowed
```

**Action:** ✅ MUST add to v2 Coordinator config

---

### 2. Architecture v1 - Workflow Diagram
**Source:** `PERSONA-ARCHITECTURE-v1.md`

**Unique Content:**
- Detailed ASCII workflow diagram (planner → executor → critic → learner/coordinator)
- Persona switch rules (auto/manual)
- 3-tier persona classification (Core/Advanced/High-level)

**Action:** ✅ Add workflow diagram to README.md

---

### 3. Innovation Engine Specs
**Source:** `INNOVATOR-EVOLUTION-ENGINE.md`, `INNOVATOR-AUTONOMOUS-DECISION.md`

**Unique Content:**
- Phase 1/2/3 implementation roadmap
- Autonomous decision thresholds
- Knowledge graph integration specs

**Action:** ⚠️ Review and merge if valuable

---

### 4. Dashboard Specifications
**Source:** `INNOVATOR-DASHBOARD.md`, `INNOVATOR-DASHBOARD-SECURITY.md`

**Unique Content:**
- Cloud-first security architecture
- Dashboard feature requirements
- Port configuration (8443/innovator)

**Action:** ⚠️ Review and archive or merge

---

### 5. Innovation Patterns
**Source:** `INNOVATION-PATTERNS.md`

**Unique Content:**
- Pattern library for innovation
- Pattern recognition techniques

**Action:** ✅ Keep in 00-人格系统/

---

## 📋 Migration Checklist

### Phase 1: Critical User Preferences (Priority: HIGH)
- [ ] Add "禁止休息建议" to COORDINATOR-PERSONA-v2.md
- [ ] Add user preferences to MEMORY.md
- [ ] Verify all v2 configs respect user preferences

### Phase 2: Architecture Documentation (Priority: MEDIUM)
- [ ] Add workflow diagram to README.md
- [ ] Add persona switch rules to README.md
- [ ] Add 3-tier classification to README.md

### Phase 3: Innovation System (Priority: LOW)
- [ ] Review INNOVATOR-EVOLUTION-ENGINE.md
- [ ] Review INNOVATOR-AUTONOMOUS-DECISION.md
- [ ] Merge valuable content or archive

### Phase 4: Archive v1 Files (Priority: LOW)
- [ ] Move v1 persona configs to 99-archive/ (after merging)
- [ ] Add archive metadata
- [ ] Update archive index

---

## ⚠️ Critical Lessons

**[MULTI-032]** 删除前必须对比分析
- Compare v1 vs v2 versions
- Evaluate file value (High/Medium/Low)
- Preserve unique content
- Never delete directly

**[MULTI-033]** 7 人格系统必须用于自身优化
- Must use 7-persona for system self-optimization
- Planner creates plan
- Critic reviews value
- Executor executes
- Never skip the process

**[MULTI-034]** 用户偏好必须保留
- User explicit instructions are CRITICAL
- Must migrate to new versions
- Never lose user preferences during refactoring

---

*Status:* Plan created, executing Phase 1
