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
