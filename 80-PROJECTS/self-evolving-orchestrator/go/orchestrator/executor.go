package orchestrator

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)

// Executor handles task execution via LLM agents
type Executor struct {
	router  *ProviderRouter
	client  *http.Client
	baseURL string
}

// NewExecutor creates a new executor with default settings
func NewExecutor(router *ProviderRouter) *Executor {
	return &Executor{
		router: router,
		client: &http.Client{
			Timeout: 60 * time.Second,
		},
		baseURL: getEnv("LLM_API_BASE_URL", "https://api.anthropic.com"),
	}
}

// NewExecutorWithURL creates an executor with custom base URL
func NewExecutorWithURL(router *ProviderRouter, baseURL string) *Executor {
	return &Executor{
		router:  router,
		client:  &http.Client{Timeout: 60 * time.Second},
		baseURL: baseURL,
	}
}

// Execute runs a task via specified agent
func (e *Executor) Execute(ctx context.Context, agent *Agent, task string) (*ExecutionResult, error) {
	start := time.Now()

	prompt := agent.BuildPrompt(task)
	complexity := e.estimateComplexity(task)
	config := e.router.Route(prompt, complexity)

	response, err := e.callAPI(ctx, config, prompt)
	duration := time.Since(start)

	if err != nil {
		return &ExecutionResult{
			Subtask:   agent.Name,
			Output:    "",
			Success:   false,
			Error:     err.Error(),
			Duration:  duration,
			Timestamp: time.Now(),
		}, nil
	}

	return &ExecutionResult{
		Subtask:   agent.Name,
		Output:    response,
		Success:   true,
		Duration:  duration,
		Timestamp: time.Now(),
	}, nil
}

// ExecuteParallel runs multiple tasks concurrently via agents
func (e *Executor) ExecuteParallel(ctx context.Context, agents []*Agent, tasks []string) ([]ExecutionResult, error) {
	if len(agents) == 0 || len(tasks) == 0 {
		return []ExecutionResult{}, nil
	}

	// Match tasks to agents (round-robin if more tasks than agents)
	var wg sync.WaitGroup
	var mu sync.Mutex
	results := make([]ExecutionResult, 0, len(tasks))

	ctx, cancel := context.WithTimeout(ctx, 5*time.Minute)
	defer cancel()

	for i, task := range tasks {
		agent := agents[i%len(agents)]
		wg.Add(1)
		go func(a *Agent, t string) {
			defer wg.Done()
			result, _ := e.Execute(ctx, a, t) // Error already captured in result
			mu.Lock()
			defer mu.Unlock()
			results = append(results, *result)
		}(agent, task)
	}

	wg.Wait()
	return results, nil
}

// AggregateResults combines results based on topology
func (e *Executor) AggregateResults(results []ExecutionResult, topology SwarmTopology) (string, error) {
	switch topology {
	case TopologyHierarchical, TopologyStar:
		return e.aggregateHierarchical(results)
	case TopologyMesh:
		return e.aggregateMesh(results)
	case TopologyRing:
		return e.aggregateRing(results)
	default:
		return e.aggregateMesh(results)
	}
}

func (e *Executor) aggregateHierarchical(results []ExecutionResult) string {
	var sb strings.Builder
	successCount := 0

	for _, r := range results {
		if r.Success {
			successCount++
			sb.WriteString(fmt.Sprintf("[%s] SUCCESS:\n%s\n\n", r.Subtask, r.Output))
		} else {
			sb.WriteString(fmt.Sprintf("[%s] FAILED: %s\n\n", r.Subtask, r.Error))
		}
	}

	sb.WriteString(fmt.Sprintf("=== Aggregated: %d/%d successful ===\n", successCount, len(results)))
	return sb.String()
}

func (e *Executor) aggregateMesh(results []ExecutionResult) string {
	var sb strings.Builder
	sb.WriteString("=== Mesh Results (all agents contributed) ===\n\n")

	for _, r := range results {
		status := "SUCCESS"
		if !r.Success {
			status = "FAILED"
		}
		sb.WriteString(fmt.Sprintf("[%s] %s (%s):\n%s\n\n", r.Subtask, status, r.Duration, r.Output))
	}

	return sb.String()
}

func (e *Executor) aggregateRing(results []ExecutionResult) string {
	var sb strings.Builder
	sb.WriteString("=== Ring Pipeline Results ===\n\n")

	for i, r := range results {
		sb.WriteString(fmt.Sprintf("Step %d [%s]:\n%s\n\n", i+1, r.Subtask, r.Output))
	}

	return sb.String()
}

