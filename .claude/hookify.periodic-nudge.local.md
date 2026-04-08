---
name: periodic-nudge
enabled: false
event: bash
pattern: .
action: allow
---

```bash
# PostToolUse: check if nudge should fire
node D:/OpenClaw/workspace/.omc/scripts/hook-nudge.mjs --check
```
