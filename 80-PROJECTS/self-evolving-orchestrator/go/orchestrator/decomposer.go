package orchestrator

import (
	"context"
	"fmt"
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
	// Fallback to simple decomposer for now
	decomposer := &SimpleDecomposer{}
	return decomposer.Decompose(ctx, task)
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