func (e *Executor) callAPI(ctx context.Context, config ModelConfig, prompt string) (string, error) {
	switch config.Provider {
	case ProviderClaude:
		return e.callClaude(ctx, config, prompt)
	case ProviderOpenAI:
		return e.callOpenAI(ctx, config, prompt)
	case ProviderGemini:
		return e.callGemini(ctx, config, prompt)
	case ProviderOllama:
		return e.callOllama(ctx, config, prompt)
	default:
		return e.callClaude(ctx, config, prompt)
	}
}

func (e *Executor) callClaude(ctx context.Context, config ModelConfig, prompt string) (string, error) {
	apiKey := getEnv("ANTHROPIC_API_KEY", "")
	if apiKey == "" {
		return "[No API key configured - would call Claude]", nil
	}

	reqBody := map[string]interface{}{
		"model": config.Model,
		"max_tokens": config.MaxTokens,
		"messages": []map[string]string{
			{"role": "user", "content": prompt},
		},
	}

	body, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", e.baseURL+"/v1/messages", bytes.NewReader(body))
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-api-key", apiKey)
	req.Header.Set("anthropic-version", "2023-06-01")

	resp, err := e.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var result map[string]interface{}
	if err := json.Unmarshal(respBody, &result); err != nil {
		return "", fmt.Errorf("failed to parse response: %w", err)
	}

	if content, ok := result["content"].([]interface{}); ok {
		if len(content) > 0 {
			if block, ok := content[0].(map[string]interface{}); ok {
				if text, ok := block["text"].(string); ok {
					return text, nil
				}
			}
		}
	}

	return string(respBody), nil
}

func (e *Executor) callOpenAI(ctx context.Context, config ModelConfig, prompt string) (string, error) {
	apiKey := getEnv("OPENAI_API_KEY", "")
	if apiKey == "" {
		return "[No API key configured - would call OpenAI]", nil
	}

	reqBody := map[string]interface{}{
		"model": config.Model,
		"messages": []map[string]string{
			{"role": "user", "content": prompt},
		},
	}

	body, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", "https://api.openai.com/v1/chat/completions", bytes.NewReader(body))
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	resp, err := e.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var result map[string]interface{}
	if err := json.Unmarshal(respBody, &result); err != nil {
		return "", fmt.Errorf("failed to parse response: %w", err)
	}

	if choices, ok := result["choices"].([]interface{}); ok {
		if len(choices) > 0 {
			if choice, ok := choices[0].(map[string]interface{}); ok {
				if msg, ok := choice["message"].(map[string]interface{}); ok {
					if content, ok := msg["content"].(string); ok {
						return content, nil
					}
				}
			}
		}
	}

	return string(respBody), nil
}

func (e *Executor) callGemini(ctx context.Context, config ModelConfig, prompt string) (string, error) {
	apiKey := getEnv("GEMINI_API_KEY", "")
	if apiKey == "" {
		return "[No API key configured - would call Gemini]", nil
	}

	url := fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent?key=%s", config.Model, apiKey)

	reqBody := map[string]interface{}{
		"contents": []map[string]interface{}{
			{"parts": []map[string]string{{"text": prompt}}},
		},
	}

	body, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := e.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(respBody))
	}

	return string(respBody), nil
}

func (e *Executor) callOllama(ctx context.Context, config ModelConfig, prompt string) (string, error) {
	endpoint := config.Endpoint
	if endpoint == "" {
		endpoint = "http://localhost:11434"
	}

	url := endpoint + "/api/generate"

	reqBody := map[string]interface{}{
		"model": config.Model,
		"prompt": prompt,
	}

	body, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := e.client.Do(req)
	if err != nil {
		return "", fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API returned status %d: %s", resp.StatusCode, string(respBody))
	}

	var result map[string]interface{}
	if err := json.Unmarshal(respBody, &result); err != nil {
		return "", fmt.Errorf("failed to parse response: %w", err)
	}

	if response, ok := result["response"].(string); ok {
		return response, nil
	}

	return string(respBody), nil
}

func (e *Executor) estimateComplexity(task string) ComplexityLevel {
	tokens := estimateTokens(task)
	if tokens < 50 {
		return ComplexitySimple
	}
	if tokens < 500 {
		return ComplexityMedium
	}
	return ComplexityComplex
}

// getEnv gets environment variable with default
func getEnv(key, defaultValue string) string {
	if value := strings.TrimSpace(os.Getenv(key)); value != "" {
		return value
	}
	return defaultValue
}
