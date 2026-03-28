# Self-Evolving Task Orchestrator - Design Specification

**Date:** 2026-03-28
**Status:** Draft
**Author:** Claude

## 1. Overview

### Problem Statement

现有三个项目各自独立运作：
- `a2a-router` - A2A 路由核心（TypeScript）
- `agent-islands` - 多Agent协作平台（TypeScript）
- `multi-agent-discuss` - Go 多Agent讨论系统

缺乏统一的自演化任务编排能力，无法根据执行反馈自动调整任务分解策略。

### Solution

构建 **Self-Evolving Orchestrator**，基于 SEMA 和 AutoAgent 论文，实现：

1. **LLM 驱动的任务分解** - 复用 `OrchestratorAgent` 的 LLM 分解能力
2. **自演化循环** - decompose → execute → evaluate → refine → repeat
3. **混合架构** - Go 处理核心逻辑，TypeScript 处理协议适配

---

## 2. Architecture

### Overall Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client / User                             │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TypeScript Protocol Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ MCP Adapter │  │ A2A Adapter │  │ HTTP API    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Go Core Engine                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              SelfEvolvingOrchestrator                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐        │   │
│  │  │ Decomposer │  │ SelfEvolver│  │ResultRanker│        │   │
│  │  └────────────┘  └────────────┘  └────────────┘        │   │
│  │                                                          │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │              EvolutionLoop                         │   │   │
│  │  │   decompose → execute → evaluate → refine → repeat│   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                │                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Dispatcher   │  │   Executor   │  │    Peer     │       │
│  │  (现有复用)   │  │  (现有复用)   │  │  Registry   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TypeScript Agent Islands                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ AgentHub    │  │  Workflow   │  │  Adapters   │          │
│  │             │  │Orchestrator │  │(News/Stock)│          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Technology | Responsibility |
|-------|-------------|----------------|
| **Protocol Adapter** | TypeScript | MCP/A2A protocol conversion, HTTP API |
| **Core Engine** | Go | Task decomposition, self-evolution, result ranking |
| **Agent Execution** | TypeScript | Task execution, tool invocation |
| **Communication** | Both | IPC, message queue |

---

## 3. Components

### 3.1 SelfEvolvingOrchestrator (Go)

**Location:** `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/`

**Interface:**

```go
type Orchestrator interface {
    Process(ctx context.Context, task string) (string, error)
    ProcessWithEvolution(ctx context.Context, task string, opts *EvolutionOptions) (string, error)
}

type EvolutionOptions struct {
    MaxIterations   int
    QualityThreshold float64
    Timeout        time.Duration
}
```

**Key Methods:**

- `Process(task)` - Basic orchestration (existing)
- `ProcessWithEvolution(task, opts)` - Self-evolving orchestration (new)

### 3.2 Decomposer (Go, Existing)

Reuses existing `LLMDecomposer` from `multi-agent-discuss`.

```go
type LLMDecomposer interface {
    Decompose(ctx context.Context, task string) ([]string, error)
}
```

### 3.3 SelfEvolver (Go, New)

**Purpose:** Analyzes execution results and adjusts decomposition strategy.

```go
type SelfEvolver struct {
    history       []EvolutionRecord
    strategyPool   []DecomposeStrategy
    currentStrategy int
}

type EvolutionRecord struct {
    Task       string
    Subtasks   []string
    Results    []ExecutionResult
    Score      float64
    Strategy   DecomposeStrategy
}

type DecomposeStrategy struct {
    Name           string
    Granularity    Granularity  // coarse, medium, fine
    ModelHint      string       // "fast" or "strong"
    MaxSubtasks    int
}

func (s *SelfEvolver) ShouldRefine(ctx context.Context, record *EvolutionRecord) (bool, string)
func (s *SelfEvolver) GetNextStrategy() DecomposeStrategy
func (s *SelfEvolver) RecordResult(record *EvolutionRecord)
```

**Refinement Triggers:**
- All subtasks failed
- Score below threshold
- Timeout exceeded
- Excessive overlap between subtasks

### 3.4 ResultRanker (Go, New)

