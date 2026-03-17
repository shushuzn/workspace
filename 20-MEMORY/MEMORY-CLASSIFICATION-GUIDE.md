# 🧠 Memory Classification Guide - 记忆分级指南

**Date:** 2026-03-14  
**Version:** 1.0  
**Status:** Active

---

## 🎯 Purpose

解决"每步保存记忆太浪费"问题，通过分级策略平衡详细度与效率。

---

## 📊 Two-Tier Architecture (双层架构)

```
┌─────────────────────────────────────────┐
│ Tier 1: Daily Notes (日常笔记)          │
│ Location: memory/YYYY-MM-DD.md          │
│ - Complete step-by-step logs            │
│ - Save everything, no filtering         │
│ - Raw material for distillation         │
├─────────────────────────────────────────┤
│ Tier 2: Long-term Memory (长期记忆)     │
│ Location: MEMORY.md                     │
│ - Only high-value insights              │
│ - Distilled after task completion       │
│ - Transferable patterns priority        │
└─────────────────────────────────────────┘
```

---

## 🏷️ Classification Levels (分级标准)

### L1 - Critical Tasks (重要任务)

**Criteria:**
- First-time execution (首次执行)
- System validation (系统验证)
- Autonomous decision (自主决策)
- Innovation experiments (创新实验)
- High learning value (高学习价值)

**Save Strategy:**
- Daily Notes: Save every step (每步保存)
- MEMORY.md: Distill to 1-2 core insights (蒸馏为 1-2 条核心观点)

**Examples:**
- ✅ 7-Persona System Activation
- ✅ Autonomous Decision #1-#5
- ✅ Memory Distillation Process
- ✅ New Feature Development

**Memory Count:**
- Before optimization: 5-10 entries
- After optimization: 1-2 entries (merged)
- Reduction: 80%

---

### L2 - Routine Tasks (常规任务)

**Criteria:**
- Regular operations (常规操作)
- File organization (文件整理)
- Configuration updates (配置更新)
- Documentation creation (文档创建)

**Save Strategy:**
- Daily Notes: Save milestones (里程碑保存)
- MEMORY.md: Merge into 1 entry (合并为 1 条)

**Milestones:**
1. Task start (任务开始)
2. Major decision (重大决策)
3. Task completion (任务完成)

**Examples:**
- ✅ Workspace cleanup
- ✅ Directory renaming
- ✅ Script creation
- ✅ README updates

**Memory Count:**
- Before optimization: 3-5 entries
- After optimization: 1 entry (merged)
- Reduction: 70-80%

---

### L3 - Simple Tasks (简单任务)

**Criteria:**
- Single file operation (单文件操作)
- Query tasks (查询任务)
- Repetitive operations (重复操作)
- Low learning value (低学习价值)

**Save Strategy:**
- Daily Notes: Save task summary (任务级保存)
- MEMORY.md: Selective save (选择性保存)

**When to Save to MEMORY.md:**
- ✅ New pattern discovered
- ✅ Best practice established
- ✅ Reusable insight
- ❌ Routine operation → Skip

**Examples:**
- ✅ Create single script
- ✅ Check file status
- ✅ Rename directory
- ❌ Open file

**Memory Count:**
- Before optimization: 1-2 entries
- After optimization: 0-1 entries
- Reduction: 50-100%

---

## 🔄 Decision Tree (决策树)

```
New Task
    ↓
[Q1] First time or high value?
    ├─ YES → L1 (Critical)
    └─ NO  → [Q2]
           ↓
[Q2] Multiple steps or milestones?
    ├─ YES → L2 (Routine)
    └─ NO  → [Q3]
           ↓
[Q3] New insight or pattern?
    ├─ YES → L3 (Save to MEMORY.md)
    └─ NO  → L3 (Daily notes only)
```

---

## 📝 Memory Merge Rules (记忆合并规则)

