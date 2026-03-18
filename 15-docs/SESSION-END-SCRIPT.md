# Session End Script - One-Click Workflow

**Version:** 1.0  
**Date:** 2026-03-18  
**Location:** `30-scripts-tools/session_end.py`

---

## Overview

一键完成会话结束流程，将 5 个手动步骤压缩为 1 个命令。

**Before:**
```bash
# 5 manual steps
py 30-scripts-tools\post_session_compress.py --auto
py 30-scripts-tools\fast_load.py
# Check daily note lines manually
git add .
git commit -m "Message"
git push
```

**After:**
```bash
# 1 command
py 30-scripts-tools\session_end.py "Commit message"
```

---

## Usage

### Basic Usage

```bash
py 30-scripts-tools\session_end.py "Your commit message"
```

### Examples

```bash
# Simple message
py 30-scripts-tools\session_end.py "Memory Tag System complete"

# Multi-word message (automatically joined)
py 30-scripts-tools\session_end.py Session end script v1 - One-click workflow
```

---

## What It Does

### 7 Automated Steps

| Step | Action | Critical |
|------|--------|----------|
| 1 | Run `post_session_compress.py --auto` | ✅ Yes |
| 2 | Verify context size <100KB | No |
| 3 | Check daily note <100 lines | No |
| 4 | Show git status | No |
| 5 | Run `git add .` | No |
| 6 | Run `git commit -m "..."` | ✅ Yes |
| 7 | Run `git push` | ✅ Yes |

### Critical Steps

If any critical step fails (1, 6, 7), the script exits with code 1.

Non-critical steps (2-5) show warnings but don't block completion.

---

## Output Example

```
============================================================
SESSION END - One-Click Workflow
============================================================

Time: 2026-03-18 17:28:00
ℹ️  Commit message: "Memory Tag System complete"

============================================================
STEP 1: Session Compression
============================================================

ℹ️  Running session compression...
   Command: py 30-scripts-tools\post_session_compress.py --auto
✅ Running session compression - OK

============================================================
STEP 2: Context Size Verification
============================================================

ℹ️  Verifying context size...
   ✅ SOUL.md: 12.8KB
   ✅ USER.md: 10.6KB
   ✅ AGENTS.md: 11.3KB
   ✅ TOOLS.md: 5.7KB
   ✅ HEARTBEAT.md: 5.6KB
   ✅ 13-memory/MEMORY.md: 9.2KB
   ✅ 13-memory/2026-03-18.md: 2.9KB
   总大小：58.2KB (0.06MB)
✅ Context size OK (<100KB)

============================================================
STEP 3: Daily Note Check
============================================================

ℹ️  Checking daily note lines...
   13-memory\2026-03-18.md: 97 lines
✅ Daily note lines OK (97 < 100)

============================================================
STEP 4: Git Status
============================================================

ℹ️  Checking git status...
   2 file(s) to commit:
   A  30-scripts-tools/session_end.py
   A  30-scripts-tools/critic-auto-session-end-script.json

============================================================
STEP 5: Git Add
============================================================

ℹ️  Adding files to git...
   Command: git add .
✅ Adding files to git - OK

============================================================
STEP 6: Git Commit
============================================================

ℹ️  Committing changes...
   Command: git commit -m "Memory Tag System complete"
✅ Committing changes - OK
   [master da25e13] Memory Tag System complete
    2 files changed, 100 insertions(+)

============================================================
STEP 7: Git Push
============================================================

ℹ️  Pushing to remote...
   Command: git push
✅ Pushing to remote - OK

============================================================
SESSION END SUMMARY
============================================================

Passed: 7/7
  ✅ Session Compress: PASS
  ✅ Context Check: PASS
  ✅ Daily Note Check: PASS
  ✅ Git Status: PASS
  ✅ Git Add: PASS
  ✅ Git Commit: PASS
  ✅ Git Push: PASS

============================================================
FINAL VERDICT
============================================================

✅ SESSION END COMPLETE
ℹ️  All critical steps passed
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All critical steps passed |
| 1 | One or more critical steps failed |

---

## Error Handling

### Windows Encoding

Script automatically sets UTF-8 encoding for Windows PowerShell.

### Git Commit Message

Script uses subprocess list form to avoid shell escaping issues with commit messages.

### Timeout

All commands have 60-second timeout (30s for verification steps).

---

## Integration

### With Auto-Critic

Recommended workflow:

```bash
# 1. Start task with critic
py 30-scripts-tools\auto-critic.py -t "Task-Name" -p start

# 2. Do your work...

# 3. Final critic review
py 30-scripts-tools\auto-critic.py -t "Task-Name" -p final

# 4. Complete critic checklist (edit JSON)

# 5. End session
py 30-scripts-tools\session_end.py "Task-Name complete with critic review"
```

### With Post-Session Compress

`session_end.py` automatically calls `post_session_compress.py --auto` in Step 1.

No need to run separately.

---

## Troubleshooting

### Git Push Fails

**Cause:** Remote has commits you don't have locally.

**Solution:**
```bash
git pull --rebase
git push
```

### Daily Note Too Long

**Warning:** `Daily note too long (150 >= 100 lines)`

**Solution:** Manually compress daily note before running `session_end.py`:
- Remove redundant session summaries
- Keep only key decisions and lessons
- Target <100 lines

### Context Size Exceeds 100KB

**Warning:** `Context size may exceed 100KB`

**Solution:**
- Check `fast_load.py` output for large files
- Compress MEMORY.md if needed
- Ensure daily note is compressed

---

## Performance

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Commands | 5-6 | 1 | 83% reduction |
| Time | ~2 min | ~25 sec | 79% savings |
| Error Risk | Medium | Low | Automated checks |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-18 | Initial release |

---

## Related Documents

- `USER-004` - Critic and tool usage requirements
- `AGENTS.md` - Session compression requirements
- `15-docs/ZERO-SCORE-ITEMS.md` - Zero-score items reference
- `30-scripts-tools/auto-critic.py` - Auto-critic tool
- `30-scripts-tools/post_session_compress.py` - Session compression

---

**Created by:** Claw  
**License:** Part of OpenClaw workspace
