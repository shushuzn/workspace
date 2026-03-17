@echo off
echo === Downloading summarize ===
echo.

REM Create bin directory
echo Creating bin directory...
if not exist "%USERPROFILE%\bin" mkdir "%USERPROFILE%\bin"

REM Download summarize
echo Downloading summarize...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/steipete/summarize/releases/latest/download/summarize-windows-amd64.exe' -OutFile '%USERPROFILE%\bin\summarize.exe' -UseBasicParsing"

REM Verify
echo.
echo Verifying summarize...
"%USERPROFILE%\bin\summarize.exe" --version

echo.
echo === Installation Complete ===
echo.
echo Adding to PATH...
echo Please run this command to add to PATH:
echo setx PATH "%%PATH%%;%USERPROFILE%%\bin"
echo.
echo Then close and reopen PowerShell
echo.
pause
