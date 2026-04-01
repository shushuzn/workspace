package orchestrator

import (
	"context"
	"math"
	"strings"
	"testing"
	"time"
)

func TestResultRankerRelevanceScore(t *testing.T) {
	ranker := NewDefaultResultRanker()

	tests := []struct {
		name     string
		subtask  string
		output   string
		minScore float64
		maxScore float64
	}{
		{
			name:     "empty strings return zero",
			subtask:  "",
			output:   "",
			minScore: 0,
			maxScore: 0,
		},
		{
			name:     "empty output returns zero",
			subtask:  "write a function that parses JSON",
			output:   "",
			minScore: 0,
			maxScore: 0,
		},
		{
			name:     "empty subtask returns zero",
			subtask:  "",
			output:   "the output contains something",
			minScore: 0,
			maxScore: 0,
		},
		{
			name:     "perfect overlap",
			subtask:  "parse JSON data",
			output:   "the JSON parser handles data correctly",
			minScore: 0.4,
			maxScore: 1.0,
		},
		{
			name:     "no overlap",
			subtask:  "foo bar baz",
			output:   "completely unrelated text here",
			minScore: 0,
			maxScore: 0.1,
		},
		{
			name:     "short words under 3 chars ignored",
			subtask:  "a bc def g",
			output:   "a bc def g something",
			minScore: 0,
			maxScore: 0.1,
		},
		{
			name:     "partial overlap",
			subtask:  "analyze the stock market trends",
			output:   "the analysis shows market trends are up",
			minScore: 0.2,
			maxScore: 0.7,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			result := &ExecutionResult{
				Subtask:  tc.subtask,
				Output:   tc.output,
				Success:  true,
				Duration: 100 * time.Millisecond,
			}
			breakdown := ranker.scoreBreakdown(context.Background(), result)
			if breakdown.RelevanceScore < tc.minScore || breakdown.RelevanceScore > tc.maxScore {
				t.Errorf("RelevanceScore = %f, want between %f and %f",
					breakdown.RelevanceScore, tc.minScore, tc.maxScore)
			}
		})
	}
}

func TestResultRankerScoreBreakdown(t *testing.T) {
	ranker := NewDefaultResultRanker()

	t.Run("successful short output", func(t *testing.T) {
		result := &ExecutionResult{
			Subtask:  "test subtask",
			Output:   "short",
			Success:  true,
			Duration: 100 * time.Millisecond,
		}
		breakdown := ranker.scoreBreakdown(context.Background(), result)
		if breakdown.QualityScore == 0 {
			t.Error("QualityScore should be > 0 for non-empty successful output")
		}
		if breakdown.SuccessScore != 1.0 {
			t.Errorf("SuccessScore = %f, want 1.0", breakdown.SuccessScore)
		}
		if breakdown.LatencyScore == 0 {
			t.Error("LatencyScore should be > 0 for short duration")
		}
	})

	t.Run("failed result has halved quality", func(t *testing.T) {
		result := &ExecutionResult{
			Subtask:  "test subtask",
			Output:   strings.Repeat("x", 500), // enough chars to exceed min threshold
			Success:  true,
			Error:    "some error",
			Duration: 100 * time.Millisecond,
		}
		breakdown := ranker.scoreBreakdown(context.Background(), result)
		// With a non-trivial output (500 chars), halved score should be < non-halved
		wantHalved := math.Min(1.0, float64(len(result.Output))/1000.0) * 0.5
		if breakdown.QualityScore > wantHalved+0.001 {
			t.Errorf("QualityScore = %f, want <= %f (halved)", breakdown.QualityScore, wantHalved)
		}
	})

	t.Run("failed result zero success score", func(t *testing.T) {
		result := &ExecutionResult{
			Subtask:  "test subtask",
			Output:   "",
			Success:  false,
			Duration: 100 * time.Millisecond,
		}
		breakdown := ranker.scoreBreakdown(context.Background(), result)
		if breakdown.SuccessScore != 0.0 {
			t.Errorf("SuccessScore = %f, want 0.0 for failed result", breakdown.SuccessScore)
		}
		if breakdown.QualityScore != 0.0 {
			t.Errorf("QualityScore = %f, want 0.0 for failed result", breakdown.QualityScore)
		}
	})
}

func TestResultRankerRank(t *testing.T) {
	ranker := NewDefaultResultRanker()

	results := []ExecutionResult{
		{Subtask: "task a", Output: "short", Success: true, Duration: 100 * time.Millisecond},
		{Subtask: "task b", Output: "much longer output here that is more detailed", Success: true, Duration: 200 * time.Millisecond},
		{Subtask: "task c", Output: "", Success: false, Duration: 50 * time.Millisecond},
	}

	ranked := ranker.Rank(context.Background(), results)

	if len(ranked) != 3 {
		t.Fatalf("len(ranked) = %d, want 3", len(ranked))
	}

	// Should be sorted descending by total score
	for i := 1; i < len(ranked); i++ {
		if ranked[i-1].TotalScore < ranked[i].TotalScore {
			t.Errorf("ranked[%d].TotalScore (%f) < ranked[%d].TotalScore (%f), want descending",
				i-1, ranked[i-1].TotalScore, i, ranked[i].TotalScore)
		}
	}

	// Failed task should rank last
	if ranked[len(ranked)-1].Result.Success {
		t.Error("Last ranked result should have Success=false")
	}
}

