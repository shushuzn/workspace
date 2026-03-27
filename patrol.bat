@echo off
cd /d "%~dp0"
echo Starting patrol agent...
nohup node .omc/patrol-agent/src/index.js > .omc/patrol.log 2>&1 &
echo Patrol agent started in background. See .omc/patrol.log for output.
pause
