---
name: git-clean-fd
enabled: true
event: bash
pattern: git\s+clean\s+.*-[fF][dD]
---

⚠️ **git clean -fd detected**

This command deletes untracked files permanently.

**Why dangerous:**
- Removes all untracked files (git clean -f) and directories (git clean -d)
- Cannot be undone — no git history for untracked files
- May delete generated files that should be preserved

**Safer alternatives:**
- Preview first: `git clean -n -fd` (dry run)
- Delete specific files manually
- Use `git stash` instead of clean
