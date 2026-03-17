@echo off
REM Example: Task with Feishu Notification
REM Usage: example_task_with_notification.bat

cd /d D:\OpenClaw\workspace\30-scripts-tools\feishu-tools

echo ========================================
echo Running Example Task...
echo ========================================

REM Your task logic here (replace with actual task)
echo [Task] Processing...
timeout /t 2 /nobreak >nul
echo [Task] Complete!

REM Check exit code and send notification
if %ERRORLEVEL% EQU 0 (
    echo [Notification] Sending success message...
    python cron_notification.py "Example Task" "success" "Task completed successfully at %DATE% %TIME%"
) else (
    echo [Notification] Sending failure message...
    python cron_notification.py "Example Task" "failed" "Task failed with exit code: %ERRORLEVEL%"
)

echo ========================================
echo Done!
echo ========================================
