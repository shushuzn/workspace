@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "docs: long-term memory system completion report

- Add LONG-TERM-MEMORY-COMPLETION.md
- 5 memories added
- Brainstorm priority #1 implemented
"
git push origin master
