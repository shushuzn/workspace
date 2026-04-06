package orchestrator

import (
	"context"
)

// Orchestrator is the main entry point for task orchestration
type Orchestrator struct {
	loop     *EvolutionLoop
	registry *PeerRegistry
}

// NewOrchestrator creates a new orchestrator with default (length-based) ranker
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

// NewOrchestratorWithLLM creates an orchestrator with LLM-based quality scoring
func NewOrchestratorWithLLM(
	decomposer *DecomposerWrapper,
	executor func(subtask string) ExecutionResult,
	ollamaEndpoint string,
	llmModel string,
) *Orchestrator {
	evolver := NewSelfEvolver()
	ranker := NewResultRankerWithLLM(DefaultScoringWeights(), ollamaEndpoint, llmModel)
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

// SetFastMode disables LLM scoring for speed
func (o *Orchestrator) SetFastMode(v bool) {
	o.loop.ranker.SetSkipLLM(v)
}

// ExportD3 returns strategy pool and evolution history formatted for D3 Gantt visualization.
// Produces {strategies:[{id,name,granularity,score,rounds}],timeline:[{strategy,iteration,score,converged}]}
func (o *Orchestrator) ExportD3() map[string]interface{} {
	history := o.loop.evolver.GetHistory()
	strategies := o.loop.evolver.GetStrategyPool()

	// Strategy summary: avg score per strategy name across history
	scoreMap := make(map[string][]float64)
	for _, rec := range history {
		name := rec.Strategy.Name
		scoreMap[name] = append(scoreMap[name], rec.Score)
	}
	var strategySummaries []map[string]interface{}
	round := 0
	var timeline []map[string]interface{}
	for _, s := range strategies {
		scores := scoreMap[s.Name]
		var avg float64
		if len(scores) > 0 {
			for _, sc := range scores {
				avg += sc
			}
			avg /= float64(len(scores))
		}
		rounds := len(scores)
		if rounds > round {
			round = rounds
		}
		strategySummaries = append(strategySummaries, map[string]interface{}{
			"id":          s.Name,
			"name":        s.Name,
			"granularity": s.Granularity.String(),
			"modelHint":   s.ModelHint,
			"score":       avg,
			"rounds":      rounds,
		})
		for i, sc := range scores {
			timeline = append(timeline, map[string]interface{}{
				"strategy":  s.Name,
				"iteration":  i + 1,
				"score":     sc,
				"converged": i == rounds-1 && avg >= 0.7,
			})
		}
	}

	return map[string]interface{}{
		"strategies": strategySummaries,
		"timeline":   timeline,
		"maxRounds":  round,
	}
}

// GetStrategyPool returns the strategy pool from the evolver
func (o *Orchestrator) GetStrategyPool() []DecomposeStrategy {
	return o.loop.evolver.GetStrategyPool()
}
