package orchestrator

import (
	"fmt"
	"strings"
)

// AgentType represents a specialized agent role
type AgentType int

const (
	AgentTypeGeneral AgentType = iota
	AgentTypeCoder
	AgentTypeReviewer
	AgentTypeTester
	AgentTypeSecurityAuditor
	AgentTypeDocumenter
	AgentTypeDevOps
)

// Agent represents a specialized agent with specific capabilities
type Agent struct {
	ID     string
	Type   AgentType
	Name   string
	Model  string
	Weight float64
	Active bool
}

// AgentSpec defines the capabilities and defaults for an agent type
type AgentSpec struct {
	Type           AgentType
	Name           string
	PromptRole     string
	DefaultModel   string
	MaxConcurrent  int
}

// agentSpecs holds the definition for each agent type
var agentSpecs = []AgentSpec{
	{
		Type:          AgentTypeGeneral,
		Name:          "General",
		PromptRole:    "general assistant",
		DefaultModel:   "claude-sonnet-4.6",
		MaxConcurrent: 3,
	},
	{
		Type:          AgentTypeCoder,
		Name:          "Coder",
		PromptRole:    "software developer implementing code changes and refactors",
		DefaultModel:   "claude-sonnet-4.6",
		MaxConcurrent: 5,
	},
	{
		Type:          AgentTypeReviewer,
		Name:          "Reviewer",
		PromptRole:    "code reviewer validating logic, correctness, and style",
		DefaultModel:   "claude-sonnet-4.6",
		MaxConcurrent: 3,
	},
	{
		Type:          AgentTypeTester,
		Name:          "Tester",
		PromptRole:    "test engineer generating and executing tests",
		DefaultModel:   "claude-sonnet-4.6",
		MaxConcurrent: 4,
	},
	{
		Type:          AgentTypeSecurityAuditor,
		Name:          "SecurityAuditor",
		PromptRole:    "security expert detecting vulnerabilities and threats",
		DefaultModel:   "claude-opus-4.6",
		MaxConcurrent: 2,
	},
	{
		Type:          AgentTypeDocumenter,
		Name:          "Documenter",
		PromptRole:    "technical writer creating documentation and comments",
		DefaultModel:   "claude-haiku-4.5",
		MaxConcurrent: 4,
	},
	{
		Type:          AgentTypeDevOps,
		Name:          "DevOps",
		PromptRole:    "DevOps engineer handling CI/CD, deployments, and infrastructure",
		DefaultModel:   "claude-sonnet-4.6",
		MaxConcurrent: 3,
	},
}

// NewAgent creates a new agent with defaults based on type
func NewAgent(id string, agentType AgentType) *Agent {
	spec := GetSpec(agentType)
	return &Agent{
		ID:     id,
		Type:   agentType,
		Name:   spec.Name,
		Model:  spec.DefaultModel,
		Weight: 1.0,
		Active: true,
	}
}

// GetSpec returns the spec for an agent type
func GetSpec(agentType AgentType) AgentSpec {
	if agentType >= 0 && int(agentType) < len(agentSpecs) {
		return agentSpecs[agentType]
	}
	return agentSpecs[AgentTypeGeneral]
}

// GetAgentName returns a human-readable name for the agent type
func GetAgentName(agentType AgentType) string {
	return GetSpec(agentType).Name
}

// String returns a string representation of the agent type
func (a AgentType) String() string {
	switch a {
	case AgentTypeGeneral:
		return "general"
	case AgentTypeCoder:
		return "coder"
	case AgentTypeReviewer:
		return "reviewer"
	case AgentTypeTester:
		return "tester"
	case AgentTypeSecurityAuditor:
		return "security-auditor"
	case AgentTypeDocumenter:
		return "documenter"
	case AgentTypeDevOps:
		return "devops"
	default:
		return "unknown"
	}
}

// ParseAgentType converts a string to AgentType
func ParseAgentType(s string) AgentType {
	s = strings.ToLower(strings.TrimSpace(s))
	switch s {
	case "coder":
		return AgentTypeCoder
	case "reviewer":
		return AgentTypeReviewer
	case "tester":
		return AgentTypeTester
	case "security-auditor", "security":
		return AgentTypeSecurityAuditor
	case "documenter", "docs":
		return AgentTypeDocumenter
	case "devops":
		return AgentTypeDevOps
	default:
		return AgentTypeGeneral
	}
}

// BuildPrompt builds an agent-specific prompt with context
func (a *Agent) BuildPrompt(task string) string {
	spec := GetSpec(a.Type)
	return fmt.Sprintf("You are a %s. %s\n\nTask: %s", spec.Name, spec.PromptRole, task)
}

// GetProvider returns the LLM provider name for the agent's model
func (a *Agent) GetProvider() string {
	model := strings.ToLower(a.Model)
	if strings.Contains(model, "claude") {
		return "anthropic"
	}
	if strings.Contains(model, "gpt") || strings.Contains(model, "o1") || strings.Contains(model, "o3") {
		return "openai"
	}
	if strings.Contains(model, "gemini") {
		return "google"
	}
	if strings.Contains(model, "llama") || strings.Contains(model, "ollama") {
		return "ollama"
	}
	return "anthropic" // default
}
