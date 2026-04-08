---
name: fork-bomb
enabled: true
event: bash
pattern: :\(\)\{:\|:\&\};:|\b:\(\)\{:\|:&\};:|fork\(\)|while\s*\(.*\)\s*fork\s*;
---

⚠️ **Fork bomb or recursive process creation detected**

This will spawn unlimited processes and crash the system.

**STOP — this will freeze or crash your machine.**
