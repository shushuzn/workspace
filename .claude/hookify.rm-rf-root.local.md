---
name: rm-rf-root
enabled: true
event: bash
pattern: rm\s+-rf\s+/|rm\s+-rf\s+root
---

⚠️ **rm -rf / or root detected**

This command attempts to delete the entire filesystem.

**This will destroy your system.**

**STOP — do not proceed.**
