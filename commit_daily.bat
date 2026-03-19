@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add 13-memory/2026-03-20.md flow-archive/20260318-universal-workflow-001/WEEK2-NAMING-SUBDIVISION-COMPLETE.md
git commit -m "docs: Week 2 complete - naming and subdivision"
git push origin master
echo Done!
