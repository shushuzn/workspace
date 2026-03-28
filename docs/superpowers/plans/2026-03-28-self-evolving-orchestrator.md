# Self-Evolving Orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a hybrid Go/TypeScript self-evolving task orchestrator that decomposes tasks via LLM, executes them in parallel, evaluates results, and refines strategy iteratively until quality threshold is met.

**Architecture:** Go core engine handles task decomposition, self-evolution, and result ranking. TypeScript protocol adapters (MCP/A2A) bridge to existing agent-islands execution layer. Execution happens via injected function into Go (simpler IPC), with future option for remote TS agent invocation.

**Tech Stack:** Go 1.26+, TypeScript/Node.js, MCP SDK, Ollama (for local LLM)

---

## Phase 1: Project Setup

### Task 1: Create Project Structure

**Files:**
- Create: `80-PROJECTS/self-evolving-orchestrator/go/go.mod`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/cmd/orchestrator/main.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/types.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/orchestrator.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/evolution_loop.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/self_evolver.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/result_ranker.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/peer_registry.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/decomposer.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/proto/messages.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/ts/package.json`
- Create: `80-PROJECTS/self-evolving-orchestrator/ts/src/adapters/mcp-adapter.ts`
- Create: `80-PROJECTS/self-evolving-orchestrator/ts/src/adapters/a2a-adapter.ts`
- Create: `80-PROJECTS/self-evolving-orchestrator/integration/test_workflow.go`

---

### Task 2: Implement Go Core Types

**Files:**
- Modify: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/types.go`

```go
package orchestrator

// Granularity represents decomposition granularity
type Granularity int

const (
    GranularityCoarse Granularity = iota
    GranularityMedium
    GranularityFine
)

func (g Granularity) String() string {
    switch g {
    case GranularityCoarse:
        return "coarse"
    case GranularityMedium:
        return "medium"
    case GranularityFine:
        return "fine"
    default:
        return "unknown"
    }
}

// DecomposeStrategy defines how to decompose a task
type DecomposeStrategy struct {
    Name         string
    Granularity  Granularity
    ModelHint    string // "fast" or "strong"
    MaxSubtasks  int
}

// DefaultStrategies returns the default strategy pool
func DefaultStrategies() []DecomposeStrategy {
    return []DecomposeStrategy{
        {Name: "coarse-fast", Granularity: GranularityCoarse, ModelHint: "fast", MaxSubtasks: 3},
        {Name: "coarse-strong", Granularity: GranularityCoarse, ModelHint: "strong", MaxSubtasks: 3},
        {Name: "medium-fast", Granularity: GranularityMedium, ModelHint: "fast", MaxSubtasks: 5},
        {Name: "medium-strong", Granularity: GranularityMedium, ModelHint: "strong", MaxSubtasks: 5},
        {Name: "fine-fast", Granularity: GranularityFine, ModelHint: "fast", MaxSubtasks: 10},
        {Name: "fine-strong", Granularity: GranularityFine, ModelHint: "strong", MaxSubtasks: 10},
    }
}

// EvolutionOptions configures the evolution behavior
type EvolutionOptions struct {
    MaxIterations   int
    QualityThreshold float64
    Timeout        time.Duration
}

// ExecutionResult represents the result of executing a subtask
type ExecutionResult struct {
    Subtask   string
    Output    string
    Success   bool
    Error     string
    Duration  time.Duration
    Timestamp time.Time
}

// EvolutionRecord records one evolution iteration
type EvolutionRecord struct {
    Task       string
    Subtasks   []string
    Results    []ExecutionResult
    Score      float64
    Strategy   DecomposeStrategy
}

// EvolutionResultFinal is the final output of the evolution loop
type EvolutionResultFinal struct {
    FinalTask    string
    Subtasks    []string
    Results     []RankedResult
    Iterations  int
    FinalScore float64
    Converged   bool
}

// ScoringWeights defines the weight for each scoring dimension
type ScoringWeights struct {
    Quality    float64
    Latency   float64
    Success   float64
    Relevance float64 // relevance to original task
}

// DefaultScoringWeights returns equal weights
func DefaultScoringWeights() ScoringWeights {
    return ScoringWeights{
        Quality:    0.35,
        Latency:   0.15,
        Success:   0.35,
        Relevance: 0.15,
    }
}
```

- [ ] **Step 1: Create types.go with above content**

