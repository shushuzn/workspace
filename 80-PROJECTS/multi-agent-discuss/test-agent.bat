@echo off
cd /d D:\OpenClaw\workspace\80-PROJECTS\multi-agent-discuss
D:\Go\bin\go.exe run ./cmd/agent/main.go run --name %1 --port %2
