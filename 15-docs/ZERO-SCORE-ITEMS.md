# Zero-Score Items Reference Card

**Version:** 1.1 - Evidence Required + Workspace Check  
**Date:** 2026-03-18  
**Priority:** CRITICAL

---

## 🚨 Zero-Score Items (7 Items)

**Failure on ANY = 0/100 Total Score**

These are non-negotiable. No exceptions.

---

### 1. 【USER-004】批判者自动调用

**Requirement:** Critic must be auto-invoked at task start

**Failure Case:**
- Date: 2026-03-18
- Task: Memory Tag System
- Issue: Manual critic review instead of auto-critic.py
- Score: 0/100

**Prevention:**
```bash
# At task START (not end!)
py 30-scripts-tools\auto-critic.py -t "Task-Name" -p start
```

**Verification:**
- [ ] auto-critic.py invoked at task start
- [ ] critic-auto-*.json file created
- [ ] Review completed before task end

**Evidence Required:**
```json
{
  "item": "【USER-004】批判者自动调用 (不能手动补审)",
  "checked": true,
  "notes": "auto-critic.py 在任务开始时自动调用",
  "evidence": "critic-auto-task-name.json created at 2026-03-18T17:00:00"
}
```

---

### 2. 【USER-004】工具创建了必须使用

**Requirement:** Tools must be used immediately after creation

**Failure Case:**
- Date: 2026-03-18
- Task: Memory Tag System
- Issue: Created memory_tag_search.py but never used
- Score: 0/100

**Prevention:**
```bash
# Create → Use → Verify workflow
py 30-scripts-tools\memory_tag_search.py --tag critical  # Use immediately
py 30-scripts-tools\memory_tag_search.py --tag lesson   # Multiple uses
```

**Verification:**
- [ ] Tool used ≥1 time in real workflow
- [ ] Usage evidence documented (search results, output)
- [ ] Value quantified (time saved, efficiency gain)

**Evidence Required:**
```json
{
  "item": "【USER-004】工具创建了必须使用 (创建→使用→验证)",
  "checked": true,
  "notes": "工具创建后测试 3 次，93% 时间节省",
  "evidence": "Command output: py memory_tag_search.py --tag critical (9 results)"
}
```

---

### 3. 【AGENTS.md】当日笔记压缩

**Requirement:** Daily note must be <100 lines

**Failure Case:**
- Date: 2026-03-18
- Task: Multiple sessions
- Issue: 2026-03-18.md had 260 lines
- Score: 0/100

**Prevention:**
```bash
# Check line count
py -c "print(len(open('13-memory/2026-03-18.md').readlines()))"

# Compress if needed
# Remove redundant session summaries
# Keep only key decisions and lessons
```

**Verification:**
- [ ] Daily note lines <100
- [ ] Removed redundant session summaries
- [ ] Kept key decisions and critic reviews

**Evidence Required:**
```json
{
  "item": "【AGENTS.md】当日笔记压缩 (<100 行)",
  "checked": true,
  "notes": "97 行 < 100 行",
  "evidence": "Line count: 97 (verified by session_end.py)"
}
```

---

### 4. 【AGENTS.md】会话压缩执行

**Requirement:** post_session_compress.py must run at session end

**Failure Case:**
- Date: 2026-03-18
- Task: Multiple sessions
- Issue: post_session_compress.py not run
- Score: 0/100

**Prevention:**
```bash
# At EVERY session end (without exception)
py 30-scripts-tools\post_session_compress.py --auto
```

**Verification:**
- [ ] post_session_compress.py executed
- [ ] Session summary added to daily note
- [ ] Temp file cleaned up

**Evidence Required:**
```json
{
  "item": "【AGENTS.md】会话压缩执行 (post_session_compress.py --auto)",
  "checked": true,
  "notes": "会话压缩自动执行",
  "evidence": "session_end.py Step 1 output: Running session compression - OK"
}
```

---

### 5. 【AGENTS.md】上下文大小验证

**Requirement:** Context size must be <100KB

**Failure Case:**
- Date: 2026-03-18
- Task: Multiple sessions
- Issue: Context >100KB without compression
- Score: 0/100

**Prevention:**
```bash
# Check context size
py 30-scripts-tools\fast_load.py

# Expected output:
# 总大小：58.2KB (<100KB ✅)
# 速度提升：9836x
```

**Verification:**
- [ ] Context size <100KB
- [ ] Speed improvement >5000x
- [ ] All 7 core files loaded

**Evidence Required:**
```json
{
  "item": "【AGENTS.md】上下文大小验证 (<100KB)",
  "checked": true,
  "notes": "58.2KB < 100KB",
  "evidence": "fast_load.py output: 总大小：58.2KB (0.06MB)"
}
```

