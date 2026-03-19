@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace
git add -A
git commit -m "feat: arxiv brainstorm complete - 20 ideas from 10 papers, 10 dimensions, top 5 priorities identified"
git push origin master
echo Done!
