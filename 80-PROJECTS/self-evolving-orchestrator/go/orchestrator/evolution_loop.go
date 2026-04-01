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
	evolver   *SelfEvolver
	ranker    *ResultRanker
	executor  func(subtask string) ExecutionResult
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
	var lastScore float64
	var subtasks []string
	var ranked []RankedResult
	var err error

	for i := 0; i < opts.MaxIterations; i++ {
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		default:
		}

		// Decompose
		subtasks, err = e.decomposer.DecomposeWithStrategy(ctx, currentTask, strategy)
		if err != nil {
			return nil, fmt.Errorf("decompose failed: %w", err)
		}

		// Execute subtasks in parallel
		results := e.executeSubtasks(subtasks)

		// Score results
		ranked = e.ranker.Rank(ctx, results)
		aggregateScore := e.ranker.AggregateAndScore(ctx, results)
		lastScore = aggregateScore

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

		if !shouldRefine && aggregateScore >= opts.QualityThreshold {
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
			FinalTask:  currentTask,
			Subtasks:    subtasks,
			Results:     ranked,
			Iterations: opts.MaxIterations,
			FinalScore: lastScore,
			Converged:  false,
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
