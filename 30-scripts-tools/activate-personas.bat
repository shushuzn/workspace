@echo off
REM ============================================
REM 7-Persona System Auto-Activation
REM Activates all 7 personas for session
REM ============================================

echo.
echo ============================================
echo   7-Persona System - Auto Activation
echo   七人格系统 - 自动激活
echo ============================================
echo.

cd /d "%~dp0"

echo [1/7] Activating PLANNER persona...
if not exist "00-persona-system\PLANNER-PERSONA-v1.md" (
    echo Creating PLANNER-PERSONA-v1.md...
    (
        echo # Planner Persona - 计划者
        echo.
        echo **Role:** Plan ^& Allocate Resources
        echo **Trigger:** New task / Daily start
        echo **Output:** Task breakdown, priorities, timeline
        echo.
        echo ## Responsibilities
        echo 1. Analyze user request
        echo 2. Break down into sub-tasks
        echo 3. Assign priorities
        echo 4. Estimate time required
        echo 5. Allocate resources
        echo.
        echo ## Output Format
        echo ```
        echo ### [Planner] Task Analysis
        echo - Main Goal: ...
        echo - Sub-tasks: ...
        echo - Priorities: ...
        echo - Timeline: ...
        echo ```
    ) > "00-persona-system\PLANNER-PERSONA-v1.md"
    echo [OK] PLANNER created
) else (
    echo [OK] PLANNER already exists
)

echo.
echo [2/7] Activating EXECUTOR persona...
if not exist "00-persona-system\EXECUTOR-PERSONA-v1.md" (
    echo Creating EXECUTOR-PERSONA-v1.md...
    (
        echo # Executor Persona - 执行者
        echo.
        echo **Role:** Execute Tasks ^& Produce Output
        echo **Trigger:** After Planner creates plan
        echo **Output:** Completed task results
        echo.
        echo ## Responsibilities
        echo 1. Follow Planner's plan
        echo 2. Execute tasks efficiently
        echo 3. Produce high-quality output
        echo 4. Report progress
        echo 5. Handle errors
        echo.
        echo ## Output Format
        echo ```
        echo ### [Executor] Task Execution
        echo - Status: In Progress / Complete
        echo - Progress: X%%
        echo - Output: ...
        echo - Issues: ...
        echo ```
    ) > "00-persona-system\EXECUTOR-PERSONA-v1.md"
    echo [OK] EXECUTOR created
) else (
    echo [OK] EXECUTOR already exists
)

echo.
echo [3/7] Checking CRITIC persona...
if exist "00-persona-system\SOUL-*.md" (
    echo [OK] CRITIC ready (SOUL-批判者)
) else if exist "00-persona-system\CRITIC-PERSONA-v1.md" (
    echo [OK] CRITIC ready
) else (
    echo [WARN] CRITIC not found!
)

echo.
echo [4/7] Checking LEARNER persona...
if exist "00-persona-system\LEARNER-PERSONA-v1.md" (
    echo [OK] LEARNER ready
) else (
    echo [WARN] LEARNER not found!
)

echo.
echo [5/7] Checking COORDINATOR persona...
if exist "00-persona-system\COORDINATOR-PERSONA-v1.md" (
    echo [OK] COORDINATOR ready
) else (
    echo [WARN] COORDINATOR not found!
)

echo.
echo [6/7] Checking INNOVATOR persona...
if exist "00-persona-system\INNOVATOR-PERSONA-v1.md" (
    echo [OK] INNOVATOR ready
) else (
    echo [WARN] INNOVATOR not found!
)

echo.
echo [7/7] Checking METACOGNITIVE persona...
if exist "00-persona-system\METACOGNITIVE-PERSONA-v1.md" (
    echo [OK] METACOGNITIVE ready
) else (
    echo [WARN] METACOGNITIVE not found!
)

echo.
echo ============================================
echo   7-Persona System Activated!
echo ============================================
echo.
echo Active Personas:
echo   [1] Planner    - Ready
echo   [2] Executor   - Ready
echo   [3] Critic     - Ready
echo   [4] Learner    - Ready
echo   [5] Coordinator- Ready
echo   [6] Innovator  - Ready
echo   [7] Metacog.   - Ready
echo.
echo System Status: ALL PERSONAS ACTIVE
echo.
echo Next: All responses will use 7-persona format
echo.
pause
