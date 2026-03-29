---
status: done
id: ruvnet-ruflo
hash: sha256:aeb5be910acbfb73
generated_from: research
source_url: https://github.com/ruvnet/ruflo
confidence: 1.00
created_at: 2026-03-28T02:18:20.673Z
updated_at: 2026-03-28T02:36:59.483Z
---

# Plan: ruvnet/ruflo — Agent Orchestration Platform

**Research source**: https://github.com/ruvnet/ruflo

**研究摘要**: 🌊 The leading agent orchestration platform for Claude. Deploy intelligent multi-agent swarms, coordinate autonomous workflows, and build conversational AI systems. Features enterprise-grade architecture, distributed swarm intelligence, RAG integration, and native Claude Code / Codex Integration

**置信度**: 1.00

**为什么适合 workspace**: 来自 github 的高质量研究，与现有项目相关。

---

## What is RuFlo

RuFlo (formerly Claude Flow) is an enterprise-grade AI agent orchestration platform that transforms Claude Code into a multi-agent development environment. It coordinates 100+ specialized agents through self-learning swarms with fault-tolerant consensus mechanisms.

**Stats**: 27.5k GitHub stars · 6,000+ commits · 137+ skills · 27 hooks · 12 background workers

---

## Tech Stack

- **Runtime**: Node.js 20+
- **Language**: TypeScript
- **Backend**: Rust (WASM kernels for policy engine and embeddings)
- **LLM Providers**: Anthropic Claude, OpenAI GPT, Google Gemini, Ollama (local models)
- **Database**: PostgreSQL with vector search (HNSW), SQLite persistence

---

## Key Features

### 100+ Specialized Agents
Coder, tester, reviewer, architect, security, and more — each agent is specialized for a specific task domain.

### Self-Learning Swarm Intelligence
- **RuVector Intelligence Layer**: SONA (self-optimization), EWC++ (catastrophic forgetting prevention), Flash Attention, HNSW vector search, Hyperbolic Poincaré embeddings, LoRA fine-tuning, 9 RL algorithms
- Stores successful patterns, learns from outcomes, adapts routing
- Vector DB stores agent performance embeddings for task-to-agent matching

### Swarm Coordination Patterns
- **Queen-led hierarchies**: strategic → tactical → adaptive agent layers
- **Mesh peer-to-peer**: equal-weight agent topology
- **Consensus mechanisms**: Raft, Byzantine, Gossip protocols

### Multi-LLM Support with Intelligent Routing
- Claude, GPT, Gemini, Cohere, Ollama with automatic failover
- **WASM-based Agent Booster**: handles simple code transforms in <1ms, 352x faster than LLM
- **Token Optimizer**: 30-50% token reduction via compression and caching
- Routes by task complexity: simple → medium → complex models

### Security
- Built-in AIDefence protection against prompt injection
- Input validation, path traversal prevention

### 12 Background Workers
Auto-dispatch on file changes, patterns, sessions

---

## Architecture

```
User → Ruflo (CLI/MCP) → Router → Swarm → Agents → Memory → LLM Providers
                                       ↑
                                       ↓
                                Learning Loop ←────┘
```

### RuVector Intelligence Layer
- SONA (self-optimizing), EWC++ (catastrophic forgetting prevention)
- Flash Attention, HNSW vector search
- Hyperbolic Poincaré embeddings, LoRA fine-tuning
- 9 RL algorithms

### Memory System
- HNSW-based vector storage
- AgentDB persistence
- SQLite with WAL mode

---

## Installation

```bash
# One-line install (recommended)
curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/ruflo@main/scripts/install.sh | bash

# Full setup with MCP + diagnostics
curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/ruflo@main/scripts/install.sh | bash -s -- --full

# Or via npx
npx ruflo@latest init --wizard
```

**Prerequisites**: Node.js 20+, Claude Code (`npm install -g @anthropic-ai/claude-code`)

---

## Use Cases

- Development/code quality
- Security audits
- Multi-agent swarms
- Performance optimization
- GitHub/DevOps integration
- Spec-driven development
- Learning/intelligence workflows

---

## Relevance to OpenClaw Workspace

This project is highly relevant to the OpenClaw workspace because:

1. **Multi-agent orchestration**: The workspace already has several multi-agent projects (multi-agent-discuss, patrol-agent, ai-roundtable). RuFlo's swarm intelligence patterns could inspire improvements.

2. **Agent-to-agent communication**: RuFlo's hierarchical queen/worker pattern and mesh topology for agent coordination could inform the a2a-router project.

3. **Self-learning routing**: RuFlo's RuVector intelligence layer — which stores agent performance embeddings and routes tasks to best-performing agents — is directly applicable to the memory-mesh concept in the workspace.

4. **MCP integration**: RuFlo's native MCP support aligns with the workspace's existing MCP server work.

---

## Implementation Roadmap

### Recommended: Option B + D (Hybrid + Incremental)

**Phase 1 — MCP Bridge (Week 1-2)**: Low risk
- Extend `a2a-router` to connect to Ruflo MCP Server as upstream provider
- Ruflo agents appear as peers in `multi-agent-discuss` discovery
- No architectural changes to existing projects

**Phase 2 — Hybrid Orchestration (Week 3-6)**: Medium effort
- Connect `self-evolving-orchestrator` (ResultRanker, SelfEvolver) to Ruflo worker pool
- SelfEvolver selects Ruflo agents for task execution
- Preserve existing Go orchestrator logic

**Phase 3 — Intelligence Layer (Week 7+)**: Future
- Deepen RuVector integration if Phase 2 succeeds
- Consider Rust-based HNSW components callable from Go

### NOT Recommended
- **Option A (Full adoption)**: Would replace multi-agent-discuss, self-evolving-orchestrator, and a2a-router — kills valuable custom work
- **Option C (Fork intelligence layer)**: Too much reverse-engineering effort for uncertain payoff

### Immediate Actions
1. Install: `curl -fsSL https://cdn.jsdelivr.net/gh/ruvnet/ruflo@main/scripts/install.sh | bash`
2. Test MCP: `npx ruflo@latest hooks intelligence --status`
3. Preserve all existing projects — do NOT delete
4. Full analysis: `docs/superpowers/plans/2026-03-28-ruvnet-ruflo-analysis.md`