```bash
cat > 80-PROJECTS/self-evolving-orchestrator/go/orchestrator/types.go << 'EOF'
package orchestrator

import "time"

// Granularity represents decomposition granularity
type Granularity int

const (
    GranularityCoarse Granularity = iota
    GranularityMedium
    GranularityFine
)

func (g Granularity) String() string {
    switch g {
    case GranularityCoarse:
        return "coarse"
    case GranularityMedium:
        return "medium"
    case GranularityFine:
        return "fine"
    default:
        return "unknown"
    }
}

// DecomposeStrategy defines how to decompose a task
type DecomposeStrategy struct {
    Name        string
    Granularity Granularity
    ModelHint   string // "fast" or "strong"
    MaxSubtasks int
}

// DefaultStrategies returns the default strategy pool
func DefaultStrategies() []DecomposeStrategy {
    return []DecomposeStrategy{
        {Name: "coarse-fast", Granularity: GranularityCoarse, ModelHint: "fast", MaxSubtasks: 3},
        {Name: "coarse-strong", Granularity: GranularityCoarse, ModelHint: "strong", MaxSubtasks: 3},
        {Name: "medium-fast", Granularity: GranularityMedium, ModelHint: "fast", MaxSubtasks: 5},
        {Name: "medium-strong", Granularity: GranularityMedium, ModelHint: "strong", MaxSubtasks: 5},
        {Name: "fine-fast", Granularity: GranularityFine, ModelHint: "fast", MaxSubtasks: 10},
        {Name: "fine-strong", Granularity: GranularityFine, ModelHint: "strong", MaxSubtasks: 10},
    }
}

// EvolutionOptions configures the evolution behavior
type EvolutionOptions struct {
    MaxIterations    int
    QualityThreshold float64
    Timeout         time.Duration
}

// ExecutionResult represents the result of executing a subtask
type ExecutionResult struct {
    Subtask   string
    Output    string
    Success   bool
    Error     string
    Duration  time.Duration
    Timestamp time.Time
}

// EvolutionRecord records one evolution iteration
type EvolutionRecord struct {
    Task     string
    Subtasks []string
    Results  []ExecutionResult
    Score    float64
    Strategy DecomposeStrategy
}

// EvolutionResultFinal is the final output of the evolution loop
type EvolutionResultFinal struct {
    FinalTask   string
    Subtasks   []string
    Results    []RankedResult
    Iterations int
    FinalScore float64
    Converged  bool
}

// ScoringWeights defines the weight for each scoring dimension
type ScoringWeights struct {
    Quality    float64
    Latency   float64
    Success   float64
    Relevance float64 // relevance to original task
}

// DefaultScoringWeights returns equal weights
func DefaultScoringWeights() ScoringWeights {
    return ScoringWeights{
        Quality:    0.35,
        Latency:   0.15,
        Success:   0.35,
        Relevance: 0.15,
    }
}
EOF
```

- [ ] **Step 2: Run go build to verify syntax**

```bash
cd 80-PROJECTS/self-evolving-orchestrator/go && go build ./...
```
Expected: no output (success)

- [ ] **Step 3: Commit**

```bash
git add 80-PROJECTS/self-evolving-orchestrator/go/orchestrator/types.go
git commit -m "feat(orchestrator): add core types for self-evolving orchestrator"
```

---

### Task 3: Implement ResultRanker

**Files:**
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/result_ranker.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/result_ranker_test.go`

```go
package orchestrator

import (
    "math"
    "sort"
    "time"
)

// RankedResult pairs an execution result with its score
type RankedResult struct {
    Result     *ExecutionResult
    TotalScore float64
    Breakdown ScoreBreakdown
}

// ScoreBreakdown shows individual dimension scores
type ScoreBreakdown struct {
    QualityScore  float64
    LatencyScore  float64
    SuccessScore float64
}

// ResultRanker scores and ranks execution results
type ResultRanker struct {
    weights ScoringWeights
}

// NewResultRanker creates a ranker with given weights
func NewResultRanker(weights ScoringWeights) *ResultRanker {
    return &ResultRanker{weights: weights}
}

// NewDefaultResultRanker creates a ranker with default weights
func NewDefaultResultRanker() *ResultRanker {
    return NewResultRanker(DefaultScoringWeights())
}

// Rank scores and sorts results
func (r *ResultRanker) Rank(results []ExecutionResult) []RankedResult {
    ranked := make([]RankedResult, len(results))
    for i, result := range results {
        breakdown := r.scoreBreakdown(&result)
        total := r.weights.Quality*breakdown.QualityScore +
            r.weights.Latency*breakdown.LatencyScore +
            r.weights.Success*breakdown.SuccessScore
        ranked[i] = RankedResult{
            Result:     &results[i],
            TotalScore: total,
            Breakdown:  breakdown,
        }
    }
    sort.Slice(ranked, func(i, j int) bool {
        return ranked[i].TotalScore > ranked[j].TotalScore
    })
    return ranked
}

// AggregateAndScore computes a single quality score from all subtask results
func (r *ResultRanker) AggregateAndScore(results []ExecutionResult) float64 {
    if len(results) == 0 {
        return 0.0
    }
    ranked := r.Rank(results)
    // Weighted average, prioritizing higher-ranked results
    var totalScore float64
    var weightSum float64
    for i, rr := range ranked {
        weight := 1.0 / math.Max(1.0, float64(i+1)) // 1st gets weight 1, 2nd gets 0.5, etc.
        totalScore += rr.TotalScore * weight
        weightSum += weight
    }
    return totalScore / weightSum
}

