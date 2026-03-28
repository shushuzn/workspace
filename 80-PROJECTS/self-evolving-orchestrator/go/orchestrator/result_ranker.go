package orchestrator

import (
	"math"
	"sort"
	"time"
)

// ResultRanker scores and ranks execution results
type ResultRanker struct {
	weights ScoringWeights
}

// NewResultRanker creates a ranker with given weights
func NewResultRanker(weights ScoringWeights) *ResultRanker {
	return &ResultRanker{weights: weights}
}

// NewDefaultResultRanker creates a ranker with default weights
func NewDefaultResultRanker() *ResultRanker {
	return NewResultRanker(DefaultScoringWeights())
}

// Rank scores and sorts results by total score (descending)
func (r *ResultRanker) Rank(results []ExecutionResult) []RankedResult {
	ranked := make([]RankedResult, len(results))
	for i, result := range results {
		breakdown := r.scoreBreakdown(&result)
		total := r.weights.Quality*breakdown.QualityScore +
			r.weights.Latency*breakdown.LatencyScore +
			r.weights.Success*breakdown.SuccessScore +
			r.weights.Relevance*breakdown.QualityScore // relevance uses quality for now
		ranked[i] = RankedResult{
			Result:     &results[i],
			TotalScore: total,
			Breakdown:  breakdown,
		}
	}
	sort.Slice(ranked, func(i, j int) bool {
		return ranked[i].TotalScore > ranked[j].TotalScore
	})
	return ranked
}

// AggregateAndScore computes a single quality score from all subtask results
func (r *ResultRanker) AggregateAndScore(results []ExecutionResult) float64 {
	if len(results) == 0 {
		return 0.0
	}
	ranked := r.Rank(results)
	var totalScore float64
	var weightSum float64
	for i, rr := range ranked {
		weight := 1.0 / math.Max(1.0, float64(i+1))
		totalScore += rr.TotalScore * weight
		weightSum += weight
	}
	return totalScore / weightSum
}

func (r *ResultRanker) scoreBreakdown(result *ExecutionResult) ScoreBreakdown {
	var qualityScore float64
	if result.Success {
		qualityScore = math.Min(1.0, float64(len(result.Output))/1000.0)
		if len(result.Error) > 0 {
			qualityScore *= 0.5
		}
	}

	var latencyScore float64
	if result.Duration > 0 {
		latencyScore = math.Max(0, 1.0-result.Duration.Seconds()/30.0)
	}

	var successScore float64
	if result.Success {
		successScore = 1.0
	}

	return ScoreBreakdown{
		QualityScore:  qualityScore,
		LatencyScore: latencyScore,
		SuccessScore: successScore,
	}
}
