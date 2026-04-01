package orchestrator

import (
	"context"
	"testing"
	"time"
)

func TestDetectOverlap(t *testing.T) {
	evolver := NewSelfEvolver()

	tests := []struct {
		name     string
		results  []ExecutionResult
		wantOver bool
	}{
		{
			name:     "single result never overlaps",
			results:  []ExecutionResult{{Subtask: "a", Output: "hello world", Success: true}},
			wantOver: false,
		},
		{
			name:     "two identical outputs overlap",
			results:  []ExecutionResult{{Subtask: "a", Output: "the same text here", Success: true}, {Subtask: "b", Output: "the same text here", Success: true}},
			wantOver: true,
		},
		{
			name:     "two completely different outputs don't overlap",
			results:  []ExecutionResult{{Subtask: "a", Output: "cats are furry animals that purr", Success: true}, {Subtask: "b", Output: "stocks rise and fall daily on market", Success: true}},
			wantOver: false,
		},
		{
			name:     "two partially similar outputs may not exceed threshold",
			results:  []ExecutionResult{{Subtask: "a", Output: "the weather today is sunny and warm", Success: true}, {Subtask: "b", Output: "the weather tomorrow will be sunny and hot", Success: true}},
			wantOver: false,
		},
		{
			name:     "empty output never overlaps",
			results:  []ExecutionResult{{Subtask: "a", Output: "", Success: true}, {Subtask: "b", Output: "something", Success: true}},
			wantOver: false,
		},
		{
			name:     "three diverse outputs no overlap",
			results:  []ExecutionResult{{Subtask: "a", Output: "dogs run in the park", Success: true}, {Subtask: "b", Output: "fish swim in the ocean", Success: true}, {Subtask: "c", Output: "birds fly across the sky", Success: true}},
			wantOver: false,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got := evolver.detectOverlap(context.Background(), tc.results)
			if got != tc.wantOver {
				t.Errorf("detectOverlap = %v, want %v", got, tc.wantOver)
			}
		})
	}
}

func TestShouldRefine(t *testing.T) {
	evolver := NewSelfEvolver()

	tests := []struct {
		name       string
		record     *EvolutionRecord
		wantRefine bool
	}{
		{
			name: "all failed triggers refine",
			record: &EvolutionRecord{
				Task:     "test",
				Subtasks: []string{"a", "b"},
				Results:  []ExecutionResult{{Subtask: "a", Output: "", Success: false}, {Subtask: "b", Output: "", Success: false}},
				Score:    0.6,
			},
			wantRefine: true,
		},
		{
			name: "score below 0.5 triggers refine",
			record: &EvolutionRecord{
				Task:     "test",
				Subtasks: []string{"a"},
				Results:  []ExecutionResult{{Subtask: "a", Output: "short", Success: true}},
				Score:    0.3,
			},
			wantRefine: true,
		},
		{
			name: "excessive overlap triggers refine",
			record: &EvolutionRecord{
				Task:     "test",
				Subtasks: []string{"a", "b"},
				Results:  []ExecutionResult{{Subtask: "a", Output: "identical content identical content", Success: true}, {Subtask: "b", Output: "identical content identical content", Success: true}},
				Score:    0.6,
			},
			wantRefine: true,
		},
		{
			name: "good score no overlap doesn't refine",
			record: &EvolutionRecord{
				Task:     "test",
				Subtasks: []string{"a", "b"},
				Results:  []ExecutionResult{{Subtask: "a", Output: "cats meow loudly", Success: true}, {Subtask: "b", Output: "dogs bark quietly", Success: true}},
				Score:    0.7,
			},
			wantRefine: false,
		},
		{
			name: "empty results doesn't crash",
			record: &EvolutionRecord{
				Task:     "test",
				Subtasks: []string{},
				Results:  []ExecutionResult{},
				Score:    0.6,
			},
			wantRefine: false,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got, _ := evolver.ShouldRefine(context.Background(), tc.record)
			if got != tc.wantRefine {
				t.Errorf("ShouldRefine = %v, want %v", got, tc.wantRefine)
			}
		})
	}
}

func TestGetNextStrategy(t *testing.T) {
	evolver := NewSelfEvolver()

	// Should cycle through all strategies
	strategies := make([]DecomposeStrategy, 0, 8)
	for i := 0; i < 8; i++ {
		strategies = append(strategies, evolver.GetNextStrategy())
	}

	// First 6 should be the pool in order
	if len(strategies) < 6 {
		t.Fatalf("expected at least 6 strategies, got %d", len(strategies))
	}

	// After pool exhausted, should stay at last strategy
	for i := 6; i < len(strategies); i++ {
		if strategies[i].Name != strategies[5].Name {
			t.Errorf("strategy %d = %v, want last = %v", i, strategies[i].Name, strategies[5].Name)
		}
	}
}

func TestRecordResultAndHistory(t *testing.T) {
	evolver := NewSelfEvolver()

	record := &EvolutionRecord{
		Task:     "test task",
		Subtasks: []string{"a", "b"},
		Results:  []ExecutionResult{{Subtask: "a", Output: "result a", Success: true}},
		Score:    0.5,
	}

	evolver.RecordResult(record)

	history := evolver.GetHistory()
	if len(history) != 1 {
		t.Errorf("len(history) = %d, want 1", len(history))
	}
	if history[0].Task != "test task" {
		t.Errorf("history[0].Task = %s, want 'test task'", history[0].Task)
	}
}

func TestResetHistory(t *testing.T) {
	evolver := NewSelfEvolver()
	evolver.RecordResult(&EvolutionRecord{Task: "a", Score: 0.5})
	evolver.RecordResult(&EvolutionRecord{Task: "b", Score: 0.6})

	evolver.ResetHistory()

	if len(evolver.GetHistory()) != 0 {
		t.Errorf("after ResetHistory, len(history) = %d, want 0", len(evolver.GetHistory()))
	}

	// GetNextStrategy should restart from beginning
	strat := evolver.GetNextStrategy()
	if strat.Name != "coarse-fast" {
		t.Errorf("after reset, first strategy = %s, want 'coarse-fast'", strat.Name)
	}
}

func TestEvolutionRecordWithDuration(t *testing.T) {
	// Ensure ExecutionResult works with Duration field
	result := ExecutionResult{
		Subtask:   "test",
		Output:    "output text here",
		Success:   true,
		Duration:  2500 * time.Millisecond,
		Timestamp: time.Now(),
	}

	if result.Duration.Seconds() != 2.5 {
		t.Errorf("Duration = %v, want 2.5s", result.Duration)
	}
}
