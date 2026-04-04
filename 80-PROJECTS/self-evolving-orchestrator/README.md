# Self-Evolving Orchestrator

A Go-based task orchestration system that self-evolves its decomposition strategy based on execution outcomes. Uses a strategy pool, scoring feedback loop, and overlap detection to refine task decomposition.


## 安装

```bash
npm install
```

## Architecture

```
Orchestrator
├── EvolutionLoop       — Self-evolution core; runs iterations with strategy refinement
├── SelfEvolver        — Analyzes results, decides when/how to refine decomposition
├── ResultRanker       — Scores results by quality, latency, success, relevance
└── DecomposerWrapper  — Applies strategy hints to LLM or simple decomposition
```

### Components

**Orchestrator** (`orchestrator.go`) — Entry point. Provides `Process` (with self-evolution) and `ProcessBasic` (single-shot).

**EvolutionLoop** (`evolution_loop.go`) — Runs up to `MaxIterations` cycles. Each iteration: decompose → execute subtasks in parallel → rank results → record in SelfEvolver → decide whether to refine. Exits when quality is acceptable (`!shouldRefine && score >= threshold`) or max iterations reached.

**SelfEvolver** (`self_evolver.go`) — Maintains:
- `history` — all `EvolutionRecord` entries
- `strategyPool` — 6 strategies (coarse/medium/fine × fast/strong)
- `currentStrategy` — next strategy index

`ShouldRefine` returns true when: all subtasks failed, score < 0.5, or excessive output overlap detected (cosine similarity > 0.85 via n-gram fingerprints).

**ResultRanker** (`result_ranker.go`) — Scores each subtask result across four dimensions:

| Dimension | Score | Weight (default) |
|-----------|-------|-----------------|
| Quality | Output length / 1000, halved on error | 0.35 |
| Latency | 1 − duration/30s | 0.15 |
| Success | 1 if successful, 0 otherwise | 0.35 |
| Relevance | Keyword overlap (subtask vs output) | 0.15 |

`AggregateAndScore` computes a weighted mean of ranked results (reciprocal-rank weighting).

**DecomposerWrapper** (`decomposer.go`) — Wraps a base decomposer. Strategy hints modify the prompt by granularity (coarse/medium/fine → major/detailed/atomic steps). Base decomposer falls back to `SimpleDecomposer` (sentence split) on error.

**DecomposeStrategy** (`types.go`) — Defines `Granularity`, `ModelHint` ("fast"/"strong"), and `MaxSubtasks`.

## Self-Evolution Loop

```
Run(task, opts)
  └─ for i in 0..MaxIterations-1
       ├─ DecomposeWithStrategy(task, strategy[i])
       ├─ executeSubtasks()         ← parallel goroutines
       ├─ ranker.Rank(results)
       ├─ evolver.RecordResult()    ← store history
       ├─ evolver.ShouldRefine()     ← check overlap, score, failures
       └─ if !shouldRefine && score >= threshold  ← BREAK
          else strategy = evolver.GetNextStrategy()  ← refine
```

Refinement signals: all subtasks failed, score < 0.5, output cosine similarity > 0.85 (overlap).

## Scoring Weights

```go
ScoringWeights{
    Quality:   0.35,
    Latency:   0.15,
    Success:   0.35,
    Relevance: 0.15,
}
```

## Usage

```go
decomposer := orchestrator.NewLLMBasedDecomposer("http://localhost:11434", "llama3.2:1b")
executor := func(subtask string) orchestrator.ExecutionResult {
    // execute subtask, return result
}
orch := orchestrator.NewOrchestrator(
    orchestrator.NewDecomposerWrapper(decomposer),
    executor,
)
result, err := orch.Process(ctx, "your task here", &orchestrator.EvolutionOptions{
    MaxIterations:    3,
    QualityThreshold: 0.7,
    Timeout:          60 * time.Second,
})
```

## Testing

```bash
cd go/orchestrator
go test ./...
```

## Project Structure

```
go/orchestrator/
├── agent.go          — Peer agent registration and messaging
├── decomposer.go     — LLM and simple decomposition + wrapper
├── evolution_loop.go — Self-evolution iteration loop
├── executor.go       — Subtask execution environment
├── orchestrator.go   — Main entry point
├── peer_registry.go  — Peer registry
├── provider.go       — LLM provider
├── result_ranker.go  — Scoring and ranking
├── self_evolver.go   — Strategy pool + ShouldRefine + overlap detection
├── swarm.go          — Swarm coordination
└── types.go          — All type definitions
```
