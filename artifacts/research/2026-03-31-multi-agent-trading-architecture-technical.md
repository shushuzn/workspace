# Technical Research: Multi-Agent Trading Architecture for stock-analysis-agent

## Strategic Summary

TradingAgents uses a **multi-agent debate architecture** where specialized analysts feed into opposing researchers who debate findings, then a trader synthesizes and risk management approves. The current stock-analysis-agent uses a **simple ReAct loop** — a significant architectural upgrade would add team collaboration, debate rounds, and structured synthesis. Recommended approach: **LangGraph-based multi-agent orchestration** layered on existing tool infrastructure.

## Requirements

- Target project: `stock-analysis-agent`
- Primary goal: Multi-agent collaboration (借鉴多智能体协作)
- Deployment target: Local CLI (本地CLI)
- Preserve existing: Tool infrastructure (agent_tools.py), report generation (report.py), LLM integration (llm.py)

---

## Current State Comparison

| Component | stock-analysis-agent (now) | TradingAgents (target) |
|-----------|---------------------------|----------------------|
| Agent pattern | Single ReAct loop | Multi-agent team |
| Tool use | Sequential execution | Per-agent tools |
| Synthesis | LLM + rules | Structured debate → Trader |
| Memory | None | Per-agent memory |
| Routing | Fixed tool selection | Conditional graph edges |
| Risk | Rule-based signal | Portfolio Manager |

---

## Approach 1: LangGraph Multi-Agent (Recommended — Full Architecture)

### How it works

Replace the single ReAct loop with a LangGraph state machine. Agents are graph nodes. Edges route based on state. Each agent gets a memory via state context.

```
┌─────────────────────────────────────────────────────────────────┐
│                        AgentState                                │
│  symbol, query,                                                  │
│  analyst_reports: {fundamental, sentiment, news, technical},     │
│  bull_case: str, bear_case: str,                                │
│  trader_decision: str, risk_verdict: str,                       │
│  memories: {bull, bear, trader, risk}                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  analyst_team (parallel node)                                   │
│  ├── fundamentals_analyst → get_fundamentals tool               │
│  ├── sentiment_analyst → news/social tools                     │
│  ├── news_analyst → get_news tool                              │
│  └── technical_analyst → calc_all tool                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  researcher_team (sequential debate)                            │
│  ├── bull_researcher → bull_case = 分析报告...做多理由          │
│  │        ↓ max_debate_rounds                                   │
│  └── bear_researcher → bear_case = 分析报告...做空理由          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  trader (synthesis node)                                        │
│  Composes final report + trading decision                        │
│  action: BUY / SELL / HOLD | confidence: 0.0-1.0                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  risk_manager (approval node)                                   │
│  Evaluates: volatility, liquidity, position size                │
│  verdict: APPROVED / REJECTED | reasoning                        │
└─────────────────────────────────────────────────────────────────┘
```

### Libraries

```bash
pip install langgraph langchain-core langchain-anthropic
```

- `langgraph` (latest) — state machine orchestration
- `langchain-core` / `langchain-anthropic` — agent primitives
- Existing `agent_tools.py` (fully preserved — tool layer unchanged)
- `stock-analysis-mcp` (sibling project, already integrated)

### Files to Create

```
src/multi_agent/
  __init__.py
  state.py          # AgentState dataclass with TypedDict
  graph.py          # LangGraph compilation
  nodes/
    __init__.py
    analyst_team.py   # parallel analyst execution
    researchers.py    # bull/bear debate with memory
    trader.py        # synthesis + decision
    risk_manager.py  # risk evaluation + approval
  prompts.py        # system prompts per agent role
  config.py         # DEFAULT_CONFIG equivalent
```

### Pros

- Battle-tested pattern (44k stars on TradingAgents)
- Conditional routing is explicit and debuggable
- Per-agent memory via state persistence
- Supports debate rounds (`max_debate_rounds`)
- Multi-LLM provider support (OpenAI, Claude, Gemini, etc.)
- Full audit trail of agent reasoning

### Cons

- Steeper learning curve than ReAct
- More complex debugging (state machine vs linear)
- Must define prompts for each agent role
- Overhead of graph compilation for simple tasks

### Best when

Building a production multi-agent system requiring debate, synthesis, and risk management

### Complexity

M → L

---

## Approach 2: Supervisor/Hierarchical Pattern

### How it works

