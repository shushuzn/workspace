## Insights from 2026-04-08 session

### 1. Hook Responsibility Boundary ✅ EXECUTED
**Rule**: hooks = collect + store only; agent generates insights
**Violation fixed**: hook-mcp-consumer once called Ollama → removed
**Key**: no LLM calls in hooks, ever

### 2. Deduplication Required for Audit Spam ✅ EXECUTED
**Problem**: `ls 34~50` (16 calls at 20ms intervals) flooded audit log
**Fix**: 500ms dedup window in hook-audit-log-mcp
**Pattern**: debug loops can generate rapid repeated commands

### 3. Modern JSONL Uses tool_use Blocks ✅ EXECUTED
**Problem**: trajectory extractor used text regex for tool names
**Fix**: parse `type: 'tool_use'` blocks with `.name` field
**Format**: modern Claude Code JSONL has array content with block types

### 4. Workflow Consolidation Opportunity ✅ EXECUTED
**Observation**: Bash→Bash→Bash pattern occurs 56× in single session
**Root cause**: diagnostic scripts run --stats + read queue + --emit in sequence
**Fix**: `omc-diagnose.mjs` 合并了三个诊断命令为一条

### 5. Agent is the Analysis Engine ✅ EXECUTED
**Principle**: I am responsible for generating insights, not external LLMs
**Wrong pattern**: hook calling MiniMax/Ollama for insight generation
**Correct pattern**: hook stores raw data → drain → next session agent analyzes

### 6. Hook问题需要明确的验证反馈 ✅ EXECUTED
**Observation**: session 899884e0中用户反复问"hook启用了吗"共106次
**Root cause**: hook状态不透明，用户无法从行为感知hook是否工作
**Fix**: drain文件现在包含Hook Status段落（entries today、tools、dedup、queue depth）
**Result**: 下个session用户可从drain文件直接看到hook活跃状态

### 7. 大型调试session的特征 ✅ EXECUTED
**Data**: 1419次工具调用，857次Bash（60%），191次Read，129次Edit
**Pattern**: Read+Edit+Bash密集混合，说明在修复而非创造
**Fix**: trajectory现在检测Bash>30 + Read>20 + Edit>10 + 0 seeds → 标记为"debugging mode"

### 8. MCP Tool不可用时用文件替代 ✅ EXECUTED
**Problem**: `agentdb_pattern-store` 和 `memory_store` 均报 "Cannot read properties of null (reading 'model')"，AgentDB bridge 初始化失败
**Root cause**: MCP server 本身的 AgentDB 层崩溃，不是 hook 的问题
**Fix**: step4 直接写 `agentdb-patterns.jsonl`，不再通过 MCP tool；`buildInjectMarkdown` 改为直接确认存储而非调用工具
**Pattern**: 依赖第三方 MCP 服务时，fallback 方案必须是文件，不应假设服务始终可用

### 9. Edit工具遇到复杂字符串时代码被转义破坏 ✅ EXECUTED
**Problem**: 多次遇到 Edit 工具失效——旧字符串匹配失败，或替换后代码中出现 `\n`、`\`` 等转义序列
**Root cause**: JS 模板字符串内的模板字符串需要双转义；bash heredoc `$()` 会被 shell 展开；Node.js -e 的字符串在 Windows CRLF 下行为异常
**Fix**: 写 `.js` 或 `.mjs` 文件用 fs.readFileSync/writeFileSync 替代 Edit 工具处理复杂字符串替换；避免 heredoc 和 -e 字符串
**Pattern**: 复杂字符串替换优先用脚本文件，Edit 工具仅适用于简单单行或已知格式内容
### 10. Heavy bash usage detected [auto-generated]
**Observation**: Bash calls (11) in session — review if commands can be consolidated
**Rule**: Track this pattern in future sessions





### 11. Heavy bash usage detected [auto-generated]
**Observation**: Bash calls (26) in session — review if commands can be consolidated
**Rule**: Track this pattern in future sessions


### 14. Zero-Seed Production Despite 55 Tool Calls [auto-generated]
**Observation**: 200 events, 55 tool calls, 4 user prompts — yet 0 seeds generated. Heavy Bash(26) + Read(13) + Write(9) workflow consumed the session with no idea output.
**Rule**: Every session that processes 4+ user prompts must produce at least 1 seed or explicitly document why none apply. Add seed output check to session-close checklist.

### 15. Grep Underutilization (1 call) Signals Reactive Not Preventive Debugging [auto-generated]
**Observation**: Only 1 Grep call across 55 tools. Heavy Bash(26) suggests debugging via command execution rather than code search/analysis. Likely chasing symptoms instead of finding root cause.
**Rule**: Before running Bash to debug, always Grep first to understand code structure. Target: minimum 3 Grep calls per debugging session.



### 16. 55工具调用却0 seeds——会话未留下任何可执行种子 [auto-generated]

**Observation**: 55次工具调用、4轮用户交互、200 events的session，ideas.md写入0条。工具产出完全丢失在临时对话中，无任何seed沉淀。

