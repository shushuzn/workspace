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