---

### 6. 【USER-001】工作区正确性 (NEW!)

**Requirement:** Must work in D:\OpenClaw\workspace, NOT C:

**Failure Case:**
- Date: 2026-03-18
- Task: Multiple tools
- Issue: Created files in C:\Users\华为\.copaw\workspaces\default
- Score: 0/100

**Prevention:**
```bash
# Always start with correct workspace
cd /d D:\OpenClaw\workspace

# Verify before working
py -c "import os; print('OK' if 'OpenClaw' in os.getcwd() else 'WRONG!')"
```

**Verification:**
- [ ] Current directory contains "OpenClaw"
- [ ] No files created in C: drive
- [ ] All paths use D:\OpenClaw\workspace

**Evidence Required:**
```json
{
  "item": "【USER-001】工作区正确性 (D:\\OpenClaw\\workspace, C 盘=0 分)",
  "checked": true,
  "notes": "工作区验证通过",
  "evidence": "os.getcwd(): D:\\OpenClaw\\workspace"
}
```

**Auto-Check:** auto-critic.py now blocks execution if wrong workspace detected!

---

### 7. 【USER-004】检查项必须有证据 (NEW!)

**Requirement:** Every checklist item must have evidence, no blind checking

**Failure Case:**
- Date: 2026-03-18
- Task: Multiple
- Issue: Checked items without proof (mechanical checking)
- Score: 0/100

**Prevention:**
```json
// In critic-auto-*.json, EVERY item must have:
{
  "item": "...",
  "checked": true,
  "notes": "Description",
  "evidence": "PROOF HERE (command/output/screenshot/path)"
}
```

**Verification:**
- [ ] All checked items have non-empty "evidence" field
- [ ] Evidence is specific (not "done" or "ok")
- [ ] Evidence is verifiable (commands, outputs, file paths)

**Evidence Required:**
```json
{
  "item": "【USER-004】检查项必须有证据 (无证据=0 分)",
  "checked": true,
  "notes": "所有检查项已附证据",
  "evidence": "critic-auto-*.json: all 17 items have evidence field filled"
}
```

**Evidence Quality Standards:**

| Quality | Example | Acceptable |
|---------|---------|------------|
| ❌ Bad | "done" | No |
| ❌ Bad | "ok" | No |
| ❌ Bad | "checked" | No |
| ✅ Good | "Command: py fast_load.py → 58.2KB" | Yes |
| ✅ Good | "File: 13-memory/2026-03-18.md (97 lines)" | Yes |
| ✅ Good | "Git: commit a3f7c2d pushed to origin" | Yes |

---

## Quick Checklist (Print This)

### Before Task Start
- [ ] Run auto-critic.py -p start
- [ ] Review pre_task checklist

### During Task
- [ ] Use tools immediately after creation
- [ ] Document usage evidence

### Before Task End
- [ ] Run auto-critic.py -p final
- [ ] Complete ALL zero-score items
- [ ] Verify daily note <100 lines

### At Session End
- [ ] Run post_session_compress.py --auto
- [ ] Run fast_load.py to verify <100KB
- [ ] Git commit + push

---

## Scoring Impact

| Zero-Score Items Passed | Other Items | Final Score |
|-------------------------|-------------|-------------|
| ❌ Any failed | Any | **0/100** |
| ✅ All passed | ≥95% | 95-100/100 |
| ✅ All passed | 85-94% | 85-94/100 |
| ✅ All passed | 70-84% | 70-84/100 |
| ✅ All passed | <70% | <70/100 |

**Rule:** Zero-score items are gatekeepers. Must pass first.

---

## Historical Context

### 2026-03-18: The Day of Zero Scores

**What Happened:**
1. Created Memory Tag System tools
2. Did NOT use tools (0 usage) → 0/100
3. Did NOT auto-invoke critic (manual review) → 0/100
4. Did NOT compress daily note (260 lines) → 0/100
5. Did NOT run session compression → 0/100

**Recovery:**
- Created auto-critic.py for auto-invocation
- Used tools 3 times with evidence (93% time saved)
- Compressed daily note to 39 lines
- Ran post_session_compress.py --auto
- Verified context 58.2KB (<100KB)

**Lesson:** These 5 items are now permanently embedded in auto-critic.py

---

## Related Documents

- `USER-004` - Critic and tool usage requirements
- `AGENTS.md` - Session compression requirements
- `15-docs/CRITIC-V5-UNIVERSAL.md` - Full critic documentation
- `30-scripts-tools/auto-critic.py` - Auto-critic implementation

---

**Remember:** "零分项未通过 = 总分 0 分"

**Print this card. Keep it visible. Check every task.**
