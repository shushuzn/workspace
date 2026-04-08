---
name: auto-seed-generator
enabled: true
event: bash
pattern: .
action: allow
---

```bash
# PostToolUse: increment tool call counter
# Fires on every bash command, triggering the seed auto-creation at threshold.
node D:/OpenClaw/workspace/.omc/scripts/hook-auto-seed.mjs --check
```
