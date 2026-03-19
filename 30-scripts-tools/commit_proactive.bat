@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: proactive interaction system - brainstorm priority #3

- proactive_agent.py (23.1KB, 650+ lines)
- 5 core features: reminders, suggestions, alerts, context, learning
- Command-line and interactive menu modes
- Quiet hours protection
- User behavior learning system
- Brainstorm implementation: 4/5 (80%%) complete
"
git push origin master
