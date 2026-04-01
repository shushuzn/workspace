package orchestrator

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"net/http"
	"sort"
	"strings"
	"sync"
	"time"
)

// ResultRanker scores and ranks execution results
type ResultRanker struct {
	weights    ScoringWeights
	llmScorer  *LLMQualityScorer
	skipLLM    bool
	scoreCache map[string]float64
	cacheMu   sync.Mutex
}

// NewResultRanker creates a ranker with given weights
func NewResultRanker(weights ScoringWeights) *ResultRanker {
	return &ResultRanker{weights: weights, scoreCache: make(map[string]float64)}
}

// NewResultRankerWithLLM creates a ranker with LLM quality scoring
func NewResultRankerWithLLM(weights ScoringWeights, endpoint, model string) *ResultRanker {
	return &ResultRanker{
		weights:    weights,
		llmScorer:  NewLLMQualityScorer(endpoint, model),
		skipLLM:    false,
		scoreCache: make(map[string]float64),
	}
}

// SetSkipLLM disables LLM scoring (for fast mode)
func (r *ResultRanker) SetSkipLLM(v bool) { r.skipLLM = v }

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

// AggregateAndScore computes a single quality score from all subtask results.
// Reuses Rank() so each result is scored exactly once.
func (r *ResultRanker) AggregateAndScore(ctx context.Context, results []ExecutionResult) float64 {
	ranked := r.Rank(ctx, results)
	return r.AggregateAndScoreFromRanked(ctx, ranked)
}

// AggregateAndScoreFromRanked computes a single quality score from already-ranked results.
// Accepts the output of Rank() to avoid double-scoring.
func (r *ResultRanker) AggregateAndScoreFromRanked(ctx context.Context, ranked []RankedResult) float64 {
	if len(ranked) == 0 {
		return 0.0
	}
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
	qualityScore := r.qualityScore(ctx, result)

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

// qualityScore returns LLM-based score if available, else length-based fallback.
// Results are cached by (subtask_hash, output_hash) to avoid redundant LLM calls.
func (r *ResultRanker) qualityScore(ctx context.Context, result *ExecutionResult) float64 {
	if !result.Success || result.Output == "" {
		return 0
	}

	// Check cache first
	cacheKey := r.qualityCacheKey(result)
	r.cacheMu.Lock()
	if score, ok := r.scoreCache[cacheKey]; ok {
		r.cacheMu.Unlock()
		return score
	}
	r.cacheMu.Unlock()

	var score float64

	// Fast mode: skip LLM, use heuristic only
	if r.skipLLM || r.llmScorer == nil || ctx == nil {
		score = r.heuristicScore(result)
	} else {
		// Use LLM scorer
		s, err := r.llmScorer.ScoreQuality(ctx, result.Subtask, result.Output)
		if err == nil {
			score = s
		} else {
			score = r.heuristicScore(result)
		}
	}

	// Cache result
	r.cacheMu.Lock()
	r.scoreCache[cacheKey] = score
	r.cacheMu.Unlock()

	return score
}

func (r *ResultRanker) heuristicScore(result *ExecutionResult) float64 {
	score := math.Min(1.0, float64(len(result.Output))/1000.0)
	if len(result.Error) > 0 {
		score *= 0.5
	}
	return score
}

func (r *ResultRanker) qualityCacheKey(result *ExecutionResult) string {
	h := sha256.New()
	h.Write([]byte(result.Subtask))
	h.Write([]byte(result.Output))
	return fmt.Sprintf("%x", h.Sum(nil))
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

// LLMQualityScorer evaluates output quality using Ollama chat API
type LLMQualityScorer struct {
	endpoint string
	model   string
	timeout time.Duration
}

// NewLLMQualityScorer creates an LLM-based quality scorer
func NewLLMQualityScorer(endpoint, model string) *LLMQualityScorer {
	if endpoint == "" {
		endpoint = "http://localhost:11434"
	}
	if model == "" {
		model = "llama3.2:1b"
	}
	return &LLMQualityScorer{
		endpoint: endpoint,
		model:    model,
		timeout:  15 * time.Second,
	}
}

// ScoreQuality calls the LLM to judge output quality on [0, 1]
// Returns a float or an error. Falls back to length-based heuristic on error.
func (s *LLMQualityScorer) ScoreQuality(ctx context.Context, subtask, output string) (float64, error) {
	if output == "" {
		return 0, nil
	}

	prompt := fmt.Sprintf(`You are a code quality judge. Rate this code on [0.0, 1.0].

Task: %s

Output: %s

Respond with ONLY a single number between 0.0 and 1.0 (e.g. 0.73). No explanation.`, subtask, output)

	reqBody := map[string]interface{}{
		"model":    s.model,
		"prompt":   prompt,
		"stream":   false,
		"max_tokens": 16,
		"temperature": 0.1,
	}

	body, err := json.Marshal(reqBody)
	if err != nil {
		return 0, err
	}

	req, err := http.NewRequestWithContext(ctx, "POST", s.endpoint+"/api/generate", bytes.NewReader(body))
	if err != nil {
		return 0, err
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: s.timeout}
	resp, err := client.Do(req)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return 0, fmt.Errorf("llm quality score: status %d: %s", resp.StatusCode, string(respBody))
	}

	var result struct {
		Response string `json:"response"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return 0, err
	}

	// Parse the first number found in the response
	text := strings.TrimSpace(result.Response)
	for i := 0; i < len(text); i++ {
		if text[i] >= '0' && text[i] <= '9' || text[i] == '.' {
			end := i + 1
			for end < len(text) && (text[end] >= '0' && text[end] <= '9' || text[end] == '.') {
				end++
			}
			val := text[i:end]
			if f, err := parseFloat(val); err == nil {
				return math.Min(1.0, math.Max(0.0, f)), nil
			}
		}
	}
	return 0, fmt.Errorf("llm quality score: no parseable number in: %s", text)
}

func parseFloat(s string) (float64, error) {
	var f float64
	n := len(s)
	for i := 0; i < n; i++ {
		if s[i] >= '0' && s[i] <= '9' {
			f = f*10 + float64(s[i]-'0')
		} else if s[i] == '.' {
			div := 1.0
			for i+1 < n && s[i+1] >= '0' && s[i+1] <= '9' {
				i++
				div *= 10
				f = f*10 + float64(s[i]-'0')
			}
			return f / div, nil
		}
	}
	return f, nil
}
