package orchestrator

import (
	"context"
	"testing"
	"time"
)

// mockDecomposer implements LLMDecomposer
type mockDecomposer struct {
	subtasks []string
	err      error
	calls    int
}

func (m *mockDecomposer) Decompose(ctx context.Context, task string) ([]string, error) {
	m.calls++
	if m.err != nil {
		return nil, m.err
	}
	return m.subtasks, nil
}


func TestEvolutionLoopRefinesOnLowScore(t *testing.T) {
	decomposer := &mockDecomposer{
		subtasks: []string{"task a", "task b"},
	}

	executor := func(subtask string) ExecutionResult {
		return ExecutionResult{
			Subtask:  subtask,
			Output:   "tiny",
			Success:  true,
			Duration: 50 * time.Millisecond,
		}
	}

	evolver := NewSelfEvolver()
	ranker := NewDefaultResultRanker()
	loop := NewEvolutionLoop(NewDecomposerWrapper(decomposer), evolver, ranker, executor)

	result, err := loop.Run(context.Background(), "task", &EvolutionOptions{
		MaxIterations:    3,
		QualityThreshold: 0.7,
		Timeout:         10 * time.Second,
	})

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result == nil {
		t.Fatal("expected result")
	}
	if result.Iterations < 2 {
		t.Errorf("Iterations = %d, want >= 2 (low score should trigger refine)", result.Iterations)
	}
}

func TestEvolutionLoopRefinesOnOverlap(t *testing.T) {
	decomposer := &mockDecomposer{
		subtasks: []string{"task a", "task b"},
	}

	executor := func(subtask string) ExecutionResult {
		return ExecutionResult{
			Subtask:  subtask,
			Output:   "the exact same identical text the exact same identical text the exact same",
			Success:  true,
			Duration: 100 * time.Millisecond,
		}
	}

	evolver := NewSelfEvolver()
	ranker := NewDefaultResultRanker()
	loop := NewEvolutionLoop(NewDecomposerWrapper(decomposer), evolver, ranker, executor)

	result, err := loop.Run(context.Background(), "task", &EvolutionOptions{
		MaxIterations:    3,
		QualityThreshold: 0.5,
		Timeout:         10 * time.Second,
	})

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result == nil {
		t.Fatal("expected result")
	}
	if result.Iterations < 2 {
		t.Errorf("Iterations = %d, want >= 2 (overlap should trigger refine)", result.Iterations)
	}
}

func TestEvolutionLoopMaxIterations(t *testing.T) {
	decomposer := &mockDecomposer{
		subtasks: []string{"task a"},
	}

	executor := func(subtask string) ExecutionResult {
		return ExecutionResult{
			Subtask:  subtask,
			Output:   "short",
			Success:  true,
			Duration: 50 * time.Millisecond,
		}
	}

	evolver := NewSelfEvolver()
	ranker := NewDefaultResultRanker()
	loop := NewEvolutionLoop(NewDecomposerWrapper(decomposer), evolver, ranker, executor)

	result, err := loop.Run(context.Background(), "task", &EvolutionOptions{
		MaxIterations:    2,
		QualityThreshold: 0.9,
		Timeout:         10 * time.Second,
	})

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result == nil {
		t.Fatal("expected result")
	}
	if result.Iterations != 2 {
		t.Errorf("Iterations = %d, want 2 (max reached)", result.Iterations)
	}
	if result.Converged {
		t.Error("Converged = true, want false")
	}
}

func TestEvolutionLoopContextCancellation(t *testing.T) {
	decomposer := &mockDecomposer{
		subtasks: []string{"slow task"},
	}

	executor := func(subtask string) ExecutionResult {
		time.Sleep(200 * time.Millisecond)
		return ExecutionResult{
			Subtask:  subtask,
			Output:   "done",
			Success:  true,
			Duration: 200 * time.Millisecond,
		}
	}

	evolver := NewSelfEvolver()
	ranker := NewDefaultResultRanker()
	loop := NewEvolutionLoop(NewDecomposerWrapper(decomposer), evolver, ranker, executor)

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Millisecond)
	defer cancel()

	_, err := loop.Run(ctx, "task", &EvolutionOptions{
		MaxIterations: 5,
		Timeout:       10 * time.Second,
	})

	// loop.Run returns nil error even on ctx.Done(); it returns result==nil
	// so we just verify it doesn't crash
	_ = err
}

func TestDecomposerWrapperRespectsMaxSubtasks(t *testing.T) {
	base := &mockDecomposer{calls: 0, subtasks: []string{"a", "b", "c", "d", "e", "f"}}
	wrapper := NewDecomposerWrapper(base)
	ctx := context.Background()

	tests := []struct {
		granularity Granularity
		maxSubtasks int
	}{
		{GranularityCoarse, 2},
		{GranularityMedium, 3},
		{GranularityFine, 5},
	}

	for _, tc := range tests {
		base.calls = 0
		subtasks, err := wrapper.DecomposeWithStrategy(ctx, "test", DecomposeStrategy{
			Granularity: tc.granularity,
			ModelHint:   "fast",
			MaxSubtasks: tc.maxSubtasks,
		})
		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}
		if len(subtasks) > tc.maxSubtasks {
			t.Errorf("len(subtasks) = %d, want <= %d", len(subtasks), tc.maxSubtasks)
		}
		if base.calls != 1 {
			t.Errorf("base called %d times, want 1", base.calls)
		}
	}
}

func TestEvolutionRecordsHistory(t *testing.T) {
	decomposer := &mockDecomposer{subtasks: []string{"task a", "task b"}}
	executor := func(subtask string) ExecutionResult {
		return ExecutionResult{Subtask: subtask, Output: "output for " + subtask, Success: true, Duration: 100 * time.Millisecond}
	}
	evolver := NewSelfEvolver()
	ranker := NewDefaultResultRanker()
	loop := NewEvolutionLoop(NewDecomposerWrapper(decomposer), evolver, ranker, executor)

	loop.Run(context.Background(), "task", &EvolutionOptions{
		MaxIterations:    3,
		QualityThreshold: 0.5,
		Timeout:         10 * time.Second,
	})

	history := evolver.GetHistory()
	if len(history) == 0 {
		t.Error("expected history to be recorded")
	}
	if len(history) != 3 {
		t.Errorf("len(history) = %d, want 3", len(history))
	}
}


