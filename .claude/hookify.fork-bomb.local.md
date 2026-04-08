---
name: fork-bomb
enabled: true
event: bash
pattern: :\(\)\s*\{\s*:\|:&\s*\}\s*;:\s*:?&|while\s+:\s*;\s*do\s+:\s*;\s*done\s*&
---

⚠️ **Fork bomb or recursive process creation detected**

This will spawn unlimited processes and crash the system.

**STOP — this will freeze or crash your machine.**