func TestResultRankerAggregateAndScore(t *testing.T) {
	ranker := NewDefaultResultRanker()

	t.Run("empty results returns 0", func(t *testing.T) {
		score := ranker.AggregateAndScore(context.Background(), []ExecutionResult{})
		if score != 0.0 {
			t.Errorf("AggregateAndScore([]) = %f, want 0.0", score)
		}
	})

	t.Run("single result", func(t *testing.T) {
		results := []ExecutionResult{
			{Subtask: "task", Output: "some output here", Success: true, Duration: 100 * time.Millisecond},
		}
		score := ranker.AggregateAndScore(context.Background(), results)
		if score <= 0 {
			t.Errorf("AggregateAndScore([single]) = %f, want > 0", score)
		}
	})

	t.Run("multiple results weighted by rank", func(t *testing.T) {
		results := []ExecutionResult{
			{Subtask: "task a", Output: "short", Success: true, Duration: 100 * time.Millisecond},
			{Subtask: "task b", Output: "much longer output that should rank higher", Success: true, Duration: 200 * time.Millisecond},
		}
		score := ranker.AggregateAndScore(context.Background(), results)
		// Should be between 0 and 1
		if score < 0 || score > 1 {
			t.Errorf("AggregateAndScore = %f, want between 0 and 1", score)
		}
	})
}

func TestCosineSim(t *testing.T) {
	tests := []struct {
		name     string
		a        []float64
		b        []float64
		minVal   float64
		maxVal   float64
	}{
		{
			name:   "zero vectors returns 0",
			a:      []float64{0, 0, 0},
			b:      []float64{0, 0, 0},
			minVal: 0,
			maxVal: 0,
		},
		{
			name:   "empty vectors returns 0",
			a:      []float64{},
			b:      []float64{},
			minVal: 0,
			maxVal: 0,
		},
		{
			name:   "mismatched length returns 0",
			a:      []float64{1, 2, 3},
			b:      []float64{1, 2},
			minVal: 0,
			maxVal: 0,
		},
		{
			name:   "identical normalized vectors returns 1",
			a:      []float64{0.707, 0.707},
			b:      []float64{0.707, 0.707},
			minVal: 0.99,
			maxVal: 1.01,
		},
		{
			name:   "orthogonal vectors returns 0",
			a:      []float64{1, 0},
			b:      []float64{0, 1},
			minVal: -0.01,
			maxVal: 0.01,
		},
		{
			name:   "opposite vectors returns -1",
			a:      []float64{1, 0},
			b:      []float64{-1, 0},
			minVal: -1.01,
			maxVal: -0.99,
		},
		{
			name:   "identical vectors return 1",
			a:      []float64{1, 0},
			b:      []float64{1, 0},
			minVal: 0.99,
			maxVal: 1.01,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			val := cosineSim(tc.a, tc.b)
			if val < tc.minVal || val > tc.maxVal {
				t.Errorf("cosineSim = %f, want between %f and %f", val, tc.minVal, tc.maxVal)
			}
		})
	}
}

func TestNgramFingerprint(t *testing.T) {
	t.Run("empty text returns zero vector", func(t *testing.T) {
		fp := ngramFingerprint("", 3)
		if len(fp) != 100 {
			t.Fatalf("len(fp) = %d, want 100", len(fp))
		}
		for _, v := range fp {
			if v != 0 {
				t.Errorf("empty text fingerprint should be all zeros, got %f", v)
				break
			}
		}
	})

	t.Run("short text returns zero vector", func(t *testing.T) {
		fp := ngramFingerprint("ab", 3)
		for _, v := range fp {
			if v != 0 {
				t.Errorf("short text fingerprint should be all zeros, got %f", v)
				break
			}
		}
	})

	t.Run("normal text returns L2 normalized vector", func(t *testing.T) {
		fp := ngramFingerprint("hello world test string", 3)
		var norm float64
		for _, v := range fp {
			norm += v * v
		}
		norm = math.Sqrt(norm)
		// Should be normalized to length ~1
		if norm < 0.99 || norm > 1.01 {
			t.Errorf("L2 norm = %f, want ~1.0", norm)
		}
		// All values should be non-negative
		for _, v := range fp {
			if v < 0 {
				t.Errorf("fingerprint value negative: %f", v)
				break
			}
		}
	})

	t.Run("same text produces identical fingerprints", func(t *testing.T) {
		text := "hello world hello world"
		fp1 := ngramFingerprint(text, 3)
		fp2 := ngramFingerprint(text, 3)
		for i := range fp1 {
			if fp1[i] != fp2[i] {
				t.Errorf("fingerprints differ at index %d: %f vs %f", i, fp1[i], fp2[i])
				break
			}
		}
	})

	t.Run("case insensitive", func(t *testing.T) {
		fp1 := ngramFingerprint("HELLO WORLD", 3)
		fp2 := ngramFingerprint("hello world", 3)
		for i := range fp1 {
			if fp1[i] != fp2[i] {
				t.Errorf("case-insensitive fingerprints differ at index %d: %f vs %f", i, fp1[i], fp2[i])
				break
			}
		}
	})
}
