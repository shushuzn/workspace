@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d D:\OpenClaw\workspace
py 30-scripts-tools\long_term_memory.py --add "工作流优化 Top 5 全部完成 - 平均效率提升 90%" --category "workflow" --tags "工作流，优化，Top5" --importance 5
py 30-scripts-tools\long_term_memory.py --add "缓存机制实现 - 重复任务加速 90%, gzip 压缩 60-80%%" --category "tool" --tags "缓存，性能，压缩" --importance 5
py 30-scripts-tools\long_term_memory.py --add "异常检测系统 - 超时检测 + 自动重试 + 智能降级" --category "tool" --tags "异常，检测，自愈" --importance 4
py 30-scripts-tools\long_term_memory.py --add "错误恢复机制 - checkpoint 恢复 + 步骤重试" --category "workflow" --tags "错误，恢复，重试" --importance 4
py 30-scripts-tools\long_term_memory.py --add "AI 智能体进化路线图 - 25 个创意，14 个五星" --category "research" --tags "AI, 进化，头脑风暴" --importance 5
pause
