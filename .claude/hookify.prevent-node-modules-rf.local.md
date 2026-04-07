---
name: prevent-node-modules-rf
enabled: true
event: bash
pattern: rm\s+-rf\s+.*node_modules
---

**Danger: `rm -rf` on node_modules detected**

This command would permanently destroy your dependencies and node_modules cannot be recovered from git.

**If you meant to delete node_modules for a clean reinstall:**
- Run `npm install` (or `pnpm install` / `yarn`) to reinstall
- Use `rm -rf node_modules` without the `-rf` flags if you want a prompt

**If you're in a subdirectory and meant to delete that directory's node_modules:**
- Navigate to the correct directory first
- Never use `rm -rf` on node_modules anywhere in the workspace