A supervisor LLM coordinates sub-agents via tool-calling or function routing. Supervisor receives analyst outputs and decides next steps (similar to AutoGen's GroupChat).

```python
# Supervisor decides: "analyst_team" → "researcher_debate" → "trader" → "risk"
decisions = supervisor.invoke(state)
```

### Libraries

- `autogen-agentchat` (微软AutoGen) — supervisor orchestration
- Or: Custom supervisor with existing ReAct pattern

### Pros

- Simpler than full LangGraph
- Supervisor can dynamically route based on task
- Good for 3-5 agent coordination
- Less boilerplate than LangGraph

### Cons

- Routing is prompt-dependent, not explicit edges
- Supervisor prompt engineering is tricky
- No built-in debate round support
- Central supervisor becomes bottleneck

### Best when

Quick prototype with 3-4 agents, no complex conditional routing

### Complexity

S → M

---

## Approach 3: Parallel Tool Agents + LLM Synthesis (Pragmatic First Step)

### How it works

Keep existing tool infrastructure entirely. Run analyst tools concurrently with `asyncio`, then use an LLM with explicit bull/bear framing for synthesis. No new framework.

```python
# Run all indicator tools in parallel
async def analyst_team(symbol):
    results = await asyncio.gather(
        get_fundamentals(symbol),
        calc_all(symbol),
        get_news(symbol),
    )
    return results

# Then LLM synthesis with bull/bear framing
prompt = f"""你是专业分析师。针对 {symbol}：
bullish_arguments: ...  # from fundamentals + positive indicators
bearish_arguments: ...  # from negative indicators
给出做多/做空/观望决策。"""
```

### Libraries

- `asyncio` — built-in, parallel execution
- Existing `agent_tools.py` — no changes
- Existing `llm.py` — enhanced with debate prompts
- Existing `report.py` — extended for debate format

### Pros

- Minimal new infrastructure
- Leverages existing code fully
- Async parallel execution → faster results
- Fastest to implement (days, not weeks)

### Cons

- No true agent memory between rounds
- No explicit debate routing
- Synthesis is single LLM call, not structured agent
- Can't easily add complex conditional logic

### Best when

Evolutionary upgrade path, preserving ReAct simplicity while adding parallelism

### Complexity

S

---

## Comparison Matrix

| Aspect | LangGraph Multi-Agent | Supervisor Pattern | Parallel + LLM |
|--------|----------------------|-------------------|----------------|
| Multi-agent debate | ✅ Explicit edges | ⚌ Implicit/prompt | ❌ No |
| Agent memory | ✅ Per-agent via state | ⚌ Global only | ❌ No |
| Routing clarity | ✅ Edges visible | ⚌ Prompt-dependent | N/A |
| Implementation effort | High | Medium | Low |
| Debuggability | Excellent | Medium | Good |
| Matches TradingAgents | ★★★★★ | ★★☆☆☆ | ★☆☆☆☆ |
| Time to prototype | 1-2 weeks | 3-5 days | 1-2 days |
| Preserves existing tools | ✅ | ✅ | ✅✅ |

---

## Recommendation

**Option A — Full LangGraph** for production system when ready for full TradingAgents architecture.
**Option B — Parallel+LLM first** as pragmatic Phase 1 (days), then evolve to LangGraph when architecture stabilizes.

Given the existing `stock-analysis-agent` codebase, a **hybrid approach**:

1. **Phase 1 — Parallel Execution** (1-2 days): Add async parallel tool execution, enhance LLM synthesis with explicit bull/bear framing
2. **Phase 2 — Add Debate** (3-5 days): Introduce bull_researcher and bear_researcher as separate LLM calls with opposing mandates, multi-round debate
3. **Phase 3 — LangGraph** (1-2 weeks): Formalize with state machine when roles and data flow stabilize

---

## Implementation Context

### For LangGraph Approach (full)

**libraries:**
```bash
pip install langgraph langchain-core langchain-anthropic
```

**key files to create:**
- `src/multi_agent/state.py` — AgentState TypedDict
- `src/multi_agent/graph.py` — LangGraph compilation
- `src/multi_agent/nodes/analyst_team.py` — parallel analyst execution
- `src/multi_agent/nodes/researchers.py` — bull/bear debate
- `src/multi_agent/nodes/trader.py` — synthesis + decision
- `src/multi_agent/nodes/risk_manager.py` — risk approval
- `src/multi_agent/prompts.py` — role prompts

**reference patterns from existing code:**
- `src/agent_tools.py` — tool executor (unchanged)
- `src/llm.py` — LLM client setup (reuse)
- `src/report.py` — report formatting (extend)

### For Parallel+LLM Approach (quick)

**modify:**
- `src/agent.py` — add async parallel execution
- `src/llm.py` — add bull/bear debate synthesis prompts
- `src/report.py` — add debate section format

**new:**
- `src/debate.py` — bull_researcher/bear_researcher prompts

### Next Action

Prototype Approach 3 (Parallel+LLM) as proof-of-concept, then evaluate whether complexity warrants LangGraph upgrade.

---

## Sources

- TradingAgents GitHub: https://github.com/TauricResearch/TradingAgents — 44.8k stars
- LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- stock-analysis-agent: `80-PROJECTS/stock-analysis-agent/`
