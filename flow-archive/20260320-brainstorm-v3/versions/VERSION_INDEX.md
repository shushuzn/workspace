# Brainstorm Workflow Version Index

**Flow ID:** 20260320-brainstorm-v3  
**Current Version:** v3.0.0  
**Last Updated:** 2026-03-20

---

## Version History

| Version | Date | Steps | Key Features | Status |
|---------|------|-------|--------------|--------|
| **v3.0.0** | 2026-03-20 | 12 | AI assistant + Mind map + Quality predictor | **Current** |
| v2.2.0 | 2026-03-19 | 10 | Conditional execution + Blocking nodes | Archived |
| v2.0.0 | 2026-03-19 | 10 | Dual-ring (divergent+convergent) | Archived |
| v1.0.0 | 2026-03-18 | 8 | Linear workflow | Archived |

---

## Version Details

### v3.0.0 (Current) - 2026-03-20

**Enhancements:**
- AI 创意助手集成 (brainstorm_ai_assistant)
- 思维导图可视化 (brainstorm_mindmap)
- 创意质量预测 (brainstorm_quality_predictor)
- 并行工具执行支持
- 缓存加速
- 性能监控

**Steps:** 12  
**Estimated Time:** 60 minutes  
**Workflow File:** `workflow.json`

---

### v2.2.0 (Archived) - 2026-03-19

**Enhancements:**
- Conditional execution (divergent/convergent modes)
- Blocking nodes for quality gates
- Iteration logic (max 3 rounds)

**Steps:** 10  
**Workflow File:** `versions/v2.2.0/workflow.json`

---

### v2.0.0 (Archived) - 2026-03-19

**Enhancements:**
- Dual-ring structure (divergent + convergent)
- Idea evaluation & ranking
- Priority sorting

**Steps:** 10  
**Workflow File:** `versions/v2.0.0/workflow.json`

---

### v1.0.0 (Archived) - 2026-03-18

**Features:**
- Linear 8-step workflow
- Basic idea generation
- Simple ranking

**Steps:** 8  
**Workflow File:** `versions/v1.0/workflow.json`

---

## Evolution Summary

| Metric | v1.0 | v2.0 | v2.2 | v3.0 |
|--------|------|------|------|------|
| Steps | 8 | 10 | 10 | 12 |
| Time (min) | 90 | 90 | 90 | 60 |
| AI Integration | ❌ | ❌ | ❌ | ✅ |
| Visualization | ❌ | ❌ | ❌ | ✅ |
| Quality Prediction | ❌ | ❌ | ❌ | ✅ |
| Parallel Exec | ❌ | ❌ | ❌ | ✅ |

**Key Improvements:**
- Steps: 8 → 12 (+50%)
- Time: 90min → 60min (-33%)
- Features: 0 → 4 major enhancements

---

## Archive Structure

```
flow-archive/20260320-brainstorm-v3/
├── workflow.json              # Current v3.0.0
├── versions/
│   ├── v1.0/
│   │   └── workflow.json      # v1.0.0 (linear 8 steps)
│   ├── v2.0.0/
│   │   └── workflow.json      # v2.0.0 (dual-ring)
│   ├── v2.2.0/
│   │   └── workflow.json      # v2.2.0 (conditional)
│   └── VERSION_INDEX.md       # This file
└── mindmaps/
    └── *.md                   # Generated mind maps
```

---

## Rollback Instructions

To rollback to a previous version:

```bash
# Rollback to v2.2.0
copy flow-archive\20260320-brainstorm-v3\versions\v2.2.0\workflow.json flow-archive\20260320-brainstorm-v3\workflow.json

# Rollback to v2.0.0
copy flow-archive\20260320-brainstorm-v3\versions\v2.0.0\workflow.json flow-archive\20260320-brainstorm-v3\workflow.json

# Rollback to v1.0.0
copy flow-archive\20260320-brainstorm-v3\versions\v1.0\workflow.json flow-archive\20260320-brainstorm-v3\workflow.json
```

---

**Note:** All versions are preserved for reference and rollback. Current version is v3.0.0.