func (r *ResultRanker) scoreBreakdown(result *ExecutionResult) ScoreBreakdown {
    var qualityScore float64
    if result.Success {
        // Quality based on output length (longer = potentially more thorough)
        // and absence of error indicators
        qualityScore = math.Min(1.0, float64(len(result.Output))/1000.0)
        if len(result.Error) > 0 {
            qualityScore *= 0.5
        }
    }

    var latencyScore float64
    // Lower latency is better, cap at 30 seconds
    if result.Duration > 0 {
        latencyScore = math.Max(0, 1.0-result.Duration.Seconds()/30.0)
    }

    var successScore float64
    if result.Success {
        successScore = 1.0
    }

    return ScoreBreakdown{
        QualityScore:  qualityScore,
        LatencyScore: latencyScore,
        SuccessScore: successScore,
    }
}
```

- [ ] **Step 1: Write the failing test**

```go
// result_ranker_test.go
package orchestrator

import (
    "testing"
    "time"
)

func TestResultRanker_Rank(t *testing.T) {
    ranker := NewDefaultResultRanker()
    results := []ExecutionResult{
        {Subtask: "task1", Output: "short", Success: true, Duration: 1 * time.Second},
        {Subtask: "task2", Output: "much longer output with more content", Success: true, Duration: 5 * time.Second},
        {Subtask: "task3", Output: "", Success: false, Error: "failed", Duration: 2 * time.Second},
    }

    ranked := ranker.Rank(results)

    if len(ranked) != 3 {
        t.Errorf("expected 3 results, got %d", len(ranked))
    }
    // Successful results should rank higher than failed
    if ranked[0].Result.Success != true {
        t.Errorf("expected first result to be successful")
    }
}

