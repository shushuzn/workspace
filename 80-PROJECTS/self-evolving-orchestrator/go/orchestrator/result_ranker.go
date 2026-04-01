package orchestrator

import (
	"context"
	"math"
	"sort"
	"strings"
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
// Requires context for semantic relevance scoring via embeddings
func (r *ResultRanker) Rank(ctx context.Context, results []ExecutionResult) []RankedResult {
	ranked := make([]RankedResult, len(results))
	for i, result := range results {
		breakdown := r.scoreBreakdown(ctx, &result)
		total := r.weights.Quality*breakdown.QualityScore +
			r.weights.Latency*breakdown.LatencyScore +
			r.weights.Success*breakdown.SuccessScore +
			r.weights.Relevance*breakdown.RelevanceScore
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
// Requires context for semantic relevance scoring
func (r *ResultRanker) AggregateAndScore(ctx context.Context, results []ExecutionResult) float64 {
	if len(results) == 0 {
		return 0.0
	}
	ranked := r.Rank(ctx, results)
	var totalScore float64
	var weightSum float64
	for i, rr := range ranked {
		weight := 1.0 / math.Max(1.0, float64(i+1))
		totalScore += rr.TotalScore * weight
		weightSum += weight
	}
	return totalScore / weightSum
}

func (r *ResultRanker) scoreBreakdown(ctx context.Context, result *ExecutionResult) ScoreBreakdown {
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
		QualityScore:    qualityScore,
		LatencyScore:   latencyScore,
		SuccessScore:   successScore,
		RelevanceScore: r.relevanceScore(ctx, result),
	}
}

// relevanceScore computes semantic relevance using embeddings when available,
// falls back to keyword overlap
func (r *ResultRanker) relevanceScore(ctx context.Context, result *ExecutionResult) float64 {
	if result.Subtask == "" || result.Output == "" {
		return 0
	}

	// Fast path: if no embedder, use keyword overlap
	if sharedEmbedder == nil || ctx == nil {
		return keywordRelevance(result.Subtask, result.Output)
	}

	// Semantic path: embed both and compute cosine similarity
	subtaskVec, err := sharedEmbedder.Embed(ctx, result.Subtask)
	if err != nil || len(subtaskVec) == 0 {
		return keywordRelevance(result.Subtask, result.Output)
	}

	outputVec, err := sharedEmbedder.Embed(ctx, result.Output)
	if err != nil || len(outputVec) == 0 {
		return keywordRelevance(result.Subtask, result.Output)
	}

	return math.Min(1.0, CosineSimilarity(subtaskVec, outputVec))
}

// keywordRelevance computes keyword overlap between subtask and output (legacy)
func keywordRelevance(subtask, output string) float64 {
	if subtask == "" || output == "" {
		return 0
	}
	subtaskLower := strings.ToLower(subtask)
	outputLower := strings.ToLower(output)
	subWords := strings.Fields(subtaskLower)
	var overlap int
	for _, word := range subWords {
		if len(word) > 3 && strings.Contains(outputLower, word) {
			overlap++
		}
	}
	return math.Min(1.0, float64(overlap)/math.Max(1.0, float64(len(subWords))))
}
