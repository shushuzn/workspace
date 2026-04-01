package orchestrator

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
)

// LLMDecomposer is the interface for task decomposition
type LLMDecomposer interface {
	Decompose(ctx context.Context, task string) ([]string, error)
}

// Decomposer is a type alias for LLMDecomposer for brevity
type Decomposer = LLMDecomposer

// SimpleDecomposer is a basic implementation that splits on newlines
type SimpleDecomposer struct{}

func (d *SimpleDecomposer) Decompose(ctx context.Context, task string) ([]string, error) {
	lines := strings.Split(strings.TrimSpace(task), ".")
	var subtasks []string
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if len(line) > 10 {
			subtasks = append(subtasks, line+".")
		}
	}
	if len(subtasks) == 0 {
		return []string{task}, nil
	}
	return subtasks, nil
}

// LLMBasedDecomposer uses Ollama for decomposition
type LLMBasedDecomposer struct {
	endpoint string
	model    string
}

func NewLLMBasedDecomposer(endpoint, model string) *LLMBasedDecomposer {
	return &LLMBasedDecomposer{
		endpoint: endpoint,
		model:    model,
	}
}

func (d *LLMBasedDecomposer) Decompose(ctx context.Context, task string) ([]string, error) {
	prompt := fmt.Sprintf(`Break down this task into 2-5 subtasks. Return ONLY a JSON array of strings, nothing else.
Task: %s

Response format: ["subtask 1", "subtask 2", ...]`, task)

	reqBody := map[string]interface{}{
		"model":  d.model,
		"prompt": prompt,
		"stream": false,
	}

	reqJSON, err := json.Marshal(reqBody)
	if err != nil {
		return nil, err
	}

	req, err := http.NewRequestWithContext(ctx, "POST", d.endpoint+"/api/generate", bytes.NewReader(reqJSON))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		// Fallback to simple decomposer on error
		decomposer := &SimpleDecomposer{}
		return decomposer.Decompose(ctx, task)
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	response, ok := result["response"].(string)
	if !ok {
		return nil, fmt.Errorf("unexpected response format")
	}

	// Parse JSON array from response
	start := strings.Index(response, "[")
	end := strings.LastIndex(response, "]")

	if start == -1 || end == -1 {
		// Fallback: parse markdown subtask format ("**Subtask N:**" or "- Subtask" or "N.")
		lines := strings.Split(response, "\n")
		subtasks := make([]string, 0)
		for _, line := range lines {
			line = strings.TrimSpace(line)
			// Skip headers, empty lines, and short lines
			if len(line) < 15 || strings.HasPrefix(line, "#") {
				continue
			}
			// Strip markdown bold/italic markers and numbering prefixes
			line = strings.TrimPrefix(line, "**")
			line = strings.TrimSuffix(line, "**")
			line = strings.TrimPrefix(line, "*")
			line = strings.TrimSuffix(line, "*")
			line = strings.TrimPrefix(line, "- ")
			line = strings.TrimPrefix(line, "• ")
			// Strip leading "1.", "2.", etc.
			for i := 1; i <= 9; i++ {
				line = strings.TrimPrefix(line, fmt.Sprintf("%d. ", i))
				line = strings.TrimPrefix(line, fmt.Sprintf("%s. ", string(rune('0'+i))))
			}
			line = strings.TrimSpace(line)
			if len(line) > 10 {
				subtasks = append(subtasks, line)
			}
		}
		if len(subtasks) == 0 {
			return []string{task}, nil
		}
		return subtasks, nil
	}

	jsonStr := response[start : end+1]
	var subtasks []string
	if err := json.Unmarshal([]byte(jsonStr), &subtasks); err != nil {
		return []string{task}, nil
	}

	return subtasks, nil
}

// DecomposerWrapper wraps a decomposer with strategy hints
type DecomposerWrapper struct {
	base Decomposer
}

func NewDecomposerWrapper(base Decomposer) *DecomposerWrapper {
	return &DecomposerWrapper{base: base}
}

func (w *DecomposerWrapper) DecomposeWithStrategy(ctx context.Context, task string, strategy DecomposeStrategy) ([]string, error) {
	modifiedTask := task

	switch strategy.Granularity {
	case GranularityCoarse:
		modifiedTask = fmt.Sprintf("Break this into %d major steps: %s", strategy.MaxSubtasks, task)
	case GranularityMedium:
		modifiedTask = fmt.Sprintf("Break this into %d detailed steps: %s", strategy.MaxSubtasks, task)
	case GranularityFine:
		modifiedTask = fmt.Sprintf("Break this into %d small, atomic steps: %s", strategy.MaxSubtasks, task)
	}

	subtasks, err := w.base.Decompose(ctx, modifiedTask)
	if err != nil {
		return nil, err
	}

	if len(subtasks) > strategy.MaxSubtasks {
		subtasks = subtasks[:strategy.MaxSubtasks]
	}

	return subtasks, nil
}
