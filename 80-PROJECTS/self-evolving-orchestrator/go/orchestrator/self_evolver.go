package orchestrator

import (
    "context"
    "fmt"
)

// SelfEvolver analyzes execution results and adjusts decomposition strategy
type SelfEvolver struct {
    history         []EvolutionRecord
    strategyPool    []DecomposeStrategy
    currentStrategy int
}

// NewSelfEvolver creates a SelfEvolver with default strategies
func NewSelfEvolver() *SelfEvolver {
    return &SelfEvolver{
        history:         []EvolutionRecord{},
        strategyPool:    DefaultStrategies(),
        currentStrategy: 0,
    }
}

// ShouldRefine determines if the decomposition should be refined
// Returns (shouldRefine, reason)
func (s *SelfEvolver) ShouldRefine(ctx context.Context, record *EvolutionRecord) (bool, string) {
    // Refine if all subtasks failed
    allFailed := true
    for _, r := range record.Results {
        if r.Success {
            allFailed = false
            break
        }
    }
    if allFailed && len(record.Results) > 0 {
        return true, "all subtasks failed"
    }

    // Refine if score below threshold
    if record.Score < 0.5 {
        return true, fmt.Sprintf("score %f below threshold 0.5", record.Score)
    }

    // Refine if excessive overlap (detected by similar outputs)
    if s.detectOverlap(record.Results) {
        return true, "excessive overlap between subtasks"
    }

    return false, "quality acceptable"
}

// GetNextStrategy returns the next strategy in the pool
func (s *SelfEvolver) GetNextStrategy() DecomposeStrategy {
    if s.currentStrategy >= len(s.strategyPool) {
        s.currentStrategy = len(s.strategyPool) - 1
    }
    strategy := s.strategyPool[s.currentStrategy]
    s.currentStrategy++
    return strategy
}

// RecordResult stores an evolution record for future analysis
func (s *SelfEvolver) RecordResult(record *EvolutionRecord) {
    s.history = append(s.history, *record)
}

// GetHistory returns the evolution history
func (s *SelfEvolver) GetHistory() []EvolutionRecord {
    return s.history
}

// ResetHistory clears the evolution history
func (s *SelfEvolver) ResetHistory() {
    s.history = []EvolutionRecord{}
    s.currentStrategy = 0
}

func (s *SelfEvolver) detectOverlap(results []ExecutionResult) bool {
    if len(results) < 2 {
        return false
    }
    // Simple overlap detection placeholder
    return false
}
