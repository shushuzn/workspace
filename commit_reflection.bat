@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add flow-archive/20260318-universal-workflow-001/REFLECTION-QUALITY-OVER-QUANTITY.md
git commit -m "docs: add reflection report - quality over quantity principle"
git push origin master
echo Done!
