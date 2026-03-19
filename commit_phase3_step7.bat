@echo off
chcp 65001 >nul
cd /d D:\OpenClaw\workspace

echo ============================================================
echo 📦 Git 提交 - 速度优化 Phase 3 完成
echo ============================================================

git add -A

git commit -m "feat: speed optimization phase 3 complete - final summary and guide created - 6/12 steps done"

git push origin master

echo.
echo ============================================================
echo ✅ Git 提交完成!
echo ============================================================