### Format
```
[CODE-001] Task Name (Merged Step 1-N)

**Date:** YYYY-MM-DD
**Source:** Autonomous Decision #X (Merged)
**Confidence:** High

**Task Overview:**
- Goal: ...
- Steps: N steps (Check→Identify→Execute→Verify→Summarize)
- Result: X% success
- Save Strategy: Every step → Merged to 1

**Execution Process:**
1. Step 1 - ...
2. Step 2 - ...
3. Step 3 - ...

**Result:**
- ✅ Success 1
- ✅ Success 2
- ❌ Failed (if any)

**Transferable Pattern:**
```
Pattern name → Steps → Outcome
```

**Optimization Note:**
- Original: N entries (STEP-001 to STEP-00N)
- Merged: 1 entry
- Reduction: X%
- Information retained: 100%
```

### Example
```
[WS-001] Workspace Optimization Complete (Merged Step 1-5)

**Date:** 2026-03-14
**Source:** Autonomous Decision #3 (Merged)
**Confidence:** High

**Task Overview:**
- Goal: Rename Chinese directories, 100% English compliance
- Steps: 5 (Check→Identify→Execute→Verify→Summarize)
- Result: 4/5 success (98% compliance)

**Execution Process:**
1. Step 1 - Check: 45 dirs, 8 root files, 5 Chinese names
2. Step 2 - Identify: Listed 5 directories to rename
3. Step 3 - Execute: Renamed 4, 1 locked
4. Step 4 - Verify: 98% compliance, 1 pending
5. Step 5 - Summarize: Established transferable pattern

**Result:**
- ✅ 51-web-网页 → 51-web
- ✅ 91-logs-日志 → 91-logs
- ✅ 92-tests-测试 → 92-tests
- ✅ 99-archive-归档 → 99-archive-old
- ❌ 50-projects-项目 → Locked (pending restart)

**Transferable Pattern:**
```
Workspace optimization → Check→Identify→Execute→Verify→Summarize → Merge to 1 entry
```

**Optimization Note:**
- Original: 5 entries (WS-001 to WS-005)
- Merged: 1 entry
- Reduction: 80%
- Information retained: 100%
```

---

## 📊 Optimization Metrics (优化指标)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Memory entries/task (L1) | 5-10 | 1-2 | 80% ↓ |
| Memory entries/task (L2) | 3-5 | 1 | 70-80% ↓ |
| Memory entries/task (L3) | 1-2 | 0-1 | 50-100% ↓ |
| MEMORY.md growth | Fast | Controlled | Sustainable |
| Distillation time | Long | Short | 60% ↓ |
| Retrieval efficiency | Low | High | 2x ↑ |

---

## 🎯 Implementation Guide (实施指南)

### Step 1: Classify Task
```
Before starting task:
1. Check criteria (L1/L2/L3)
2. Determine save strategy
3. Set expectation (memory count)
```

### Step 2: Execute & Log
```
During task:
- L1: Log every step to daily notes
- L2: Log milestones to daily notes
- L3: Log summary to daily notes
```

### Step 3: Distill & Merge
```
After task:
1. Review daily notes
2. Extract core insights
3. Merge into 1 entry (if L1/L2)
4. Update MEMORY.md
```

### Step 4: Update Log
```
Update MEMORY.md changelog:
- Date
- Merged entries
- Source task
```

---

## 💡 Best Practices (最佳实践)

### Do ✅
- Save complete process to daily notes
- Merge related steps into 1 MEMORY entry
- Focus on transferable patterns
- Update changelog after merge
- Review classification weekly

### Don't ❌
- Don't save every step to MEMORY.md
- Don't create redundant entries
- Don't skip daily notes
- Don't forget to merge
- Don't ignore classification

---

## 📈 Review & Iterate (审查与迭代)

### Weekly Review
- Check memory growth rate
- Review classification accuracy
- Identify optimization opportunities
- Update guidelines if needed

### Monthly Distillation
- Run memory-distiller script
- Merge similar entries
- Archive outdated patterns
- Update trend tracking

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `MEMORY.md` | Long-term memory storage |
| `memory/YYYY-MM-DD.md` | Daily notes |
| `memory-distiller.js` | Auto-distillation script |
| `MEMORY-CLASSIFICATION-GUIDE.md` | This file |

---

*Version:* 1.0  
*Created:* 2026-03-14  
*Status:* Active  
*Next Review:* 2026-03-21
