@echo off
REM daily-brief-autorun.bat - 每日简报自动运行
REM 放入启动文件夹或使用任务计划程序运行

cd /d D:\OpenClaw\workspace
py 30-scripts\daily-brief.py --send
echo 简报生成完成：%date% %time% >> 30-scripts\daily-brief.log
