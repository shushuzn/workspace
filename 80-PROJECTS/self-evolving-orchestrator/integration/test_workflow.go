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
			Subtask:  subtask,
			Output:   "mock execution: " + subtask,
			Success:  true,
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
