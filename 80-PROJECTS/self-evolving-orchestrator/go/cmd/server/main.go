package main

import (
	"bytes"
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
	port       int
	timeoutSec int
	fastMode   bool
)

func main() {
	flag.IntVar(&port, "port", 8080, "HTTP server port")
	flag.IntVar(&timeoutSec, "timeout", 60, "Default timeout in seconds")
	flag.BoolVar(&fastMode, "fast", false, "Fast mode: skip LLM scoring")
	flag.Parse()

	decomposer := orchestrator.NewDecomposerWrapper(orchestrator.NewLLMBasedDecomposer("http://localhost:11434", "llama3.2:1b"))

	if !fastMode {
		embedder := orchestrator.NewOllamaEmbedder("http://localhost:11434", "llama3.2:1b")
		orchestrator.SetEmbedder(embedder)
	}

	model := "llama3.2:1b"
	if !fastMode {
		model = "qwen3.5:0.8b"
	}
	endpoint := "http://localhost:11434"
	executor := makeExecutor(endpoint, model)

	o := orchestrator.NewOrchestratorWithLLM(decomposer, executor, endpoint, model)
	o.SetFastMode(fastMode)

	srv := orchestrator.NewHTTPServer(o)

	addr := fmt.Sprintf(":%d", port)
	log.Printf("Starting server on %s", addr)
	log.Printf("  POST /run            — Run task (JSON: {task, maxIterations, threshold, timeoutSec})")
	log.Printf("  GET  /health         — Health check")
	log.Printf("  POST /api/v1/orchestrate — Orchestrate task")
	log.Printf("  GET  /api/v1/peers  — List peers")

	if err := srv.Serve(addr); err != nil {
		log.Fatalf("server failed: %v", err)
	}
}

func makeExecutor(endpoint, model string) func(subtask string) orchestrator.ExecutionResult {
	return func(subtask string) orchestrator.ExecutionResult {
		start := time.Now()
		reqBody := map[string]interface{}{
			"model":  model,
			"prompt": "You are a coding assistant. Complete the following task concisely. Only output code, no explanation.\n\nTask: " + subtask,
			"stream": false,
		}
		reqJSON, _ := json.Marshal(reqBody)
		req, err := http.NewRequest("POST", endpoint+"/api/generate", bytes.NewReader(reqJSON))
		if err != nil {
			return errResult(subtask, err.Error(), start)
		}
		req.Header.Set("Content-Type", "application/json")
		resp, err := http.DefaultClient.Do(req)
		if err != nil {
			return errResult(subtask, err.Error(), start)
		}
		defer resp.Body.Close()
		if resp.StatusCode != http.StatusOK {
			body, _ := io.ReadAll(resp.Body)
			return errResult(subtask, fmt.Sprintf("status %d: %s", resp.StatusCode, string(body)), start)
		}
		var result map[string]interface{}
		if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
			return errResult(subtask, "decode error: "+err.Error(), start)
		}
		response, ok := result["response"].(string)
		if !ok {
			return errResult(subtask, "no response field", start)
		}
		return orchestrator.ExecutionResult{
			Subtask:   subtask,
			Output:    response,
			Success:   true,
			Duration:  time.Since(start),
			Timestamp: time.Now(),
		}
	}
}

func errResult(subtask, errMsg string, start time.Time) orchestrator.ExecutionResult {
	return orchestrator.ExecutionResult{
		Subtask:   subtask,
		Success:   false,
		Error:     errMsg,
		Duration:  time.Since(start),
		Timestamp: time.Now(),
	}
}
