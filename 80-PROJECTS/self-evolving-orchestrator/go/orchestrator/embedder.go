package orchestrator

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"net/http"
	"sync"
	"time"
)

// OllamaEmbedder creates embeddings via Ollama's /api/embeddings endpoint
type OllamaEmbedder struct {
	baseURL string
	model   string
	client  *http.Client
	mu      sync.Mutex // serialize calls to avoid Ollama overload
}

// NewOllamaEmbedder creates an embedder pointing at the given base URL and model
func NewOllamaEmbedder(baseURL, model string) *OllamaEmbedder {
	if baseURL == "" {
		baseURL = "http://localhost:11434"
	}
	if model == "" {
		model = "llama3.2:1b"
	}
	return &OllamaEmbedder{
		baseURL: baseURL,
		model:   model,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// Embed returns a dense vector for the given text
func (e *OllamaEmbedder) Embed(ctx context.Context, text string) ([]float64, error) {
	reqBody := map[string]interface{}{
		"model":  e.model,
		"prompt": text,
	}

	body, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("embed: marshal: %w", err)
	}

	url := e.baseURL + "/api/embeddings"
	req, err := http.NewRequestWithContext(ctx, "POST", url, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("embed: new request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := e.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("embed: request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		respBody, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("embed: status %d: %s", resp.StatusCode, string(respBody))
	}

	var result struct {
		Embedding []float64 `json:"embedding"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, fmt.Errorf("embed: decode: %w", err)
	}

	return result.Embedding, nil
}

// EmbedBatch embeds multiple texts concurrently
func (e *OllamaEmbedder) EmbedBatch(ctx context.Context, texts []string) ([][]float64, error) {
	results := make([][]float64, len(texts))
	errChan := make(chan error, len(texts))

	for i, text := range texts {
		go func(idx int, txt string) {
			vec, err := e.Embed(ctx, txt)
			if err != nil {
				errChan <- err
				return
			}
			results[idx] = vec
			errChan <- nil
		}(i, text)
	}

	for i := 0; i < len(texts); i++ {
		if err := <-errChan; err != nil {
			return nil, err
		}
	}

	return results, nil
}

// CosineSimilarity computes cosine similarity between two vectors
func CosineSimilarity(a, b []float64) float64 {
	if len(a) != len(b) || len(a) == 0 {
		return 0
	}
	var dot, normA, normB float64
	for i := range a {
		dot += a[i] * b[i]
		normA += a[i] * a[i]
		normB += b[i] * b[i]
	}
	if normA == 0 || normB == 0 {
		return 0
	}
	return dot / (math.Sqrt(normA) * math.Sqrt(normB))
}
