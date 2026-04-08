## Insights from 2026-04-08 session

### 1. Hook Responsibility Boundary
**Rule**: hooks = collect + store only; agent generates insights
**Violation fixed**: hook-mcp-consumer once called Ollama → removed
**Key**: no LLM calls in hooks, ever

### 2. Deduplication Required for Audit Spam
**Problem**: `ls 34~50` (16 calls at 20ms intervals) flooded audit log
**Fix**: 500ms dedup window in hook-audit-log-mcp
**Pattern**: debug loops can generate rapid repeated commands

### 3. Modern JSONL Uses tool_use Blocks
**Problem**: trajectory extractor used text regex for tool names
**Fix**: parse `type: 'tool_use'` blocks with `.name` field
**Format**: modern Claude Code JSONL has array content with block types

### 4. Workflow Consolidation Opportunity ✅ EXECUTED
**Observation**: Bash→Bash→Bash pattern occurs 56× in single session
**Root cause**: diagnostic scripts run --stats + read queue + --emit in sequence
**Fix**: `omc-diagnose.mjs` 合并了三个诊断命令为一条

### 5. Agent is the Analysis Engine
**Principle**: I am responsible for generating insights, not external LLMs
**Wrong pattern**: hook calling MiniMax/Ollama for insight generation
**Correct pattern**: hook stores raw data → drain → next session agent analyzes

### 6. Hook问题需要明确的验证反馈 ✅ EXECUTED
**Observation**: session 899884e0中用户反复问"hook启用了吗"共106次
**Root cause**: hook状态不透明，用户无法从行为感知hook是否工作
**Fix**: drain文件现在包含Hook Status段落（entries today、tools、dedup、queue depth）
**Result**: 下个session用户可从drain文件直接看到hook活跃状态

### 7. 大型调试session的特征
**Data**: 1419次工具调用，857次Bash（60%），191次Read，129次Edit
**Pattern**: Read+Edit+Bash密集混合，说明在修复而非创造
**Opportunity**: 此类session的trajectory应标记为"debugging"而非"generating"，用于区分不同工作模式
