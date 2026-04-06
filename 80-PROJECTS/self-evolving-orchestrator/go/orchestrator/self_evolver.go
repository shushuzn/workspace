package orchestrator

import (
    "context"
    "fmt"
    "math"
    "strings"
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

    // Refine if score critically low
    if record.Score < 0.3 {
        return true, fmt.Sprintf("score %f critically low", record.Score)
    }

    // Refine if excessive overlap (detected by similar outputs)
    if s.detectOverlap(ctx, record.Results) {
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

// GetStrategyPool returns the current strategy pool
func (s *SelfEvolver) GetStrategyPool() []DecomposeStrategy {
    return s.strategyPool
}

// ResetHistory clears the evolution history
func (s *SelfEvolver) ResetHistory() {
    s.history = []EvolutionRecord{}
    s.currentStrategy = 0
}

// sharedEmbedder is the global embedder for semantic overlap detection
var sharedEmbedder *OllamaEmbedder

// SetEmbedder configures the shared embedder instance
func SetEmbedder(embedder *OllamaEmbedder) {
	sharedEmbedder = embedder
}

// detectOverlap returns true if any two results have cosine similarity > 0.85
// Uses embeddings when embedder is configured, falls back to n-gram fingerprints
func (s *SelfEvolver) detectOverlap(ctx context.Context, results []ExecutionResult) bool {
	if len(results) < 2 {
		return false
	}

	// Fast path: if no embedder, use legacy n-gram
	if sharedEmbedder == nil {
		return s.legacyDetectOverlap(results)
	}

	// Semantic path: embed all outputs and compare
	texts := make([]string, len(results))
	for i, r := range results {
		texts[i] = r.Output
	}

	vectors, err := sharedEmbedder.EmbedBatch(ctx, texts)
	if err != nil || len(vectors) == 0 {
		return s.legacyDetectOverlap(results)
	}

	for i := 0; i < len(results); i++ {
		for j := i + 1; j < len(results); j++ {
			if len(vectors[i]) == 0 || len(vectors[j]) == 0 {
				continue
			}
			if CosineSimilarity(vectors[i], vectors[j]) > 0.85 {
				return true
			}
		}
	}
	return false
}

// legacyDetectOverlap uses n-gram fingerprinting (original implementation)
func (s *SelfEvolver) legacyDetectOverlap(results []ExecutionResult) bool {
	vectors := make([][]float64, len(results))
	for i, r := range results {
		vectors[i] = ngramFingerprint(r.Output, 3)
	}
	for i := 0; i < len(results); i++ {
		for j := i + 1; j < len(results); j++ {
			if cosineSim(vectors[i], vectors[j]) > 0.85 {
				return true
			}
		}
	}
	return false
}

// ngramFingerprint creates a sparse TF-like vector from n-gram hashes
func ngramFingerprint(text string, n int) []float64 {
    // Use 100 buckets — hash each n-gram, increment bucket
    buckets := make([]float64, 100)
    if len(text) < n {
        return buckets
    }
    textLower := strings.ToLower(text)
    for i := 0; i <= len(textLower)-n; i++ {
        gram := textLower[i : i+n]
        bucket := int(uint64(hashString(gram)) % 100)
        buckets[bucket]++
    }
    // L2 normalize
    var norm float64
    for _, v := range buckets {
        norm += v * v
    }
    norm = math.Sqrt(norm)
    if norm > 0 {
        for i := range buckets {
            buckets[i] /= norm
        }
    }
    return buckets
}

func hashString(s string) uint64 {
    // Simple FNV-1a
    var h uint64 = 14695981039346656037
    for i := 0; i < len(s); i++ {
        h ^= uint64(s[i])
        h *= 1099511628211
    }
    return h
}

func cosineSim(a, b []float64) float64 {
    if len(a) != len(b) || len(a) == 0 {
        return 0
    }
    var dot float64
    for i := 0; i < len(a); i++ {
        dot += a[i] * b[i]
    }
    return dot
}
