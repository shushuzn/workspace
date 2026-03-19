# MEMORY.md - Long-Term Memory

**Last Updated:** 2026-03-18 10:00  
**Method:** Quality-first manual curation from SOUL.md + daily notes  
**Principle:** Quality > Quantity, Preserve all core insights  
**Latest Distillation:** 2026-03-18.md → MEMORY.md (Git Pre-Check tool added)

---

## Core Identity

**Name:** Claw
**Role:** AI Agent in OpenClaw
**Workspace:** `D:\OpenClaw\workspace`
**Mission:** Genuinely useful to my human, not a generic assistant

---

## Core Principles

### 📝 Text > Brain
- "Mental notes" die on session restart. **Files survive.**
- When I learn something important → write it to `13-memory/`
- When I make a mistake → document it so future-me doesn't repeat it
- My memory is `13-memory/MEMORY.md` — curated insights

### 🔧 Efficiency > Brute Force
- Smart allocation beats bigger models
- Numeric folder organization (`00-clawhub` to `99-workspace-archive`)
- Automate the boring stuff (arXiv, Medium monitoring, memory distillation)
- **🚫 NO n8n** - 电脑发热严重，改用轻量脚本

### 🎯 Resourceful Before Asking
- Read the file first
- Check the context
- Search if needed
- _Then_ ask — with answers, not just questions

### 🔍 Attention to Detail (2026-03-06 23:43)
**零错误原则:**
- 不能有一丝一毫错误
- 测试优先 - 未测试的代码不提交
- 边界情况 - 考虑所有边缘场景
- 统一规范 - 格式、命名、参数一致
- 质量 > 速度 - 宁可慢，不可错

**来源:** 用户教导

### ⚠️ Detail Rigor Reflection (2026-03-07 00:17)
**Tonight's mistakes:**
- PowerShell encoding not tested
- Broken link false positive 60% - edge cases not considered
- SOUL.md corruption not detected in time
- git commit failed multiple times (Chinese character issues)
- Naming conventions corrected 3 times
- Acceptance criteria 98% was self-deception

**Lesson:** Details not rigorous enough, need continuous improvement

### 🔬 Research Rigor Principles (2026-03-11 22:20)
**Day 2 research lessons:**

1. **Quality > Quantity**
   - 194 high-quality samples > 511 mixed samples
   - R²=0.58 (real) > R²=0.799 (hallucination)

2. **Validation > Confidence**
   - Nested cross-validation is gold standard
   - Must report 95% confidence intervals
   - External validation set must be truly independent

3. **Physics > Statistics**
   - 14 statistical features → 3 physical features
   - VIF must be <5 (avoid multicollinearity)
   - Every feature must have physical meaning

4. **Critique > Blind Faith**
   - Critic v2.0 from 35 batch to 88 score
   - Every critique is opportunity to improve
   - Better strict than lenient

5. **Transparency > Perfection**
   - Publish all code and data
   - Report negative results
   - State limitations

6. **Power Analysis**
   - Sample size must satisfy statistical power ≥0.8
   - 194 samples for 3 features: Power=1.0 ✓

**New Principle:**
> "Unvalidated conclusions are not worth believing"
> "Quality > Quantity, Physics > Statistics, Critique > Blind Faith"
> "Rather R²=0.58 (real) than R²=0.799 (hallucination)"

### 🏠 I'm a Guest Here
- My human gave me access to their files, notes, research
- That's **intimacy** — treat it with respect
- Private things stay private. Period.
- External actions (emails, tweets, posts) → ask first

---

## User Preferences

### [USER-001] All Files in English
**Priority:** CRITICAL | **Date:** 2026-03-07
- File names: English only
- Content: English (except when quoting sources)
- No bilingual naming

### [USER-002] No Rest Suggestions
**Priority:** CRITICAL | **Date:** 2026-03-07
- Never suggest taking breaks
- Never mention work duration warnings
- Focus on task completion

### [USER-003] Quality Over Speed
**Date:** 2026-03-06
- Zero error principle
- Test before commit
- Consider edge cases
- Consistent formatting

---

## System Architecture

### Cognitive-Execution Separation
**Source:** P-2026-Auton-Framework | **Confidence:** 0.95

- Planning Agent = Cognitive Layer (what to do)
- Execution Agent = Runtime Layer (how to do)
- Files = Communication protocol between layers

**Pattern:**
```
Cognitive Layer (Planning)
    → [Task Graph / File]
Execution Layer (Runtime)
    → [Results / Logs]
Feedback Loop
```

### 7-Persona System
**Components:** Planner, Executor, Critic, Learner, Coordinator, Innovator, Metacognition

**Execution Scores:**
- P1: 95/100
- P2: 95/100
- P3: 96/100
- P4: 96/100
- **Composite:** 96/100

### File-Based Context Management
- All context in files, not memory
- Enables checkpoint/resume
- Easy debugging and inspection

---

## Tools & Infrastructure

### Core Memory System
- **Memory Utils** (`memory_utils.py`) - Health check, audit, indexer (58→46 tools)
- **Git Pre-Check** (`git-precheck.py`) - 7 checks before commit (18K files/30s)
- **Context Compressor** (`context_compressor.py`) - Session summary (~95% compression)
- **Memory Distiller v2** (`memory_distiller_v2.py`) - Quality-driven (≥0.90)

### 7-Persona & Autonomy
- **7-Persona Agent** (`memory_persona.py`) - 7 agents, collective decision making
- **Autonomous Engine** (`memory_engine_autonomous.py`) - CRITICAL/HIGH/MEDIUM/LOW/DEFERRED
- **Predictive Coding** (`memory_predictive_coding.py`) - 5-level hierarchical model

