package orchestrator

import (
	"strings"
)

// LLMProvider represents an AI provider
type LLMProvider int

const (
	ProviderClaude LLMProvider = iota
	ProviderOpenAI
	ProviderGemini
	ProviderOllama
)

// ModelConfig holds provider model configuration
type ModelConfig struct {
	Provider        LLMProvider
	Name            string
	Model           string
	MaxTokens       int
	Temperature     float64
	CostPer1KTokens float64
	Endpoint        string // API endpoint (optional)
}

// ComplexityLevel represents task complexity for routing
type ComplexityLevel int

const (
	ComplexitySimple ComplexityLevel = iota
	ComplexityMedium
	ComplexityComplex
)

// String returns a string representation of the provider
func (p LLMProvider) String() string {
	switch p {
	case ProviderClaude:
		return "claude"
	case ProviderOpenAI:
		return "openai"
	case ProviderGemini:
		return "gemini"
	case ProviderOllama:
		return "ollama"
	default:
		return "unknown"
	}
}

// ParseProvider converts a string to LLMProvider
func ParseProvider(s string) LLMProvider {
	s = strings.ToLower(strings.TrimSpace(s))
	switch s {
	case "claude", "anthropic":
		return ProviderClaude
	case "openai", "gpt":
		return ProviderOpenAI
	case "gemini", "google":
		return ProviderGemini
	case "ollama", "local":
		return ProviderOllama
	default:
		return ProviderClaude
	}
}

// ProviderRouter selects optimal provider based on task complexity
type ProviderRouter struct {
	providers []ModelConfig
	fallback  ModelConfig
}

// NewProviderRouter creates router with default providers
func NewProviderRouter() *ProviderRouter {
	return &ProviderRouter{
		providers: []ModelConfig{
			{
				Provider:        ProviderClaude,
				Name:            "Claude Sonnet",
				Model:           "claude-sonnet-4.6",
				MaxTokens:       200000,
				Temperature:     0.7,
				CostPer1KTokens: 0.003,
			},
			{
				Provider:        ProviderClaude,
				Name:            "Claude Opus",
				Model:           "claude-opus-4.6",
				MaxTokens:       200000,
				Temperature:     0.7,
				CostPer1KTokens: 0.015,
			},
			{
				Provider:        ProviderClaude,
				Name:            "Claude Haiku",
				Model:           "claude-haiku-4.5",
				MaxTokens:       200000,
				Temperature:     0.7,
				CostPer1KTokens: 0.0008,
			},
			{
				Provider:        ProviderOpenAI,
				Name:            "GPT-5.4",
				Model:           "gpt-5.4",
				MaxTokens:       128000,
				Temperature:     0.7,
				CostPer1KTokens: 0.002,
			},
			{
				Provider:        ProviderGemini,
				Name:            "Gemini 3.1 Flash",
				Model:           "gemini-3.1-flash",
				MaxTokens:       1000000,
				Temperature:     0.7,
				CostPer1KTokens: 0.0001,
			},
			{
				Provider:        ProviderOllama,
				Name:            "Llama 3.2",
				Model:           "llama3.2",
				MaxTokens:       128000,
				Temperature:     0.7,
				CostPer1KTokens: 0.0, // local, free
				Endpoint:        "http://localhost:11434",
			},
		},
		fallback: ModelConfig{
			Provider:        ProviderClaude,
			Name:            "Claude Sonnet (fallback)",
			Model:           "claude-sonnet-4.6",
			MaxTokens:       200000,
			Temperature:     0.7,
			CostPer1KTokens: 0.003,
		},
	}
}

// Route selects optimal provider for task complexity
// simple: token estimate < 50 → Ollama/fast
// medium: token estimate < 500 → Sonnet-class
// complex: token estimate >= 500 → Opus-class
func (r *ProviderRouter) Route(task string, complexity ComplexityLevel) ModelConfig {
	tokenEstimate := estimateTokens(task)

	for _, p := range r.providers {
		switch complexity {
		case ComplexitySimple:
			// Prefer cheap/fast models for simple tasks
			if p.CostPer1KTokens < 0.001 || p.Provider == ProviderOllama {
				if tokenEstimate < 100 {
					return p
				}
			}
		case ComplexityMedium:
			// Prefer mid-tier models
			if p.CostPer1KTokens < 0.005 && p.Provider != ProviderOllama {
				return p
			}
		case ComplexityComplex:
			// Prefer strongest models for complex tasks
			if p.Provider == ProviderClaude && strings.Contains(strings.ToLower(p.Name), "opus") {
				return p
			}
			if strings.Contains(strings.ToLower(p.Model), "opus") {
				return p
			}
		}
	}

	// Fallback to default
	switch complexity {
	case ComplexitySimple:
		// Return cheapest
		for _, p := range r.providers {
			if p.CostPer1KTokens > 0 {
				return p
			}
		}
	case ComplexityMedium:
		return r.providers[0] // Claude Sonnet
	case ComplexityComplex:
		// Return Opus if available
		for _, p := range r.providers {
			if strings.Contains(strings.ToLower(p.Model), "opus") {
				return p
			}
		}
	}

	return r.fallback
}

// RouteByTokenEstimate routes based on actual token count
func (r *ProviderRouter) RouteByTokenEstimate(tokens int) ModelConfig {
	if tokens < 50 {
		// Simple: use cheapest
		for _, p := range r.providers {
			if p.Provider == ProviderOllama {
				return p
			}
		}
		for _, p := range r.providers {
			if p.CostPer1KTokens < 0.001 {
				return p
			}
		}
	}
	if tokens < 500 {
		// Medium: balanced cost/quality
		for _, p := range r.providers {
			if p.CostPer1KTokens < 0.005 {
				return p
			}
		}
	}
	// Complex: use best available
	for _, p := range r.providers {
		if strings.Contains(strings.ToLower(p.Model), "opus") {
			return p
		}
	}
	return r.fallback
}

// GetByProvider returns config for specific provider
func (r *ProviderRouter) GetByProvider(p LLMProvider) ModelConfig {
	for _, cfg := range r.providers {
		if cfg.Provider == p {
			return cfg
		}
	}
	return r.fallback
}

// GetByModel returns config for specific model
func (r *ProviderRouter) GetByModel(model string) ModelConfig {
	model = strings.ToLower(model)
	for _, cfg := range r.providers {
		if strings.Contains(strings.ToLower(cfg.Model), model) {
			return cfg
		}
	}
	return r.fallback
}

// GetAllProviders returns all configured providers
func (r *ProviderRouter) GetAllProviders() []ModelConfig {
	return r.providers
}

// estimateTokens provides a rough token estimate
func estimateTokens(text string) int {
	// Rough estimate: ~4 chars per token for English
	return len(text) / 4
}
