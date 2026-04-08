---
name: git-push-force
enabled: true
event: bash
pattern: git\s+push\s+.*--force|git\s+push\s+.*-f\s
---

⚠️ **git push --force detected**

Force-pushing rewrites remote history.

**Why dangerous:**
- Overwrites remote branch history
- Can destroy teammates' commits
- Violates collaboration norms

**Safer alternatives:**
- `git push --force-with-lease` — safer force push
- Use pull requests instead of direct pushes
- Discuss with team before force-pushing
