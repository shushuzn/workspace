---
name: git-reset-hard
enabled: true
event: bash
pattern: git\s+reset\s+.*--hard
---

⚠️ **git reset --hard detected**

This command rewrites history and destroys uncommitted changes.

**Why dangerous:**
- Discards all uncommitted changes
- Rewrites commit history (dangerous on shared branches)
- Cannot be undone without reflog

**Safer alternatives:**
- `git stash` — save changes temporarily
- `git reset --soft` — keep changes staged
- `git reset --mixed` — keep changes unstaged