func TestResultRanker_AggregateAndScore(t *testing.T) {
    ranker := NewDefaultResultRanker()
    results := []ExecutionResult{
        {Subtask: "task1", Output: "good result", Success: true, Duration: 1 * time.Second},
        {Subtask: "task2", Output: "also good", Success: true, Duration: 2 * time.Second},
    }

    score := ranker.AggregateAndScore(results)
    if score <= 0 || score > 1 {
        t.Errorf("expected score between 0 and 1, got %f", score)
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd 80-PROJECTS/self-evolving-orchestrator/go
go test ./orchestrator/... -run TestResultRanker -v
```
Expected: FAIL (function not defined)

- [ ] **Step 3: Write the implementation above**

- [ ] **Step 4: Run test to verify it passes**

```bash
go test ./orchestrator/... -run TestResultRanker -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add 80-PROJECTS/self-evolving-orchestrator/go/orchestrator/result_ranker.go
git add 80-PROJECTS/self-evolving-orchestrator/go/orchestrator/result_ranker_test.go
git commit -m "feat(orchestrator): add ResultRanker for scoring execution results"
```

---

### Task 4: Implement SelfEvolver

**Files:**
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/self_evolver.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/self_evolver_test.go`

```go
package orchestrator

import (
    "context"
    "fmt"
)

// SelfEvolver analyzes execution results and adjusts decomposition strategy
type SelfEvolver struct {
    history         []EvolutionRecord
    strategyPool    []DecomposeStrategy
    currentStrategy int
}

// NewSelfEvolver creates a SelfEvolver with default strategies
func NewSelfEvolver() *SelfEvolver {
    return &SelfEvolver{
        history:         []EvolutionRecord{},
        strategyPool:    DefaultStrategies(),
        currentStrategy: 0,
    }
}

// ShouldRefine determines if the decomposition should be refined
// Returns (shouldRefine, reason)
func (s *SelfEvolver) ShouldRefine(ctx context.Context, record *EvolutionRecord) (bool, string) {
    // Refine if all subtasks failed
    allFailed := true
    for _, r := range record.Results {
        if r.Success {
            allFailed = false
            break
        }
    }
    if allFailed && len(record.Results) > 0 {
        return true, "all subtasks failed"
    }

    // Refine if score below threshold
    if record.Score < 0.5 {
        return true, fmt.Sprintf("score %f below threshold 0.5", record.Score)
    }

    // Refine if excessive overlap (detected by similar outputs)
    if s.detectOverlap(record.Results) {
        return true, "excessive overlap between subtasks"
    }

    return false, "quality acceptable"
}

// GetNextStrategy returns the next strategy in the pool
func (s *SelfEvolver) GetNextStrategy() DecomposeStrategy {
    if s.currentStrategy >= len(s.strategyPool) {
        s.currentStrategy = len(s.strategyPool) - 1
    }
    strategy := s.strategyPool[s.currentStrategy]
    s.currentStrategy++
    return strategy
}

// RecordResult stores an evolution record for future analysis
func (s *SelfEvolver) RecordResult(record *EvolutionRecord) {
    s.history = append(s.history, *record)
}

// GetHistory returns the evolution history
func (s *SelfEvolver) GetHistory() []EvolutionRecord {
    return s.history
}

// ResetHistory clears the evolution history
func (s *SelfEvolver) ResetHistory() {
    s.history = []EvolutionRecord{}
    s.currentStrategy = 0
}

func (s *SelfEvolver) detectOverlap(results []ExecutionResult) bool {
    if len(results) < 2 {
        return false
    }
    // Simple overlap detection: check if any two outputs are >80% similar
    // This is a placeholder - real implementation would use edit distance or embeddings
    return false
}
```

- [ ] **Step 1: Write the failing test**

```go
// self_evolver_test.go
package orchestrator

import (
    "context"
    "testing"
    "time"
)

func TestSelfEvolver_ShouldRefine(t *testing.T) {
    evolver := NewSelfEvolver()

    // Test: all failed should trigger refine
    record := &EvolutionRecord{
        Task:   "test task",
        Results: []ExecutionResult{
            {Success: false, Error: "failed"},
            {Success: false, Error: "failed"},
        },
        Score: 0.0,
    }

    shouldRefine, reason := evolver.ShouldRefine(context.Background(), record)
    if !shouldRefine {
        t.Errorf("expected ShouldRefine=true for all failed tasks, got false")
    }
    if reason != "all subtasks failed" {
        t.Errorf("expected reason 'all subtasks failed', got '%s'", reason)
    }
}

func TestSelfEvolver_GetNextStrategy(t *testing.T) {
    evolver := NewSelfEvolver()

    strategy := evolver.GetNextStrategy()
    if strategy.Name != "coarse-fast" {
        t.Errorf("expected first strategy 'coarse-fast', got '%s'", strategy.Name)
    }

    strategy2 := evolver.GetNextStrategy()
    if strategy2.Name != "coarse-strong" {
        t.Errorf("expected second strategy 'coarse-strong', got '%s'", strategy2.Name)
    }
}

func TestSelfEvolver_RecordResult(t *testing.T) {
    evolver := NewSelfEvolver()
    record := &EvolutionRecord{
        Task:   "test",
        Results: []ExecutionResult{},
        Score:   0.8,
    }

    evolver.RecordResult(record)

    history := evolver.GetHistory()
    if len(history) != 1 {
        t.Errorf("expected 1 history record, got %d", len(history))
    }
}
```

- [ ] **Step 2: Run test to verify it fails**

```bash
go test ./orchestrator/... -run TestSelfEvolver -v
```
Expected: FAIL

- [ ] **Step 3: Write the implementation above**

- [ ] **Step 4: Run test to verify it passes**

```bash
go test ./orchestrator/... -run TestSelfEvolver -v
```
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add 80-PROJECTS/self-evolving-orchestrator/go/orchestrator/self_evolver.go
git add 80-PROJECTS/self-evolving-orchestrator/go/orchestrator/self_evolver_test.go
git commit -m "feat(orchestrator): add SelfEvolver for strategy refinement"
```

---

### Task 5: Implement Decomposer (wrapper around existing)

**Files:**
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/decomposer.go`

```go
package orchestrator

import (
    "context"
    "fmt"
    "strings"
)

// LLMDecomposer is the interface for task decomposition
type LLMDecomposer interface {
    Decompose(ctx context.Context, task string) ([]string, error)
}

// Decomposer is a type alias for LLMDecomposer for brevity
type Decomposer = LLMDecomposer

// SimpleDecomposer is a basic implementation that splits on newlines
// This is a fallback; real implementation uses LLM
type SimpleDecomposer struct{}

func (d *SimpleDecomposer) Decompose(ctx context.Context, task string) ([]string, error) {
    // Simple split - real impl would use Ollama/LLM
    lines := strings.Split(strings.TrimSpace(task), ".")
    var subtasks []string
    for _, line := range lines {
        line = strings.TrimSpace(line)
        if len(line) > 10 {
            subtasks = append(subtasks, line+".")
        }
    }
    if len(subtasks) == 0 {
        return []string{task}, nil
    }
    return subtasks, nil
}

// LLMBasedDecomposer uses Ollama for decomposition
type LLMBasedDecomposer struct {
    endpoint string
    model    string
}

func NewLLMBasedDecomposer(endpoint, model string) *LLMBasedDecomposer {
    return &LLMBasedDecomposer{
        endpoint: endpoint,
        model:    model,
    }
}

func (d *LLMBasedDecomposer) Decompose(ctx context.Context, task string) ([]string, error) {
    // TODO: Implement Ollama API call
    // For now, fall back to simple decomposer
    decomposer := &SimpleDecomposer{}
    return decomposer.Decompose(ctx, task)
}

// DecomposerWrapper wraps a decomposer with strategy hints
type DecomposerWrapper struct {
    base Decomposer
}

func NewDecomposerWrapper(base Decomposer) *DecomposerWrapper {
    return &DecomposerWrapper{base: base}
}

func (w *DecomposerWrapper) DecomposeWithStrategy(ctx context.Context, task string, strategy DecomposeStrategy) ([]string, error) {
    // Modify the task prompt based on strategy
    modifiedTask := task

    switch strategy.Granularity {
    case GranularityCoarse:
        modifiedTask = fmt.Sprintf("Break this into %d major steps: %s", strategy.MaxSubtasks, task)
    case GranularityMedium:
        modifiedTask = fmt.Sprintf("Break this into %d detailed steps: %s", strategy.MaxSubtasks, task)
    case GranularityFine:
        modifiedTask = fmt.Sprintf("Break this into %d small, atomic steps: %s", strategy.MaxSubtasks, task)
    }

    subtasks, err := w.base.Decompose(ctx, modifiedTask)
    if err != nil {
        return nil, err
    }

    // Limit to max subtasks
    if len(subtasks) > strategy.MaxSubtasks {
        subtasks = subtasks[:strategy.MaxSubtasks]
    }

    return subtasks, nil
}
```

- [ ] **Step 1: Write the implementation**

- [ ] **Step 2: Write a simple test**

```go
func TestDecomposerWrapper_DecomposeWithStrategy(t *testing.T) {
    base := &SimpleDecomposer{}
    wrapper := NewDecomposerWrapper(base)

    strategy := DecomposeStrategy{
        Name:        "test",
        Granularity: GranularityMedium,
        ModelHint:   "fast",
        MaxSubtasks: 3,
    }

    subtasks, err := wrapper.DecomposeWithStrategy(context.Background(), "This is a test task. This is another sentence.", strategy)
    if err != nil {
        t.Errorf("unexpected error: %v", err)
    }
    if len(subtasks) > strategy.MaxSubtasks {
        t.Errorf("expected at most %d subtasks, got %d", strategy.MaxSubtasks, len(subtasks))
    }
}
```

- [ ] **Step 3: Run test to verify it passes**

- [ ] **Step 4: Commit**

---

### Task 6: Implement EvolutionLoop

**Files:**
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/evolution_loop.go`
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/evolution_loop_test.go`

```go
package orchestrator

import (
    "context"
    "fmt"
    "sync"
    "time"
)

// EvolutionLoop implements the self-evolution cycle
type EvolutionLoop struct {
    decomposer *DecomposerWrapper
    evolver    *SelfEvolver
    ranker     *ResultRanker
    executor   func(subtask string) ExecutionResult
}

// NewEvolutionLoop creates a new evolution loop
func NewEvolutionLoop(
    decomposer *DecomposerWrapper,
    evolver *SelfEvolver,
    ranker *ResultRanker,
    executor func(subtask string) ExecutionResult,
) *EvolutionLoop {
    return &EvolutionLoop{
        decomposer: decomposer,
        evolver:    evolver,
        ranker:     ranker,
        executor:   executor,
    }
}

// Run executes the evolution loop
func (e *EvolutionLoop) Run(ctx context.Context, task string, opts *EvolutionOptions) (*EvolutionResultFinal, error) {
    if opts == nil {
        opts = &EvolutionOptions{
            MaxIterations:    3,
            QualityThreshold: 0.7,
            Timeout:          60 * time.Second,
        }
    }

    var finalResult *EvolutionResultFinal
    currentTask := task
    strategy := e.evolver.GetNextStrategy()

    for i := 0; i < opts.MaxIterations; i++ {
        select {
        case <-ctx.Done():
            return nil, ctx.Err()
        default:
        }

        // Decompose
        subtasks, err := e.decomposer.DecomposeWithStrategy(ctx, currentTask, strategy)
        if err != nil {
            return nil, fmt.Errorf("decompose failed: %w", err)
        }

        // Execute subtasks in parallel
        results := e.executeSubtasks(subtasks)

        // Score results
        ranked := e.ranker.Rank(results)
        aggregateScore := e.ranker.AggregateAndScore(results)

        // Record evolution
        record := &EvolutionRecord{
            Task:     currentTask,
            Subtasks: subtasks,
            Results:  results,
            Score:    aggregateScore,
            Strategy: strategy,
        }
        e.evolver.RecordResult(record)

        // Check if we should refine
        shouldRefine, _ := e.evolver.ShouldRefine(ctx, record)

        if !shouldRefine || aggregateScore >= opts.QualityThreshold {
            finalResult = &EvolutionResultFinal{
                FinalTask:   currentTask,
                Subtasks:    subtasks,
                Results:     ranked,
                Iterations:  i + 1,
                FinalScore:  aggregateScore,
                Converged:   aggregateScore >= opts.QualityThreshold,
            }
            break
        }

        // Get next strategy for refinement
        strategy = e.evolver.GetNextStrategy()
    }

    if finalResult == nil {
        finalResult = &EvolutionResultFinal{
            FinalTask:   currentTask,
            Iterations:  opts.MaxIterations,
            FinalScore:  0,
            Converged:   false,
        }
    }

    return finalResult, nil
}

func (e *EvolutionLoop) executeSubtasks(subtasks []string) []ExecutionResult {
    results := make([]ExecutionResult, len(subtasks))
    var wg sync.WaitGroup

    for i, subtask := range subtasks {
        wg.Add(1)
        go func(idx int, st string) {
            defer wg.Done()
            start := time.Now()
            result := e.executor(st)
            result.Subtask = st
            result.Duration = time.Since(start)
            results[idx] = result
        }(i, subtask)
    }

    wg.Wait()
    return results
}
```

- [ ] **Step 1: Write the implementation**

- [ ] **Step 2: Write test with mock executor**

```go
func TestEvolutionLoop_Run(t *testing.T) {
    decomposer := NewDecomposerWrapper(&SimpleDecomposer{})
    evolver := NewSelfEvolver()
    ranker := NewDefaultResultRanker()

    mockExecutor := func(subtask string) ExecutionResult {
        return ExecutionResult{
            Output:  "executed: " + subtask,
            Success: true,
        }
    }

    loop := NewEvolutionLoop(decomposer, evolver, ranker, mockExecutor)

    result, err := loop.Run(context.Background(), "test task one two three", &EvolutionOptions{
        MaxIterations:    3,
        QualityThreshold: 0.5,
        Timeout:          10 * time.Second,
    })

    if err != nil {
        t.Errorf("unexpected error: %v", err)
    }
    if result == nil {
        t.Fatal("expected result, got nil")
    }
    if result.Iterations < 1 {
        t.Errorf("expected at least 1 iteration, got %d", result.Iterations)
    }
}
```

- [ ] **Step 3: Run test**

- [ ] **Step 4: Commit**

---

### Task 7: Implement PeerRegistry

**Files:**
- Create: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/peer_registry.go`

```go
package orchestrator

import (
    "sync"
    "time"
)

// AgentStatus represents peer status
type AgentStatus string

const (
    StatusIdle    AgentStatus = "idle"
    StatusActive  AgentStatus = "active"
    StatusError   AgentStatus = "error"
    StatusOffline AgentStatus = "offline"
)

// PeerInfo holds peer agent information
type PeerInfo struct {
    ID           string
    Name         string
    Capabilities []string
    Status       AgentStatus
    Load         float64
    LastSeen     time.Time
}

// PeerRegistry manages available peer agents
type PeerRegistry struct {
    peers map[string]*PeerInfo
    mu    sync.RWMutex
}

// NewPeerRegistry creates a new peer registry
func NewPeerRegistry() *PeerRegistry {
    return &PeerRegistry{
        peers: make(map[string]*PeerInfo),
    }
}

// Register adds or updates a peer
func (r *PeerRegistry) Register(peer *PeerInfo) {
    r.mu.Lock()
    defer r.mu.Unlock()
    peer.LastSeen = time.Now()
    r.peers[peer.ID] = peer
}

// Unregister removes a peer
func (r *PeerRegistry) Unregister(id string) bool {
    r.mu.Lock()
    defer r.mu.Unlock()
    if _, exists := r.peers[id]; exists {
        delete(r.peers, id)
        return true
    }
    return false
}

// Get retrieves a peer by ID
func (r *PeerRegistry) Get(id string) (*PeerInfo, bool) {
    r.mu.RLock()
    defer r.mu.RUnlock()
    peer, exists := r.peers[id]
    return peer, exists
}

// List returns all peers
func (r *PeerRegistry) List() []*PeerInfo {
    r.mu.RLock()
    defer r.mu.RUnlock()
    peers := make([]*PeerInfo, 0, len(r.peers))
    for _, peer := range r.peers {
        peers = append(peers, peer)
    }
    return peers
}

// ListByCapability returns peers with a specific capability
func (r *PeerRegistry) ListByCapability(capability string) []*PeerInfo {
    r.mu.RLock()
    defer r.mu.RUnlock()
    var peers []*PeerInfo
    for _, peer := range r.peers {
        for _, cap := range peer.Capabilities {
            if cap == capability {
                peers = append(peers, peer)
                break
            }
        }
    }
    return peers
}

// UpdateStatus updates a peer's status
func (r *PeerRegistry) UpdateStatus(id string, status AgentStatus) bool {
    r.mu.Lock()
    defer r.mu.Unlock()
    if peer, exists := r.peers[id]; exists {
        peer.Status = status
        peer.LastSeen = time.Now()
        return true
    }
    return false
}
```

- [ ] **Step 1: Write implementation**

- [ ] **Step 2: Write test**

- [ ] **Step 3: Run test**

- [ ] **Step 4: Commit**

---

### Task 8: Implement Orchestrator (main entry point)

**Files:**
- Modify: `80-PROJECTS/self-evolving-orchestrator/go/orchestrator/orchestrator.go`

```go
package orchestrator

import (
    "context"
)

// Orchestrator is the main entry point for task orchestration
type Orchestrator struct {
    loop     *EvolutionLoop
    registry *PeerRegistry
}

// NewOrchestrator creates a new orchestrator
func NewOrchestrator(
    decomposer *DecomposerWrapper,
    executor func(subtask string) ExecutionResult,
) *Orchestrator {
    evolver := NewSelfEvolver()
    ranker := NewDefaultResultRanker()
    loop := NewEvolutionLoop(decomposer, evolver, ranker, executor)
    registry := NewPeerRegistry()

    return &Orchestrator{
        loop:     loop,
        registry: registry,
    }
}

// Process handles a task with self-evolution
func (o *Orchestrator) Process(ctx context.Context, task string, opts *EvolutionOptions) (*EvolutionResultFinal, error) {
    return o.loop.Run(ctx, task, opts)
}

// ProcessBasic handles a task without self-evolution
func (o *Orchestrator) ProcessBasic(ctx context.Context, task string) ([]ExecutionResult, error) {
    decomposer := NewDecomposerWrapper(&SimpleDecomposer{})
    subtasks, err := decomposer.DecomposeWithStrategy(ctx, task, DecomposeStrategy{MaxSubtasks: 5})
    if err != nil {
        return nil, err
    }

    results := make([]ExecutionResult, len(subtasks))
    for i, st := range subtasks {
        results[i] = ExecutionResult{Subtask: st, Success: true}
    }
    return results, nil
}

// Registry returns the peer registry
func (o *Orchestrator) Registry() *PeerRegistry {
    return o.registry
}
```

- [ ] **Step 1: Write implementation**

- [ ] **Step 2: Write test**

- [ ] **Step 3: Run test**

- [ ] **Step 4: Commit**

---

### Task 9: Create Main Entry Point

**Files:**
- Create: `80-PROJECTS/self-evolving-orchestrator/go/cmd/orchestrator/main.go`

```go
package main

import (
    "context"
    "flag"
    "fmt"
    "log"
    "time"

    "github.com/openclaw/self-evolving-orchestrator/go/orchestrator"
)

var (
    task        string
    maxIter     int
    threshold   float64
    timeoutSec  int
)

func main() {
    flag.StringVar(&task, "task", "", "Task to orchestrate")
    flag.IntVar(&maxIter, "max-iter", 3, "Max evolution iterations")
    flag.Float64Var(&threshold, "threshold", 0.7, "Quality threshold")
    flag.IntVar(&timeoutSec, "timeout", 60, "Timeout in seconds")
    flag.Parse()

    if task == "" {
        log.Fatal("task is required")
    }

    // Create decomposer
    decomposer := orchestrator.NewDecomposerWrapper(orchestrator.NewLLMBasedDecomposer("http://localhost:11434", "llama3"))

    // Create mock executor for testing
    executor := func(subtask string) orchestrator.ExecutionResult {
        time.Sleep(100 * time.Millisecond) // Simulate work
        return orchestrator.ExecutionResult{
            Subtask: subtask,
            Output:  "executed: " + subtask,
            Success: true,
        }
    }

    // Create orchestrator
    o := orchestrator.NewOrchestrator(decomposer, executor)

    // Run
    ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeoutSec)*time.Second)
    defer cancel()

    result, err := o.Process(ctx, task, &orchestrator.EvolutionOptions{
        MaxIterations:    maxIter,
        QualityThreshold: threshold,
        Timeout:          time.Duration(timeoutSec) * time.Second,
    })

    if err != nil {
        log.Fatalf("orchestration failed: %v", err)
    }

    fmt.Printf("Converged: %v\n", result.Converged)
    fmt.Printf("Iterations: %d\n", result.Iterations)
    fmt.Printf("Final Score: %.2f\n", result.FinalScore)
    fmt.Printf("Subtasks: %d\n", len(result.Subtasks))
}
```

- [ ] **Step 1: Write main.go**

- [ ] **Step 2: Run go build**

```bash
cd 80-PROJECTS/self-evolving-orchestrator/go
go build ./cmd/orchestrator
```

- [ ] **Step 3: Test with mock execution**

```bash
./orchestrator -task "analyze stock market" -max-iter 2
```

- [ ] **Step 4: Commit**

---

### Task 10: Implement TypeScript MCP Adapter

**Files:**
- Create: `80-PROJECTS/self-evolving-orchestrator/ts/src/adapters/mcp-adapter.ts`

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

interface OrchestratorStatus {
  ready: boolean;
  peers: number;
  activeTasks: number;
}

interface EvolutionResult {
  finalTask: string;
  subtasks: string[];
  iterations: number;
  finalScore: number;
  converged: boolean;
}

export class MCPAdapter {
  private server: Server;
  private orchestratorUrl: string;

  constructor(orchestratorUrl: string = 'http://localhost:8080') {
    this.orchestratorUrl = orchestratorUrl;
    this.server = new Server(
      { name: 'self-evolving-orchestrator', version: '1.0.0' },
      { capabilities: { tools: {} } }
    );
    this.setupTools();
  }

  private setupTools() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'orchestrator_process',
          description: 'Submit a task for self-evolving orchestration',
          inputSchema: {
            type: 'object',
            properties: {
              task: { type: 'string', description: 'The task to orchestrate' },
              maxIterations: { type: 'number', default: 3 },
              threshold: { type: 'number', default: 0.7 },
            },
          },
        },
        {
          name: 'orchestrator_status',
          description: 'Get orchestrator status',
          inputSchema: { type: 'object', properties: {} },
        },
        {
          name: 'orchestrator_peers',
          description: 'List registered peer agents',
          inputSchema: { type: 'object', properties: {} },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      switch (name) {
        case 'orchestrator_process':
          return await this.processTask(args.task, args.maxIterations, args.threshold);
        case 'orchestrator_status':
          return await this.getStatus();
        case 'orchestrator_peers':
          return await this.listPeers();
        default:
          return { error: `Unknown tool: ${name}` };
      }
    });
  }

  private async processTask(task: string, maxIter?: number, threshold?: number): Promise<{ content: Array<{ type: string; text: string }> }> {
    try {
      const response = await fetch(`${this.orchestratorUrl}/api/v1/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, maxIterations: maxIter, threshold }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result: EvolutionResult = await response.json();
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2),
        }],
      };
    } catch (error) {
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
      };
    }
  }

  private async getStatus(): Promise<{ content: Array<{ type: string; text: string }> }> {
    return {
      content: [{ type: 'text', text: JSON.stringify({ ready: true, peers: 0, activeTasks: 0 }) }],
    };
  }

  private async listPeers(): Promise<{ content: Array<{ type: string; text: string }> }> {
    return {
      content: [{ type: 'text', text: '[]' }],
    };
  }

  async start() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('MCP adapter running');
  }
}
```

- [ ] **Step 1: Write mcp-adapter.ts**

- [ ] **Step 2: Verify TypeScript compiles**

```bash
cd 80-PROJECTS/self-evolving-orchestrator/ts
npx tsc --noEmit
```

- [ ] **Step 3: Commit**

---

### Task 11: Integration Test

**Files:**
- Create: `80-PROJECTS/self-evolving-orchestrator/integration/test_workflow.go`

```go
package integration

