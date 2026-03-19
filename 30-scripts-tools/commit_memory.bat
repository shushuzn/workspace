@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: long-term memory system - cross-session persistent memory

- Add long_term_memory.py (19.4KB) - memory system implementation
- Add memory database: 13-memory/memory-db.json
- Add memory config: 13-memory/memory-config.json
- Add memory index: 13-memory/memory-index.json
- Features:
  - Cross-session persistent memory storage
  - Memory search and association
  - Category and tag classification
  - Memory compression and distillation
  - Query API (CLI + Python)
- 5 sample memories added
- Categories: workflow, tool, research
- Brainstorm priority #1 implementation
"
git push origin master