**Purpose:** Multi-dimensional scoring and ranking of execution results.

```go
type ResultRanker struct {
    weights ScoringWeights
}

type ScoringWeights struct {
    Quality   float64  // 0.0-1.0, result correctness
    Latency  float64  // 0.0-1.0, execution speed
    Success  float64  // 0.0-1.0, execution success rate
    Relevance float64 // 0.0-1.0, relevance to original task
}

type RankedResult struct {
    Result      *ExecutionResult
    TotalScore  float64
    Breakdown    ScoreBreakdown
}

func (r *ResultRanker) Rank(results []ExecutionResult) []RankedResult
func (r *ResultRanker) AggregateAndScore(subtaskResults [][]ExecutionResult) float64
```

### 3.5 EvolutionLoop (Go, New)

**Purpose:** Implements the self-evolution cycle.

```go
type EvolutionLoop struct {
    decomposer *LLMDecomposer
    evolver    *SelfEvolver
    ranker     *ResultRanker
    executor   func(subtask string) ExecutionResult
}

func (e *EvolutionLoop) Run(ctx context.Context, task string, opts *EvolutionOptions) (*EvolutionResult, error)

type EvolutionResult struct {
    FinalTask     string
    Subtasks     []string
    Results      []RankedResult
    Iterations   int
    FinalScore  float64
    Converged    bool
}
```

**Evolution Cycle:**

```
┌─────────────────────────────────────────────────────────────┐
│                     EvolutionLoop                             │
│                                                              │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐ │
│   │Decompose│───▶│Execute  │───▶│Evaluate │───▶│Refine?  │ │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘ │
│       ▲                                           │          │
│       │                                           yes        │
│       └────────────────────────────────────────────          │
│                            no (score > threshold)            │
└─────────────────────────────────────────────────────────────┘
```

**Termination Conditions:**
- Quality score >= threshold
- Max iterations reached
- Timeout exceeded
- Manual stop

### 3.6 Protocol Adapters (TypeScript)

**MCP Adapter:** `ts/adapters/mcp-adapter.ts`

```typescript
interface MCPAdapter {
  connect(): Promise<void>
  sendTask(task: string): Promise<EvolutionResult>
  getStatus(): Promise<OrchestratorStatus>
}
```

**A2A Adapter:** `ts/adapters/a2a-adapter.ts`

```typescript
interface A2AAdapter {
  register(agentId: string, capabilities: string[]): Promise<void>
  send(task: string, targetAgents: string[]): Promise<ExecutionResult>
}
```

### 3.7 Peer Registry (Go)

**Purpose:** Manages available peer agents.

```go
type PeerRegistry struct {
    peers map[string]*PeerInfo
    mu    sync.RWMutex
}

type PeerInfo struct {
    ID          string
    Name        string
    Capabilities []string
    Status      AgentStatus
    Load        float64
    LastSeen    time.Time
}
```

---

## 4. Data Flow

### 4.1 Basic Task Flow

```
1. Client → TS MCP Adapter → Go Orchestrator
   │
2. Orchestrator.ProcessWithEvolution(task)
   │
3. EvolutionLoop.Run():
   │
   ├── Iteration 1:
   │   a. Decomposer.Decompose(task) → [subtask1, subtask2, subtask3]
   │   b. Execute(subtask1), Execute(subtask2), Execute(subtask3) in parallel
   │   c. Ranker.Rank(results) → score: 0.65
   │   d. Quality < threshold, ShouldRefine → true
   │
   ├── Iteration 2:
   │   a. Evolver.GetNextStrategy() → finer granularity
   │   b. Decomposer.Decompose(task, strategy) → [s1, s2, s3, s4, s5]
   │   c. Execute in parallel
   │   d. Ranker.Rank(results) → score: 0.82
   │   e. Quality >= threshold, CONVERGED
   │
4. Return EvolutionResult to Client
```

### 4.2 Result Aggregation

```go
type AggregatedResult struct {
    TaskID       string
    FinalOutput  string
    TotalCost    float64  // LLM tokens, compute
    Iterations   int
    QualityScore float64
    ExecutionLog []ExecutionLog
}
```

