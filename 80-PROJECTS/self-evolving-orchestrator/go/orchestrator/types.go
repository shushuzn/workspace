package orchestrator

import "time"

// Granularity represents decomposition granularity
type Granularity int

const (
	GranularityCoarse Granularity = iota
	GranularityMedium
	GranularityFine
)

func (g Granularity) String() string {
	switch g {
	case GranularityCoarse:
		return "coarse"
	case GranularityMedium:
		return "medium"
	case GranularityFine:
		return "fine"
	default:
		return "unknown"
	}
}

// DecomposeStrategy defines how to decompose a task
type DecomposeStrategy struct {
	Name        string
	Granularity Granularity
	ModelHint   string // "fast" or "strong"
	MaxSubtasks int
}

// DefaultStrategies returns the default strategy pool
func DefaultStrategies() []DecomposeStrategy {
	return []DecomposeStrategy{
		{Name: "coarse-fast", Granularity: GranularityCoarse, ModelHint: "fast", MaxSubtasks: 3},
		{Name: "coarse-strong", Granularity: GranularityCoarse, ModelHint: "strong", MaxSubtasks: 3},
		{Name: "medium-fast", Granularity: GranularityMedium, ModelHint: "fast", MaxSubtasks: 5},
		{Name: "medium-strong", Granularity: GranularityMedium, ModelHint: "strong", MaxSubtasks: 5},
		{Name: "fine-fast", Granularity: GranularityFine, ModelHint: "fast", MaxSubtasks: 10},
		{Name: "fine-strong", Granularity: GranularityFine, ModelHint: "strong", MaxSubtasks: 10},
	}
}

// EvolutionOptions configures the evolution behavior
type EvolutionOptions struct {
	MaxIterations    int
	QualityThreshold float64
	Timeout          time.Duration
}

// ExecutionResult represents the result of executing a subtask
type ExecutionResult struct {
	Subtask   string
	Output    string
	Success   bool
	Error     string
	Duration  time.Duration
	Timestamp time.Time
}

// EvolutionRecord records one evolution iteration
type EvolutionRecord struct {
	Task     string
	Subtasks []string
	Results  []ExecutionResult
	Score    float64
	Strategy DecomposeStrategy
}

// EvolutionResultFinal is the final output of the evolution loop
type EvolutionResultFinal struct {
	FinalTask   string
	Subtasks    []string
	Results     []RankedResult
	Iterations  int
	FinalScore  float64
	Converged   bool
}

// ScoringWeights defines the weight for each scoring dimension
type ScoringWeights struct {
	Quality    float64
	Latency    float64
	Success    float64
	Relevance  float64 // relevance to original task
}

// DefaultScoringWeights returns equal weights
func DefaultScoringWeights() ScoringWeights {
	return ScoringWeights{
		Quality:   0.35,
		Latency:   0.15,
		Success:   0.35,
		Relevance: 0.15,
	}
}

// RankedResult pairs an execution result with its score
type RankedResult struct {
	Result     *ExecutionResult
	TotalScore float64
	Breakdown  ScoreBreakdown
}

// ScoreBreakdown shows individual dimension scores
type ScoreBreakdown struct {
	QualityScore  float64
	LatencyScore  float64
	SuccessScore  float64
}
