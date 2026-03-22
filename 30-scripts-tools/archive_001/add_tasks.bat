@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\OpenClaw\workspace
py 30-scripts-tools\task_decomposer.py --decompose "开发 AI 智能体多模态理解功能" --template development --priority urgent
py 30-scripts-tools\task_decomposer.py --decompose "撰写工作流优化技术报告" --template writing --priority important
py 30-scripts-tools\task_decomposer.py --decompose "研究多智能体协作架构" --template research --priority important
pause
