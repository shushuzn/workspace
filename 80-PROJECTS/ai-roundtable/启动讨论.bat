@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

:: Clear proxy env vars to try direct connection first
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=

node index.js %*
pause
