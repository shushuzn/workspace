@echo off
chcp 65001 >nul
title Set Cursor as Default

echo Setting Cursor as default for code files...
echo.

:: Python
ftype Cursor.py="D:\cursor\resources\cursor.exe" "%%1"
assoc .py=Cursor.py
echo [OK] .py

:: JavaScript
ftype Cursor.js="D:\cursor\resources\cursor.exe" "%%1"
assoc .js=Cursor.js
echo [OK] .js

:: TypeScript
ftype Cursor.ts="D:\cursor\resources\cursor.exe" "%%1"
assoc .ts=Cursor.ts
echo [OK] .ts

:: HTML
ftype Cursor.html="D:\cursor\resources\cursor.exe" "%%1"
assoc .html=Cursor.html
echo [OK] .html

:: CSS
ftype Cursor.css="D:\cursor\resources\cursor.exe" "%%1"
assoc .css=Cursor.css
echo [OK] .css

:: JSON
ftype Cursor.json="D:\cursor\resources\cursor.exe" "%%1"
assoc .json=Cursor.json
echo [OK] .json

:: Markdown
ftype Cursor.md="D:\cursor\resources\cursor.exe" "%%1"
assoc .md=Cursor.md
echo [OK] .md

echo.
echo Done! Double-click any code file to open in Cursor.
pause
