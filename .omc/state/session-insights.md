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

### 4. Workflow Consolidation Opportunity
**Observation**: Bash→Bash→Bash pattern occurs 56× in single session
**Root cause**: diagnostic scripts run --stats + read queue + --emit in sequence
**Improvement**: consolidate into single multi-command script

### 5. Agent is the Analysis Engine
**Principle**: I am responsible for generating insights, not external LLMs
**Wrong pattern**: hook calling MiniMax/Ollama for insight generation
**Correct pattern**: hook stores raw data → drain → next session agent analyzes