import (
    "context"
    "testing"
    "time"

    "github.com/openclaw/self-evolving-orchestrator/go/orchestrator"
)

func TestEndToEnd(t *testing.T) {
    // This test requires the full system to be running
    t.Skip("Requires running orchestrator server")

    decomposer := orchestrator.NewDecomposerWrapper(orchestrator.NewLLMBasedDecomposer("http://localhost:11434", "llama3"))

    executor := func(subtask string) orchestrator.ExecutionResult {
        return orchestrator.ExecutionResult{
            Subtask: subtask,
            Output:  "mock execution: " + subtask,
            Success: true,
            Duration: 100 * time.Millisecond,
        }
    }

    o := orchestrator.NewOrchestrator(decomposer, executor)

    result, err := o.Process(context.Background(), "analyze this task", &orchestrator.EvolutionOptions{
        MaxIterations:    3,
        QualityThreshold: 0.5,
        Timeout:          30 * time.Second,
    })

    if err != nil {
        t.Errorf("unexpected error: %v", err)
    }

    if result == nil {
        t.Fatal("expected result")
    }

    t.Logf("Iterations: %d, Converged: %v, Score: %.2f", result.Iterations, result.Converged, result.FinalScore)
}
```

- [ ] **Step 1: Write integration test**

- [ ] **Step 2: Verify it compiles**

- [ ] **Step 3: Commit**

---

## Phase 2: Implementation (Parallel Tasks)

After Phase 1 is complete, the following can be done in parallel:

- [ ] **Task 12: HTTP API Server** - Expose REST endpoints for orchestration
- [ ] **Task 13: A2A Adapter** - TypeScript A2A protocol adapter
- [ ] **Task 14: Ollama Integration** - Connect LLM decomposition to Ollama
- [ ] **Task 15: Agent Islands Integration** - Connect to existing agent-islands

---

## Summary

**Total Tasks:** 15

**Estimated Completion:**
- Phase 1: Tasks 1-11 (project setup + core Go components)
- Phase 2: Tasks 12-15 (API, adapters, integration)

**Key Dependencies:**
- Tasks 2-8 must complete before Task 9 (main)
- Task 11 requires Tasks 1-9 to be complete