---

## 5. Integration with Existing Projects

### 5.1 Reuse from `multi-agent-discuss`

| Component | Integration |
|-----------|-------------|
| `OrchestratorAgent` | Extend `Process()` to add evolution |
| `LLMDecomposer` | Reuse as-is for decomposition |
| `Dispatcher` | Reuse for peer communication |
| `raceResults()` | Reuse for parallel execution |

### 5.2 Reuse from `agent-islands`

| Component | Integration |
|-----------|-------------|
| `AgentHub` | As underlying task dispatcher |
| `WorkflowOrchestrator` | As high-level workflow coordinator |
| `Adapters` | For NewsHub, StockAnalyzer integration |

### 5.3 Reuse from `a2a-router`

| Component | Integration |
|-----------|-------------|
| `A2ARouter` | For cross-protocol message routing |
| Priority queues | For task prioritization |

---

## 6. File Structure

```
80-PROJECTS/self-evolving-orchestrator/
├── go/
│   ├── cmd/
│   │   └── orchestrator/
│   │       └── main.go              # Entry point
│   ├── orchestrator/
│   │   ├── orchestrator.go         # Main orchestrator interface
│   │   ├── evolution_loop.go       # Self-evolution cycle
│   │   ├── self_evolver.go         # Strategy refinement
│   │   ├── result_ranker.go        # Result scoring
│   │   ├── decomposer.go           # LLM decomposition
│   │   └── peer_registry.go        # Peer management
│   ├── proto/
│   │   ├── adaptation.go           # TS-Go IPC protocol
│   │   └── messages.go             # Message types
│   └── go.mod
├── ts/
│   ├── src/
│   │   ├── adapters/
│   │   │   ├── mcp-adapter.ts
│   │   │   └── a2a-adapter.ts
│   │   └── agent-islands/          # From existing project
│   └── package.json
├── integration/
│   ├── test_workflow.go
│   └── benchmarks_test.go
└── README.md
```

---

## 7. API

### 7.1 HTTP API Endpoints

```
POST /api/v1/orchestrate
  Body: { "task": "analyze stock market trends for A-share", "options": {...} }
  Response: { "result": "...", "iterations": 2, "quality_score": 0.82 }

POST /api/v1/orchestrate/evolve
  Body: { "task": "...", "max_iterations": 5, "threshold": 0.8 }
  Response: Stream of EvolutionResult

GET /api/v1/peers
  Response: { "peers": [...], "total": 5 }

POST /api/v1/peers/register
  Body: { "id": "...", "capabilities": ["stock", "news"] }
```

### 7.2 MCP Tools

| Tool | Description |
|------|-------------|
| `orchestrator_process` | Submit task for orchestration |
| `orchestrator_evolve` | Submit task with self-evolution |
| `orchestrator_status` | Get current status |
| `orchestrator_peers` | List registered peers |

---

## 8. Testing Strategy

### 8.1 Unit Tests

- `decomposer_test.go` - Test decomposition quality
- `self_evolver_test.go` - Test strategy selection
- `result_ranker_test.go` - Test scoring accuracy

### 8.2 Integration Tests

- `integration_test.go` - End-to-end workflow
- Mock LLM responses for deterministic testing

### 8.3 Benchmarks

- Compare evolution vs non-evolution quality
- Latency comparison
- Token cost comparison

---

## 9. References

1. **SEMA Framework** - Self-Evolving Multi-Agent Framework
   - Dynamic observation pruning
   - Hybrid knowledge-memory mechanism

2. **AutoAgent** - Adaptive Autonomous Agents
   - Evolving cognition
   - Elastic memory orchestration

3. **Existing Implementation**
   - `multi-agent-discuss/OrchestratorAgent`
   - `agent-islands/WorkflowOrchestrator`
   - `a2a-router/A2ARouter`

---

## 10. Next Steps

1. ~~Design approval~~ ✓
2. Create project structure
3. Implement Go core components
4. Implement TypeScript adapters
5. Integration testing
6. Documentation

---

**Revision History:**
- 2026-03-28: Initial draft
