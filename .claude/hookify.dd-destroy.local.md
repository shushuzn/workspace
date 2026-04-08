---
name: dd-destroy
enabled: true
event: bash
pattern: dd\s+.*if=.*of=
---

⚠️ **dd with input/output files detected**

Direct disk operations can permanently destroy data.

**Why dangerous:**
- `dd` bypasses all safety checks
- Wrong device = complete data loss
- No confirmation prompts

**Safer alternatives:**
- Use `cp` or `rsync` for file copies
- Use disk imaging tools with verification
