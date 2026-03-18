@echo off
echo === Installing blogwatcher ===
echo.

REM Check Go
echo Checking Go...
go version
if %errorlevel% neq 0 (
    echo Go not found! Please install from https://go.dev/dl/
    pause
    exit /b 1
)

REM Install blogwatcher
echo.
echo Installing blogwatcher...
go install github.com/Hyaxia/blogwatcher/cmd/blogwatcher@latest

REM Verify
echo.
echo Verifying blogwatcher...
blogwatcher --version

REM Add subscriptions
echo.
echo Adding blog subscriptions...
blogwatcher add "Andrej Karpathy" https://karpathy.ai/feed.xml
blogwatcher add "OpenAI Blog" https://openai.com/blog/rss/
blogwatcher add "Anthropic" https://www.anthropic.com/news/rss

REM Test scan
echo.
echo Testing scan...
blogwatcher scan

echo.
echo === Installation Complete ===
echo.
echo Next: Download summarize from https://github.com/steipete/summarize/releases
pause
