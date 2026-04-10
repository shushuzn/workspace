---
name: git-dirty-check
enabled: true
event: bash
pattern: git\s+(?:push|merge|reset|rebase|checkout\s+-b|stash\s+drop)
---

⚠️ **git operation on potentially dirty workspace**

Running: $&
Shared workspace has uncommitted changes — this may affect other agents.

**Why check first:**
- Prevents work loss across agents
- Keeps commit history clean
- Avoids merge conflicts

**Run check:**
```
node shared/check-git-dirty.mjs
```

**Safer alternatives:**
- `git stash` before operation
- Commit your changes first
- Use `git status` to review
