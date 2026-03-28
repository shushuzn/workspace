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
	task       string
	maxIter    int
	threshold  float64
	timeoutSec int
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