**Rule**: 任何超过20次工具调用的session，必须在结束时向`.omc/innovation/ideas.md`写入至少1条seed（哪怕是dormant低分项），将工作成果固化为可追踪资产。



### 17. Zero Seeds Despite Active Session [auto-generated]
**Observation**: Session had 55 tool calls across 4 user prompts (decent activity level) yet generated 0 seeds. The trajectory started with "为什么没有自动生成" (why wasn't it auto-generated) and ended with "你用子agent" — indicating the agent was debugging an automation failure and pivoted to subagent execution.
**Rule**: When session topic includes debugging missing automation ("为什么没有自动生成"), explicitly generate 1+ seeds from the root cause before closing the session.

### 18. Bash Dominates Over Edit (26 vs 6) [auto-generated]
**Observation**: Tool ratio Bash(26):Edit(6) = 4.3:1 shows heavy command execution rather than code authoring. Write(9) + Edit(6) = 15 file mutations total — low for 55 tool calls. Grep(1) confirms minimal codebase exploration.
**Rule**: Track Bash:Edit ratio; if >3:1 in non-debug sessions, pause and verify whether commands are substituting for actual code changes.



### 19. Bash占工具调用47%，读写比例失衡 [auto-generated]

**Observation**: 55次工具调用中Bash占26次(47%)，Read占13次(24%)，Write+Edit共15次(27%)，Grep仅1次(2%)。无任何seed生成记录。

**Rule**: 工具使用过度集中于Bash说明可能存在工具选择不当——用Bash执行文件操作而非专用工具。



### 20. Bash Dominates Over Edit — Manual Execution Over Code Changes [auto-generated]
**Observation**: 26 Bash calls vs only 6 Edit calls (ratio 4.3:1). High Bash with low Edit suggests executing commands manually rather than modifying source files directly.
**Rule**: Track Bash:Edit ratio per session; sustained ratio >3:1 indicates workflow gap.
**Fix**: N/A

### 21. 0 Seeds Despite 55 Tool Calls — Insight Generation Not Triggered [auto-generated]
**Observation**: 200 events, 55 tool calls, 4 user prompts, yet 0 seeds generated. The session was explicitly an "insight generator" but produced no seeds.
**Rule**: Session-type mismatch: insight-generator sessions must output seeds even if only 1.
**Fix**: N/A



### 22. Zero Seeds Despite 55 Tool Calls [auto-generated]

**Observation**: Session logged 55 tool calls across 4 user prompts yet generated 0 seeds. Heavy Bash (26) + file ops (28 combined Read/Write/Edit) consumed most effort without producing any actionable idea outputs.

**Rule**: Seed generation is a core workflow metric — any session >30 tool calls that produces 0 seeds indicates work is happening inside the system rather than growing the idea pipeline.



## Mid-Session Live Insight

### 1. Insight Generation Session Self-Parasitic Loop

**Observation**: The trajectory shows 0 tool calls, 0 seeds, 0 events logged, but 723 lines — indicating this insight generation prompt is feeding on itself in an echo loop with no actual tool execution occurring. The `omc-insight-generator.mjs` is likely being invoked without a working session context, producing no actionable output.

**Rule**: Track whether insight generation sessions are actually producing output vs. echo loops; insight generation that invokes itself recursively without execution is valueless.

**Fix**: N/A

## Mid-Session Live Insight

### 1. Zero seed generation despite 669 tool calls
**Observation**: Session recorded 669 tool calls across 2479 events with 728 user prompts, yet `seeds: 0` — no ideas were generated or recorded in the idea pool. This suggests the ideation/brainstorm phase was entirely skipped or suppressed.
**Rule**: Track seed count per session; any session with >200 tool calls and 0 seeds should trigger a brainstorm prompt in the next session start.
**Fix**: N/A

### 2. Bash dominates at 48.6% of all tool calls
**Observation**: Bash (325) accounts for 48.6% of all tool calls, far exceeding Read (140), Edit (86), Grep (65), and Write (24) combined. This indicates heavy reliance on shell commands rather than structured file operations.
**Rule**: High Bash ratio ( >40%) may indicate repetitive CLI invocations that could be abstracted into reusable scripts or tools.
**Fix**: N/A

### 3. Task management system entirely unused
**Observation**: `TaskCreate: 0` and `TaskUpdate: 0` across 669 tool calls — the task tracking system was never invoked despite a long, complex session with 2479 events.
**Rule**: Sessions exceeding 500 events without task operations are likely operating without structured task tracking, making progress harder to audit.
**Fix**: N/A

## Mid-Session Live Insight

### 1. Bash dominates session (49% of calls, zero task management)

**Observation**: 339 Bash calls out of 688 total tool calls (49.3% Bash ratio). Zero TaskCreate/TaskUpdate across 688 calls despite active state management. Top Bash commands are all read-only state inspection: `ls`, `wc -l`, `node --stats`, `cat`, `tail` — cycling through the same 10 state files repeatedly.

**Rule**: Track Bash ratio per session; if Bash > 40% of calls, suspect inspection loop or missing task discipline.

**Fix**: N/A (monitoring/tracking rule only — no single executable fix)

---

### 2. Repeated state file inspection cycle could be one script ✅ EXECUTED

**Observation**: The same 10 state inspection patterns repeat: `hook-audit.jsonl`, `mcp-learn-queue.jsonl`, `session-start-mcp-inject.md`, `sessions/` dir, workflow-detector, hook-test-rules, hook-self-improve --stats. All commands are read-only (ls, cat, tail, wc, node --stats).

**Rule**: If the same 3+ bash commands appear in topBash repeatedly, consider consolidating into a single status script.

**Fix**: Consolidate the repeated inspection cycle into `hook-stats.mjs` that reads all 6 state files in one pass and outputs a unified dashboard line. Replace the 10 separate bash commands with `node .omc/scripts/hook-stats.mjs`.

## Mid-Session Live Insight

### 1. Bash dominates workflow with zero task tracking
**Observation**: 349 Bash calls (50% of 699 total tools), but 0 TaskCreate and 0 TaskUpdate — all work is happening ad-hoc in shell with no task tracking discipline.
**Rule**: Track discrete work units as tasks; Bash-only workflows bypass OMC's task management.
**Fix**: N/A

### 2. Repeated state-inspection Bash commands suggest missing dashboard ✅ EXECUTED
**Observation**: Top Bash commands are all state-file inspection (`ls`, `wc`, `cat`, `tail`, `node hook-*.mjs --stats`) — same pattern repeats across 10 entries with minor variation. No consolidated view exists.
**Rule**: Repeated 3+ Bash commands with same structure = candidate for consolidation.
**Fix**: Create `.omc/scripts/hook-stats.mjs` dashboard combining `ls`, `wc`, `tail` checks into single runnable overview (already partially exists at `hook-stats.mjs` — verify it covers all 10 top commands and add any gaps).

### 3. Zero seeds generated despite high activity
**Observation**: 699 tool calls, 765 user prompts, 2619 lines — extremely active session — but seeds: 0. No seed generation occurred.
**Rule**: Active sessions should produce seeds; 0 seeds is a workflow failure signal.
**Fix**: N/A

## Mid-Session Live Insight

### 1. Repeated state-inspection Bash commands
**Observation**: Top 10 Bash commands are all state/script inspection commands reading `.omc/state/` files and running `hook-*.mjs --stats/--min-count`. These 10 commands appear to repeat 3+ times each session with slight flag variations, accounting for a significant portion of the 355 Bash calls.
**Rule**: Repeated state-inspection commands should be extracted into a single dashboard script rather than re-typed per session.
**Fix**: Create `hook-stats.mjs` (or extend existing) to run all 10 inspection commands and output a consolidated summary in one shot.

## Mid-Session Live Insight

### 1. State Inspection Overhead ✅ EXECUTED
**Problem**: 10 repeated `ls`/`cat`/`tail`/`node` commands inspecting the same `.omc/state/` files could be consolidated into one dashboard script.
**RootCause**: No unified state inspection script — each observation requires a separate Bash call to different files.
**Fix**: Write `.omc/scripts/hook-stats.mjs` (already exists per recent commit `7123817c`) to aggregate state; replace repeated topBash commands with single `node .omc/scripts/hook-stats.mjs` call.

### 2. Bash Dominance (50.7% of Tool Calls)
**Problem**: 361 Bash calls out of 712 total tool calls (50.7%) — highest tool category by far. Read (143) + Edit (88) + Grep (65) = 296 combined, still less than Bash alone.
**RootCause**: Mid-session debugging/investigation workflow uses Bash as primary exploration mechanism instead of structured tools.
**Fix**: N/A — this is a tracking rule; investigate whether high Bash% correlates with low seed output in future sessions.

### 3. Zero Seeds in High-Activity Session
**Problem**: 712 tool calls, 779 user prompts, 0 seeds generated. Session was extremely active but produced no innovation pipeline output.
**RootCause**: Brainstorm is stopped per CLAUDE.md; no active seed generation mechanism in this session type.
**Fix**: N/A — this is expected given brainstorm cessation; track as baseline metric.

## Mid-Session Live Insight

### 1. OMC state inspection commands are fragmented ✅ EXECUTED
**Problem**: The top 10 Bash commands all inspect OMC state files (hook-audit.jsonl, mcp-learn-queue.jsonl, sessions, stats) using separate tools (`ls`, `wc`, `cat`, `tail`, `node --stats/--min-count`). No unified status dashboard exists.
**RootCause**: OMC lacks a single `omc status` or `hook-stats.mjs` command that consolidates all state inspections into one view.
**Fix**: Extend `hook-stats.mjs` to accept sub-commands or flags (e.g., `hook-stats.mjs --audit --queue --sessions`) instead of requiring separate Bash calls for each data source.

### 2. Zero seeds despite 717 tool calls
**Problem**: `seeds: 0` indicates no seed generation occurred in this session, even though 717 tool calls were executed with active workflow (784 user prompts).
**RootCause**: The session was entirely operational/maintenance (self-improvement hooks, state monitoring) with no creative ideation phase. This is expected for a pure maintenance session but should be noted.
**Fix**: N/A — this is a tracking observation, not an executable fix.

### 3. Task management completely unused
**Problem**: `TaskCreate: 0` and `TaskUpdate: 0` across 717 tool calls, meaning no task tracking was used despite complex multi-step operations.
**RootCause**: OMC self-improvement workflow runs as monolithic script invocations rather than decomposed tasks with explicit tracking.
**Fix**: N/A — task management may be intentionally unused for this workflow type (script-based rather than project-based work).

## Mid-Session Live Insight

### 1. State inspection commands fragmented across 10+ bash calls ✅ EXECUTED
**Observation**: topBash shows 10 distinct inspection commands (ls/wc/cat/tail/node for hook-audit, mcp-learn-queue, sessions, session-start-mcp-inject, jsonl files). These could be one `omc-status.mjs` script.
**Rule**: Fragmented inspection → consolidate into unified status dashboard
**Fix**: `node .omc/scripts/hook-stats.mjs` already exists — check if it covers all these commands; if not, extend it to replace the 10 topBash commands

### 2. Bash 371/723 (51%) + zero TaskCreate/TaskUpdate
**Observation**: 371 Bash calls, 0 TaskCreate, 0 TaskUpdate — all work tracking is manual or non-existent. User prompts 790 vs tool calls 723 (ratio > 1) suggests many inputs without structured follow-up.
**Rule**: Heavy bash without task tracking → low traceable progress
**Fix**: N/A (task workflow may be intentionally unused per CLAUDE.md §11; tracking rule only)

### 3. Session productive but no seed generation
**Observation**: 723 tool calls / 2698 lines — active session with good throughput. Seeds = 0 (brainstorm stopped per CLAUDE.md v1.74, so this is expected/ok).
**Rule**: N/A — this is by design, not a problem
**Fix**: N/A

## Mid-Session Live Insight

### 1. Zero Seeds Despite High Activity
**Observation**: 726 tool calls, 793 user prompts, but 0 seeds generated — no brainstorm/seed activity occurred despite substantial session work (2707 lines).
**Rule**: Track seed generation rate per session; seed count should be >0 when session has 100+ tool calls.
**Fix**: N/A

### 2. Repeated State-File Inspection Pattern ✅ EXECUTED
**Observation**: Top 10 Bash commands all inspect .omc/state/ files — `hook-audit.jsonl` (3x), `mcp-learn-queue.jsonl` (2x), `sessions/` dir (2x), and 5 node script invocations. These 10 commands represent a fragmented dashboard replaced by one unified script.
**RootCause**: No single entry point for session state inspection — each stat requires a separate manual command.
**Fix**: Extend `.omc/scripts/hook-stats.mjs` (already exists per topBash) to include mcp-learn-queue count, sessions list, and hook-audit tail — eliminate 9 of 10 separate bash commands.

## Mid-Session Live Insight

### 1. Repeated state-inspection commands suggest extraction to script ✅ EXECUTED
**Observation**: `ls -la .omc/scripts/hook-*.mjs ...`, `wc -l .omc/state/hook-audit.jsonl ...`, `tail -20 .omc/state/hook-audit.jsonl`, `node hook-self-improve.mjs --stats`, `node hook-test-rules.mjs`, `cat mcp-learn-queue.jsonl`, `ls -lt sessions/`, `cat session-start-mcp-inject.md` — 10 distinct commands repeat throughout the session for inspecting OMC state. These 10 commands account for a significant portion of the 379 Bash calls.
**Rule**: Track repeated OMC self-inspection Bash commands; extract to a single `hook-stats.mjs` or `omc-dashboard.mjs` that consolidates all state reads in one place.
**Fix**: Extend `hook-stats.mjs` to include queue depth, session list, and MCP inject content as built-in commands instead of manual Bash chains.

### 2. Zero task tracking in 731 tool calls
**Observation**: TaskCreate=0, TaskUpdate=0 across 731 tool calls and 798 user prompts — no structured task tracking was used despite a large, complex session involving hook debugging, rule testing, and workflow detection.
**Rule**: Track whether TaskCreate/TaskUpdate are used in sessions; absence may indicate tasks are being tracked informally or not at all.
**Fix**: N/A — fix requires behavioral discipline change, not a code change.

### 3. Heavy Bash-to-script ratio suggests automation opportunity
**Observation**: Bash=379 out of 731 total tools (51.8%). Many Bash calls are `node .omc/scripts/hook-*.mjs` variants (workflow-detector, self-improve, test-rules, stats). These are self-referential operations that could be orchestrated from a single entry point rather than individual invocations.
**Rule**: Monitor Bash ratio; sessions >50% Bash with repeated script invocations indicate CLI ergonomics gap.
**Fix**: N/A — observation only, no specific executable fix identified from data.

## Mid-Session Live Insight

### 1. No Task Tracking Despite High Tool Volume
**Observation**: 734 tool calls across 2731 events with 0 TaskCreate and 0 TaskUpdate — a massive amount of work happened with zero task management infrastructure used throughout the session.

**Rule**: Any session exceeding 100 tool calls should use TaskCreate/TaskUpdate to track work items and prevent loss of context.

**Fix**: N/A

---

### 2. Repeated State-Inspection Bash Commands ✅ EXECUTED
**Observation**: Top Bash includes 10 distinct inspection commands run repeatedly (ls/wc/cat/tail on .omc/state/ and .omc/scripts paths). Commands like `node .omc/scripts/hook-self-improve.mjs --stats`, `hook-test-rules.mjs`, `hook-workflow-detector.mjs` appear multiple times — indicating manual looping instead of scripted batch execution.

**RootCause**: No unified dashboard or script that aggregates OMC state inspection; each check requires a separate manual command.

**Fix**: Create a single `hook-stats-dashboard.mjs` script that outputs hook-audit line count, mcp-learn queue depth, self-improve stats, workflow detector summary, and recent sessions — replacing 10+ separate Bash commands with one script.

---

### 3. Seeds Counter at Zero Despite 801 User Prompts
**Observation**: seeds: 0 — 801 prompts processed but nothing was captured as a seed or idea. The innovation pipeline was completely dormant during this session.

**Rule**: Monitor seed generation rate; sessions with >100 tool calls and 0 seeds indicate the idea pipeline may be broken.

**Fix**: N/A

## Mid-Session Live Insight

### 1. No Seeds Generated — Insight Pipeline Broken
**Observation**: `seeds: 0` across 803 user prompts and 736 tool calls. Zero seed generation in a 2737-event session is a complete insight pipeline failure.
**Rule**: Every session must produce seeds; zero seeds means the idea pipeline died.
**Fix**: N/A

### 2. Repeated File Inspection Commands — 10 Near-Identical Bash Calls ✅ EXECUTED
**Observation**: Top 10 Bash commands are all file inspection (`ls -la`, `wc -l`, `cat`, `tail`, `node --stats/--test`) on the same 3-4 files (`hook-audit.jsonl`, `mcp-learn-queue.jsonl`, `hook-*.mjs`, sessions). These 10 patterns repeat every session.
**Rule**: Repeated shell commands on the same files indicate a missing diagnostic script.
**Fix**: Write a single `hook-stats.mjs` or extend existing one to batch-report all hook/state file stats in one shot, replacing 10 separate Bash commands.

### 3. TaskCreate/TaskUpdate Never Used
**Observation**: `TaskCreate: 0`, `TaskUpdate: 0` across 736 tool calls. Zero task management despite a complex multi-step session.
**Rule**: Complex sessions need explicit task tracking to avoid losing context.
**Fix**: N/A

## Mid-Session Live Insight

### 1. State Inspection Commands Unnecessarily Fragmented ✅ EXECUTED
**Observation**: The top 10 Bash commands are all reading different OMC state files (.jsonl, .mjs scripts, session dirs) with no unified view. 387 Bash calls out of 739 total tool calls (52%) suggests heavy shell usage for monitoring. Commands like `ls -la hook-*.mjs`, `wc -l hook-audit.jsonl`, `cat mcp-learn-queue.jsonl`, `tail -20 hook-audit.jsonl` are all the same *intent* (check OMC system state) expressed as 10 separate commands.
**Rule**: Fragmented state inspection makes it hard to get a unified system picture; consolidate into one view.
**Fix**: Expand `hook-stats.mjs` to cover mcp-learn-queue and session-start-mcp-inject in addition to hook-audit, replacing 7 of the top 10 Bash commands with one script invocation.

### 2. Seeds: 0 — This Session Is Hook/Script Dev, Not Seed Execution
**Observation**: seeds: 0 across 739 tool calls and 806 user prompts. The session is entirely OMC self-improvement (hook-self-improve, hook-test-rules, hook-workflow-detector, audit log analysis) with no seed lifecycle activity.
**Rule**: Self-improvement loops (generating → testing → fixing hooks) don't produce seeds; this is normal for this workflow type.
**Fix**: N/A

## Mid-Session Live Insight

### 1. State file inspection commands should be unified into one script
**Observation**: Top 10 Bash commands include 8 distinct commands all reading from `.omc/state/` files (`hook-audit.jsonl`, `mcp-learn-queue.jsonl`, `sessions/`, `session-start-mcp-inject.md`), suggesting repeated manual state inspection. These are 8 separate commands that could be a single `hook-stats.mjs --dashboard` call.

**Rule**: Replace repeated multi-file state inspection with a single unified dashboard script.

**Fix**: Extend `hook-stats.mjs` with a `--state` flag that outputs all state file summaries in one command, replacing `ls -la hook-*.mjs + wc -l *.jsonl + cat mcp-learn-queue.jsonl + tail hook-audit.jsonl + ls sessions/` with a single invocation.

---

### 2. Zero task tracking despite 741 tool calls
**Observation**: `TaskCreate: 0, TaskUpdate: 0` across 741 tool calls and 808 user prompts — all work happened in organic conversation flow with no formal task breakdown.

**Rule**: Track non-trivial work items via TaskCreate/TaskUpdate to maintain session awareness.

**Fix**: N/A (workflow preference rather than executable bug — brainstorm is disabled anyway per session rules).

## Mid-Session Live Insight

### 1. OMC state checks are scripted but manual
**Observation**: 10 topBash commands are all OMC internal state reads (hook-audit.jsonl, mcp-learn-queue.jsonl, session-start-mcp-inject.md, etc.). These are the same 10 commands run repeatedly across 744 tool calls. The pattern shows this is a routine monitoring workflow, but each command is invoked manually.
**Rule**: Monitor ratio of Bash:Read:Edit; if Bash exceeds 50% of total calls, audit for scripted commands masquerading as exploration
**Fix**: N/A

### 2. Bash tool dominates at 52.5% of all calls
**Observation**: 391 Bash calls out of 744 total (52.5%). Read (144) + Edit (89) + Grep (65) + Write (25) = 323 combined — less than Bash alone. TaskCreate and TaskUpdate are both 0.
**RootCause**: The topBash commands are all read-only state inspection (ls, wc, cat, tail, node --stats) — mechanical operations that could be batched into 1-2 script calls instead of 10 individual Bash invocations
**Rule**: Track Bash:tool ratio; if Bash exceeds 40% of total calls, most Bash calls are likely scriptable as a single invocation
**Fix**: N/A

### 3. Zero structured task tracking despite 744 tool calls
**Observation**: TaskCreate: 0, TaskUpdate: 0 across 744 tool calls and 2772 lines. userPrompts: 815 — extremely high prompt count with no task decomposition.
**RootCause**: No evidence of seed/session/task tracking being used in this trajectory; 815 user prompts suggests session was mostly user-driven with no autonomous task framing
**Rule**: Track TaskCreate/TaskUpdate per-session; zero task ops despite high tool count indicates reactive rather than planned execution
**Fix**: N/A

## Mid-Session Live Insight

### 1. Heavy Bash Self-Inspection Loop
**Observation**: 393 Bash calls out of 746 total (52.7%), with topBash dominated by repeated state-file inspection commands (`wc -l`, `cat`, `tail`, `ls -lt`, `node --stats`). The session is polling its own OMC hooks and state files instead of productive work.
**Rule**: Track Bash:total ratio per session; >40% Bash with self-inspection dominance signals a monitoring loop, not productive progress.
**Fix**: N/A

### 2. Repeated `node .omc/scripts/hook-*.mjs` Commands
**Observation**: `hook-self-improve.mjs --stats`, `hook-test-rules.mjs`, `hook-workflow-detector.mjs --min-count 2` each appear multiple times in topBash, suggesting manual re-running of hook diagnostics.
**Rule**: If the same hook script is invoked 3+ times in a session, it should either auto-trigger via hook chain or have its output cached.
**Fix**: Add memoization/caching to hook diagnostic scripts to avoid re-running within same session.

### 3. Zero Seeds Despite 817 User Prompts
**Observation**: `seeds: 0` in trajectory despite 817 user prompts — insight generation ran but produced no seeds for the pool.
**Rule**: Seeds=0 indicates insight generator passed quality gates but found no actionable items, or was blocked by prior seed not shipped.
**Fix**: N/A

## Mid-Session Live Insight

### 1. Repeated state file inspection via Bash
**Observation**: Top 10 Bash commands are all variations of inspecting the same 5-6 OMC state files (`hook-audit.jsonl`, `mcp-learn-queue.jsonl`, session files). Commands like `tail -20 .omc/state/hook-audit.jsonl`, `wc -l .omc/state/hook-audit.jsonl`, `ls -lt .omc/state/sessions/` repeat the same read-only inspection pattern.
**Rule**: Repeated Bash commands inspecting the same files 3+ times indicate a workflow gap — should be a script or event-driven hook rather than manual polling.
**Fix**: `N/A` (already covered by `hook-self-improve.mjs --stats` — repeated manual inspection suggests the stats script output is being manually verified rather than trusted; investigate whether stats output matches manual inspection expectations)

### 2. Zero task tracking despite high activity
**Observation**: 770 tool calls, 841 user prompts, 2850 events — but TaskCreate=0 and TaskUpdate=0. The entire session ran without any OMC task tracking.
**Rule**: High-activity sessions without task tracking miss the self-learning闭环 feedback loop that seeds rely on for lifecycle management.
**Fix**: `N/A` (tracking rule only — no executable fix for this pattern without inventing a hook, which is out of scope)

### 3. Bash represents 53% of all tool calls
**Observation**: 408 Bash calls / 770 total = 53% Bash ratio. Read(146) + Edit(96) + Grep(65) + Write(25) = 332 combined. The session is essentially a Bash session with occasional file reads/edits on top.
**Rule**: Sustained Bash ratios above 50% typically indicate the agent is doing system inspection work rather than creative/delivery work — monitor for sessions where Bash stays above 60% for extended periods.
**Fix**: `N/A` (monitoring/tracking rule — no specific executable action from this data)

## Mid-Session Live Insight

### 1. Repeated state inspection commands form a pattern
**Observation**: The top 10 Bash commands are all OMC self-monitoring commands repeated in a tight loop — `ls`/`tail` audit files, `wc -l` queue files, `node hook-*.mjs --stats`. Each appears 1-2x in the top list but collectively dominate the session. The 416 Bash calls against 0 seeds generated, 0 TaskCreate calls, and only 25 Write calls indicates this session was pure OMC self-observation, not productive project execution.
**Rule**: Track OMC self-maintenance sessions separately; if Bash占总调用>40%且seeds=0, 标注为"introspection mode"而非 productive session.
**Fix**: N/A

### 2. No task tracking despite 780 tool calls
**Observation**: 780 tool calls over 2880 lines with 851 user prompts, yet TaskCreate=0 and TaskUpdate=0. All work was ad-hoc script execution with no structured task tracking.
**Rule**: Even self-improvement loops should use TaskCreate/TaskUpdate to prevent lost context.
**Fix**: N/A

### 3. Seeds=0 across a full productive session
**Observation**: seeds: 0 — despite 780 tool calls and 851 user prompts, no seeds were generated or worked. This session appears to be pure OMC maintenance (hook-audit, mcp-learn-queue, workflow-detection) with no idea generation or execution.
**Rule**: If session tools are all .omc/scripts/hook-*.mjs and seeds=0, consider whether session should be classified as "maintenance" rather than "productive".
**Fix**: N/A

### 23. Bash占62.7%工具调用但无insight产出 [auto-generated]

**Observation**: 32次Bash调用占总工具调用51次的62.7%，但整个session无任何insight记录；用户首尾prompt均质疑insight缺失，说明insight生成管道对此类Bash密集型session失效。

**Rule**: 工具调用密集型session（Bash>20次或任意单一工具>40%）必须触发insight提取，不依赖seed生成。



### 24. [Bash 64% - 脚本应直接执行而非派生子进程] [auto-generated] ✅ EXECUTED
**Observation**: 29/45 tool calls (64%) 是 Bash，子 agent 执行 insight fix 时通过 shell 派生，而非直接在当前上下文执行。轨迹显示用户明确要求"先让insight生成就立刻执行"但执行路径仍然绕道 subagent。
**Rule**: insight generator 执行阶段必须直接在当前 agent 执行，不应派生 subagent 绕路
**Fix**: 修改 `omc-insight-generator.mjs` 的执行路径：当检测到 fix 为可执行 action 时，直接通过 Edit/Write/Bash 原生工具执行，禁止 spawn subagent 执行



### 25. 54 tool calls, 0 seeds — self-improvement loop broken [auto-generated]

**Observation**: 200 events, 54 tool calls, 1 user prompt, 0 seeds generated. Heavy Bash(34) skews tool balance; no new ideas created despite active session. Start and end both "解决未解决的" suggests working on existing items without generating new seeds.

**Rule**: Every active session should produce at least 1 seed or mark existing seeds as shipped/killed; zero-seed sessions indicate reactive vs. generative mode.



### 26. [Zero seeds in full session] [auto-generated]
**Observation**: 200 events, 54 tool calls, 1 user prompt — yet 0 seeds generated. The entire session ran without any brainstorming or idea pool activity despite being a full-length session.
**Rule**: Every session that completes task work should still feed the idea pipeline; seed generation is not optional even during task execution.
**Fix**: N/A

### 27. [Heavy Bash dominance 63%] [auto-generated]
**Observation**: Bash(34) = 63% of all tool calls (34/54). Edit(9) + Read(9) + Write(2) = 20 combined. The session was overwhelmingly bash-driven with minimal code/file edits.
**Rule**: Sustained heavy bash usage (60%+) often signals task-execution mode without generative output — track as efficiency signal.
**Fix**: N/A

### 29. [PostToolUse hook 未触发导致计数器失效]
**Observation**: 当前 session 的 PostToolUse hook 未触发，audit log 无当前 session 记录，计数器始终为 0。hook 配置正确但执行层失效，导致 auto-insight 管道断路。
**Rule**: hook 失效时应触发 AI 端主动检测，而非静默失败
**Fix**: 在 `hook-session-start-inject.mjs` 中增加计数器检查，若 `count>0 且 fired=false`，注入提醒让 AI 主动完成 insight 生成

### 30. [insight验证缺失闭环]
**Observation**: insight-verifications.md 只有 `Result: executed`，无实际效果验证。所有 Fix 执行后没有客观标准判断是否有效。
**Rule**: 每个 executable insight 执行后必须验证，并记录：预期效果 vs 实际效果
**Fix**: 在 pending-actions 执行后，要求输出验证结果（有效/无效/部分有效），写入 insight-verifications.md

### 28. [实时insight生成管道打通] [in-session]
**Observation**: 本 session 修改了 `hook-auto-seed.mjs`（seed→insight）和 `hook-session-start-inject.mjs`（注入 trigger），实现了10次工具调用触发 in-session insight 生成，而非事后分析 trajectory。测试确认 trigger 正确注入到 session-start hook 输出中。
**Rule**: insight 应在会话中实时生成，不依赖 drain 后的 trajectory 分析
**Fix**: 验证：下次工具调用≥10次时，`auto-insight-trigger.json` 应存在且被 hook 正确读取



### 31. [Self-inspection loop wastes 50%+ tool calls] [auto-generated] ✅ EXECUTED
**Observation**: Top 5 Bash commands are all OMC self-monitoring: `ls hook-*.mjs + wc -l audit+queue + node hook-self-improve --stats + node hook-test-rules + cat mcp-learn-queue`. 1079 Bash calls out of 1992 total (54%). Repeated self-inspection wastes capacity.
**Rule**: Self-monitoring commands should be batched into a single script, not scattered across multiple manual calls.
**Fix**: Create `.omc/scripts/hook-dashboard.mjs` that outputs hook-audit lines, queue depth, stats, test results, and session state in ONE invocation. Replace topBash with `node .omc/scripts/hook-dashboard.mjs`.

### 32. [hook-stats.mjs cache works but not replacing manual inspection] [auto-generated]
**Observation**: hook-stats.mjs outputs a complete dashboard in one line, but topBash still shows repeated manual commands (`ls hook-*.mjs`, `wc -l *.jsonl`, `node hook-self-improve --stats`). The script exists and works but isn't being used instead of the manual inspection cycle.
**Rule**: If a script exists that replaces a repeated workflow but isn't being used, the workflow is惯性大于效率.
**Fix**: Execute `node .omc/scripts/hook-stats.mjs` once and use its output for all state inspection needs instead of the 5 separate commands.

### 33. TaskCreate/TaskUpdate Completely Unused ✅ EXECUTED Across 2022 Tool Calls [auto-generated]
**Observation**: 2022 total tool calls with TaskCreate: 0 and TaskUpdate: 0 across the entire session — zero task management infrastructure used despite massive volume. Top 5 Bash commands are all OMC self-monitoring (ls/wc/cat/tail/node on state files).
**Rule**: Sessions exceeding 500 tool calls without a single TaskCreate/TaskUpdate are operating without structured progress tracking — all work is invisible to the task system.
**Fix**: Add task creation to the auto-insight trigger: when count > threshold, also create a tracking task via TaskCreate before running diagnostics. Append `node .omc/scripts/hook-stats.mjs` to pending-actions as the single replacement for all topBash inspection commands.

### 34. [Repeated self-inspection commands still dominant after 3 insights] ✅ EXECUTED [auto-generated]
**Observation**: After insights #31/32/33 about Bash dominance (54-64%), topBash remains unchanged: `ls hook-*.mjs + wc -l *.jsonl + node hook-self-improve --stats + node hook-test-rules + cat mcp-learn-queue`. 1134 Bash calls (54%) with zero TaskCreate/TaskUpdate.
**Rule**: Insights about a pattern don't fix the pattern — the Fix must be automated, not just documented.
**Fix**: Execute `node .omc/scripts/hook-stats.mjs` ONCE and commit to using it for all future state inspection instead of manual commands. Then delete the redundant repeated inspection commands from future workflows.

### 35. [Bash 54% persists after 4 insights] ✅ EXECUTED despite commit to hook-stats.mjs] [auto-generated]
**Observation**: After insight #34 commit to use hook-stats.mjs, topBash still shows 5 repeated commands (ls hook-*.mjs, wc -l *.jsonl, node hook-self-improve --stats, node hook-test-rules, cat mcp-learn-queue). TaskCreate:0, TaskUpdate:0 across 2083 calls.
**Rule**: A Fix that's "execute once" doesn't change behavior — the workflow must replace the old pattern, not be added alongside it.
**Fix**: Delete the 5 manual inspection commands from any future workflow. Use ONLY `node .omc/scripts/hook-stats.mjs`. If hook-stats output is insufficient, improve the script, don't bypass it with manual commands.

### 36. [20 hook scripts with overlapping functionality] ✅ EXECUTED - redundant wheel reinvention] [auto-generated]
**Observation**: 20 hook-*.mjs scripts exist: hook-stats, hook-dashboard, hook-self-improve, hook-test-rules, hook-workflow-detector, etc. Insights #31-35 repeatedly suggest creating "hook-stats-dashboard" or "hook-stats.mjs" when both already exist. Agent doesn't read existing scripts before suggesting new ones.
**Rule**: Before suggesting a new script, read .omc/scripts/hook-*.mjs to check if it already exists. Repeated suggestions to create existing tools waste insight cycles.
**Fix**: Audit all 20 hook scripts, document each one's purpose, remove duplicates. For this session: use existing hook-stats.mjs for state inspection instead of 5 manual commands.

### 37. [Active learning hook triggers on meaningless test output]
**Observation**: hook-active-learn.mjs triggered on test Write ("hello world" to test.txt) — no real work was done, but system still generated a trigger. The trigger file contains meaningless content because the "work" was just a test.
**Rule**: Active learning should filter out test/debug operations. A test file write is not learning material.
**Fix**: In isMeaningfulWork(), add: reject if file_path ends in .txt, .test.*, .spec.*, or contains "test" in path.