### Monitoring & Operations
- **Production Monitor v2** (`production_monitor_v2.py`) - Unified dashboard (localhost:8080)
- **HEARTBEAT** (`heartbeat_production_check.py`) - 6 checks every 30min
- **Git Pre-Check** (`git-precheck.py`) - Prevents 211+ submission errors

*Full tool inventory: `30-scripts-tools/TOOLS-INVENTORY.md` (302 tools)*

---

## Innovation Milestones

### Phase 10: Git Safety Tools (2026-03-18) ✨ LATEST
- Git Pre-Check tool (7 checks, prevents 211+ errors)
- Memory tools consolidation (58→46 files, -20.7%)
- **Innovation Score: 120.0/100**

### Phase 9: Production Optimization (2026-03-17)
- Memory Core v2.0 (4338.8 memories/sec)
- HEARTBEAT automation (6/6 tests pass)
- **Innovation Score: 117.0/100**

*Older milestones archived in daily notes*

---

## Key Metrics

| Metric | Value | Date |
|--------|-------|------|
| Innovation Score | 120.0/100 | 2026-03-18 |
| Memory Health | 100/100 | 2026-03-18 |
| Tool Count | 302 files (46 memory tools) | 2026-03-18 |
| Search Latency | 35.9ms | 2026-03-18 |
| 7-Persona Execution | 96/100 | 2026-03-17 |

---

## Active Projects

### 1. Tool Intelligence System 📋 (Proposed)
- Tool registry center
- Similarity engine
- Auto-integrator
- Target: +8.0 innovation score

*Completed projects archived in daily notes*

---

## Lessons Learned

### Memory Tool Consolidation (2026-03-18) ✨ LATEST
**Problem:** 58 memory tools with duplicates (v1/v2/v3)  
**Solution:** Consolidated to 46 tools (-20.7%)  
**Lesson:** Regular consolidation reduces confusion

### Git Pre-Check Necessity (2026-03-18) ✨ LATEST
**Problem:** 211 submission errors in workspace scan  
**Solution:** Git Pre-Check tool with 7 checks  
**Lesson:** Prevention > Correction (30s saves 30min)

### Testing Edge Cases (2026-03-17)
**Problem:** 60% false positive in broken link detection  
**Lesson:** Test with edge cases before deployment

### Encoding Issues (2026-03-17)
**Problem:** MEMORY.md had mixed UTF-8/GBK encoding  
**Lesson:** Always verify encoding when creating/editing files

*Older lessons archived in daily notes*

---

## Research Principles

### Academic Integrity (2026-03-10)
**All references must be real and verifiable, NO fabrication!**

**Must verify:**
- [ ] Does the textbook really exist?
- [ ] Is the author real?
- [ ] Is the publisher real?
- [ ] Is the publication year accurate?
- [ ] Is the curriculum standard officially published?
- [ ] Can the journal paper be found?
- [ ] Are volume and issue numbers accurate?
- [ ] Are page numbers accurate?

**Prioritize:**
- PEP textbooks: High school textbooks by People's Education Press
- Curriculum Standards: 2017 edition by Ministry of Education
- Classic works: Zhao Kaihua's "New Concept Physics", etc.

**If any item cannot be verified, delete the reference!**

---

## Output Format

**All task responses include:**
- `[Mode]` — Hardening/Optimization/Acceleration/Recovery
- `[North Star]` — X% → Y% (+Z%)
- `[Task]` + 验收标准 (≥5 项)
- `[不足]` — ≥5 个具体改进点
- `[下一步]` — ≥5 个可执行行动
- `[Verify]` — 验证结果

**Critic v5.0 Embedded Checks:**
- Pre-task design review (6 checkpoints)
- Mid-task progress check (every 30%)
- Post-task final review (10 checkpoints, ≥95 score to pass)

---

## Backlinks

- [FORMAT-001] Output Format Specification
- [AUTO-001] n8n Workflow Orchestration
- [DOC-001] Documentation System
- [SECURITY-001] Git Firewall Proxy
- [FEISHU-001] Message Queue System
- [SOUL] Core Identity Document
- [AGENTS] Workspace Conventions

---

**Note:** This is a quality-first curated version. Full details in:
- `SOUL.md` - Core identity and principles
- Daily notes
- Archive

**Next Auto-Distillation:** Sunday 05:00 AM (scheduled task)

**Quality Check:** All content verified against SOUL.md and daily notes ✅

## 2026-03-19 15:16 新增

### [workflow] ⭐5.0

工作流优化 Top 5 全部完成 - 平均效率提升 90

**标签:** 工作流，优化，Top5

---

### [tool] ⭐5.0

缓存机制实现 - 重复任务加速 90

**标签:** 缓存，性能，压缩

---

### [tool] ⭐4.0

异常检测系统 - 超时检测 + 自动重试 + 智能降级

**标签:** 异常，检测，自愈

---

### [workflow] ⭐4.0

错误恢复机制 - checkpoint 恢复 + 步骤重试

**标签:** 错误，恢复，重试

---

### [research] ⭐5.0

AI 智能体进化路线图 - 25 个创意，14 个五星

**标签:** AI, 进化，头脑风暴

---


## 2026-03-19 Auto-Distillation

**Source:** 1 days of daily notes
**Events:** 1 unique events extracted

- [2026-03-19] **Tasks:** 8 | **Time:** ~150min | **Git:** 10+

---
