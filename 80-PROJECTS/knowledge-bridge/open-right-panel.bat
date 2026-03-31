@echo off
REM Open Knowledge Graph Panel on the RIGHT side in Windows Terminal
REM Run this from Windows Terminal (PowerShell or CMD)

cd /d D:\OpenClaw\workspace\80-PROJECTS\knowledge-bridge

REM Open a new tab running the knowledge graph with auto-refresh
wt new-tab --title "PLA Knowledge Bridge" node terminalView.js
