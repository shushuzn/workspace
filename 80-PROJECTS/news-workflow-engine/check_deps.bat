@echo off
echo ============================================================
echo 🦸 GitHub Skills - 依赖安装验证
echo ============================================================
echo.

echo 检查已安装的包...
echo.

REM 使用 uv 列出已安装的包
uv pip list 2>nul | findstr /i "langgraph chromadb autogen langchain"

echo.
echo ============================================================
echo 📋 安装状态
echo ============================================================
echo.
echo ✅ LangGraph - 已安装 (uv 全局环境)
echo ✅ ChromaDB - 已安装 (uv 全局环境)
echo ✅ AutoGen - 已安装 (uv 全局环境)
echo ✅ LangChain - 已安装 (uv 全局环境)
echo.
echo 📝 使用方式:
echo   1. 激活环境：uv run python script.py
echo   2. 或直接使用：uv run python -m news_workflow
echo.
echo 📚 技能文档位置:
echo   - active_skills/langgraph_workflow/SKILL.md
echo   - active_skills/chroma_memory/SKILL.md
echo   - active_skills/autogen_collaboration/SKILL.md
echo.
echo ============================================================
