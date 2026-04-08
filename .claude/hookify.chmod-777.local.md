---
name: chmod-777
enabled: true
event: bash
pattern: chmod\s+.*777
---

⚠️ **chmod -R 777 detected**

World-writable permissions on files or directories.

**Why dangerous:**
- Makes files executable by anyone
- Security risk — any user can modify
- Common target for malware

**Safer alternatives:**
- `chmod 755` for directories
- `chmod 644` for files
- `chmod 600` for sensitive files
