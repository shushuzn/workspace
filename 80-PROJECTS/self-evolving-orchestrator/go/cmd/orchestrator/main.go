package main

import (
	"bytes"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"time"

	"github.com/openclaw/self-evolving-orchestrator/orchestrator"
)

var (
	task       string
	maxIter    int
	threshold  float64
	timeoutSec int
	fastMode   bool
)

func main() {
	flag.StringVar(&task, "task", "", "Task to orchestrate")
	flag.IntVar(&maxIter, "max-iter", 3, "Max evolution iterations")
	flag.Float64Var(&threshold, "threshold", 0.7, "Quality threshold")
	flag.IntVar(&timeoutSec, "timeout", 60, "Timeout in seconds")
	flag.BoolVar(&fastMode, "fast", false, "Fast mode: single iteration, skip embeddings")
	flag.Parse()

	if task == "" {
		log.Fatal("task is required")
	}

	// Create decomposer
	decomposer := orchestrator.NewDecomposerWrapper(orchestrator.NewLLMBasedDecomposer("http://localhost:11434", "llama3.2:1b"))

	// Create embedder (skip in fast mode)
	if !fastMode {
		embedder := orchestrator.NewOllamaEmbedder("http://localhost:11434", "llama3.2:1b")
		orchestrator.SetEmbedder(embedder)
	}

	// Create executor: llama3.2:1b for fast mode, qwen3.5:0.8b for quality
	model := "llama3.2:1b"
	if !fastMode {
		model = "qwen3.5:0.8b"
	}
	endpoint := "http://localhost:11434"
	executor := func(subtask string) orchestrator.ExecutionResult {
		start := time.Now()

		prompt := fmt.Sprintf("You are a coding assistant. Complete the following task concisely. Only output code, no explanation.\n\nTask: %s", subtask)
		reqBody := map[string]interface{}{
			"model":  model,
			"prompt": prompt,
			"stream": false,
		}
		reqJSON, _ := json.Marshal(reqBody)
		req, err := http.NewRequestWithContext(context.Background(), "POST", endpoint+"/api/generate", bytes.NewReader(reqJSON))
		if err != nil {
			return orchestrator.ExecutionResult{Subtask: subtask, Success: false, Error: err.Error(), Duration: time.Since(start), Timestamp: time.Now()}
		}
		req.Header.Set("Content-Type", "application/json")
		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			return orchestrator.ExecutionResult{Subtask: subtask, Success: false, Error: err.Error(), Duration: time.Since(start), Timestamp: time.Now()}
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusOK {
			body, _ := io.ReadAll(resp.Body)
			return orchestrator.ExecutionResult{Subtask: subtask, Success: false, Error: fmt.Sprintf("status %d: %s", resp.StatusCode, string(body)), Duration: time.Since(start), Timestamp: time.Now()}
		}
		var result map[string]interface{}
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			return orchestrator.ExecutionResult{Subtask: subtask, Success: false, Error: "decode error", Duration: time.Since(start), Timestamp: time.Now()}
		}
		response, ok := result["response"].(string)
		if !ok {
			return orchestrator.ExecutionResult{Subtask: subtask, Success: false, Error: "no response", Duration: time.Since(start), Timestamp: time.Now()}
		}
		return orchestrator.ExecutionResult{Subtask: subtask, Output: response, Success: true, Duration: time.Since(start), Timestamp: time.Now()}
	}

	// Create orchestrator with LLM-based quality scoring
	o := orchestrator.NewOrchestratorWithLLM(decomposer, executor, endpoint, model)
	o.SetFastMode(fastMode)

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
	fmt.Printf("Subtasks (%d):\n", len(result.Subtasks))
	for i, st := range result.Subtasks {
		fmt.Printf("  %d. %s\n", i+1, st)
	}
	fmt.Printf("Results (%d):\n", len(result.Results))
	for i, r := range result.Results {
		fmt.Printf("  %d. [%.2f] %s -> %s\n", i+1, r.TotalScore, r.Result.Subtask, r.Result.Output)
	}
}
