package orchestrator

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// LLMDecomposer decomposes tasks into subtasks using LLM
type LLMDecomposer interface {
	Decompose(ctx context.Context, task string) ([]string, error)
}

// OllamaDecomposer implements LLMDecomposer using ollama API
type OllamaDecomposer struct {
	host   string
	client *http.Client
}

// NewOllamaDecomposer creates a new OllamaDecomposer
func NewOllamaDecomposer(host string) *OllamaDecomposer {
	if host == "" {
		host = "http://localhost:11434"
	}
	return &OllamaDecomposer{
		host: host,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// Decompose calls ollama to decompose a task into subtasks
func (d *OllamaDecomposer) Decompose(ctx context.Context, task string) ([]string, error) {
	prompt := fmt.Sprintf(`分解以下任务为子任务列表。返回JSON数组格式的子任务描述。
只返回JSON数组，不要其他内容。

任务: %s

返回格式示例: ["子任务1描述", "子任务2描述", "子任务3描述"]`, task)

	reqBody := map[string]interface{}{
		"model":  "llama3.2",
		"prompt": prompt,
		"stream": false,
	}

	reqBytes, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", d.host+"/api/generate", bytes.NewReader(reqBytes))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := d.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("LLM service unavailable: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("LLM service returned status %d", resp.StatusCode)
	}

	var result struct {
		Response string `json:"response"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}

	// Parse JSON array from response
	var subtasks []string
	if err := json.Unmarshal([]byte(result.Response), &subtasks); err != nil {
		return nil, fmt.Errorf("task could not be decomposed: %w", err)
	}

	if len(subtasks) == 0 {
		return nil, fmt.Errorf("task could not be decomposed: empty result")
	}

	if len(subtasks) > 100 {
		subtasks = subtasks[:100]
	}

	return subtasks, nil
}
