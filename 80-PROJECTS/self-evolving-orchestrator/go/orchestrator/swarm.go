package orchestrator

import (
	"context"
	"fmt"
	"strings"
	"sync"
	"time"
)

// SwarmTopology defines how agents coordinate
type SwarmTopology int

const (
	TopologyHierarchical SwarmTopology = iota
	TopologyMesh
	TopologyRing
	TopologyStar
)

// String returns a string representation of the topology
func (t SwarmTopology) String() string {
	switch t {
	case TopologyHierarchical:
		return "hierarchical"
	case TopologyMesh:
		return "mesh"
	case TopologyRing:
		return "ring"
	case TopologyStar:
		return "star"
	default:
		return "unknown"
	}
}

// ParseTopology converts a string to SwarmTopology
func ParseTopology(s string) SwarmTopology {
	s = strings.ToLower(strings.TrimSpace(s))
	switch s {
	case "hierarchical", "hierarchy":
		return TopologyHierarchical
	case "mesh":
		return TopologyMesh
	case "ring":
		return TopologyRing
	case "star":
		return TopologyStar
	default:
		return TopologyMesh
	}
}

// Swarm represents a group of agents coordinating on a task
type Swarm struct {
	ID        string
	Topology  SwarmTopology
	Agents    []*Agent
	Queen     *Agent   // For hierarchical topology
	Results   []ExecutionResult
	Consensus bool
	mu        sync.RWMutex
}

// SwarmConfig holds configuration for swarm execution
type SwarmConfig struct {
	Topology  SwarmTopology
	MaxAgents int
	Timeout   time.Duration
}

// DefaultSwarmConfig returns sensible defaults
func DefaultSwarmConfig() SwarmConfig {
	return SwarmConfig{
		Topology:  TopologyMesh,
		MaxAgents: 5,
		Timeout:   5 * time.Minute,
	}
}

// SwarmOrchestrator orchestrates multiple agents toward a shared goal
type SwarmOrchestrator struct {
	Config  SwarmConfig
	Router  *ProviderRouter
	Evolver *SelfEvolver
	Agents  []*Agent
	mu      sync.RWMutex
}

// NewSwarmOrchestrator creates a new swarm orchestrator
func NewSwarmOrchestrator(config SwarmConfig) *SwarmOrchestrator {
	return &SwarmOrchestrator{
		Config:  config,
		Router:  NewProviderRouter(),
		Evolver: NewSelfEvolver(),
		Agents:  []*Agent{},
	}
}

// SpawnAgents creates agents based on required types
func (s *SwarmOrchestrator) SpawnAgents(types []AgentType) []*Agent {
	s.mu.Lock()
	defer s.mu.Unlock()

	var agents []*Agent
	for i, agentType := range types {
		if i >= s.Config.MaxAgents {
			break
		}
		id := fmt.Sprintf("agent-%d", i)
		agent := NewAgent(id, agentType)
		agents = append(agents, agent)
	}
	s.Agents = agents
	return agents
}

// SpawnAgentsWithQueen creates agents with a designated queen for hierarchical topology
func (s *SwarmOrchestrator) SpawnAgentsWithQueen(workerTypes []AgentType, queenType AgentType) []*Agent {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Create queen first
	queen := NewAgent("queen-0", queenType)
	queen.Weight = 2.0 // Queen has higher weight

	var agents []*Agent
	agents = append(agents, queen)
	s.Agents = agents

	// Create workers
	for i, agentType := range workerTypes {
		if i >= s.Config.MaxAgents-1 {
			break
		}
		id := fmt.Sprintf("worker-%d", i)
		agent := NewAgent(id, agentType)
		agents = append(agents, agent)
	}

	s.Agents = agents
	return agents
}

// HierarchicalExecute: Queen decomposes task, assigns to workers, aggregates results
func (s *SwarmOrchestrator) HierarchicalExecute(ctx context.Context, task string) ([]ExecutionResult, error) {
	if len(s.Agents) < 2 {
		return nil, fmt.Errorf("hierarchical topology requires at least 2 agents")
	}

	queen := s.Agents[0]
	workers := s.Agents[1:]

	// Queen decomposes the task
	subtasks, err := s.decomposeTask(ctx, queen, task)
	if err != nil {
		return nil, fmt.Errorf("queen decomposition failed: %w", err)
	}

	// Assign subtasks to workers
	var results []ExecutionResult
	for i, subtask := range subtasks {
		worker := workers[i%len(workers)]
		result, err := s.executeTask(ctx, worker, subtask)
		if err != nil {
			results = append(results, ExecutionResult{
				Subtask:   subtask,
				Output:    "",
				Success:   false,
				Error:     err.Error(),
				Timestamp: time.Now(),
			})
		} else {
			results = append(results, *result)
		}
	}

	// Queen aggregates results
	aggregated := s.aggregateResults(results)
	results = append(results, ExecutionResult{
		Subtask:   "aggregation",
		Output:    aggregated,
		Success:   true,
		Timestamp: time.Now(),
	})

	return results, nil
}

// MeshExecute: All agents work in parallel, peer-to-peer sharing
func (s *SwarmOrchestrator) MeshExecute(ctx context.Context, task string) ([]ExecutionResult, error) {
	if len(s.Agents) == 0 {
		return nil, fmt.Errorf("mesh topology requires at least 1 agent")
	}

	// All agents work on the same task in parallel
	var wg sync.WaitGroup
	var mu sync.Mutex
	results := make([]ExecutionResult, 0, len(s.Agents))

	ctx, cancel := context.WithTimeout(ctx, s.Config.Timeout)
	defer cancel()

	for _, agent := range s.Agents {
		wg.Add(1)
		go func(a *Agent) {
			defer wg.Done()
			result, err := s.executeTask(ctx, a, task)
			mu.Lock()
			defer mu.Unlock()
			if err != nil {
				results = append(results, ExecutionResult{
					Subtask:   a.Name,
					Output:    "",
					Success:   false,
					Error:     err.Error(),
					Timestamp: time.Now(),
				})
			} else {
				results = append(results, *result)
			}
		}(agent)
	}

	wg.Wait()
	return results, nil
}

// RingExecute: Sequential pipeline, each passes output to next
func (s *SwarmOrchestrator) RingExecute(ctx context.Context, task string) ([]ExecutionResult, error) {
	if len(s.Agents) == 0 {
		return nil, fmt.Errorf("ring topology requires at least 1 agent")
	}

	var results []ExecutionResult
	currentTask := task

	for i, agent := range s.Agents {
		result, err := s.executeTask(ctx, agent, currentTask)
		if err != nil {
			results = append(results, ExecutionResult{
				Subtask:   agent.Name,
				Output:    "",
				Success:   false,
				Error:     err.Error(),
				Timestamp: time.Now(),
			})
			return results, fmt.Errorf("ring pipeline failed at agent %d: %w", i, err)
		}
		results = append(results, *result)
		currentTask = result.Output // Pass output to next agent
	}

	return results, nil
}

// StarExecute: Central hub coordinates, fans out and collects
func (s *SwarmOrchestrator) StarExecute(ctx context.Context, task string) ([]ExecutionResult, error) {
	if len(s.Agents) < 2 {
		return nil, fmt.Errorf("star topology requires at least 2 agents")
	}

	hub := s.Agents[0]
	spokes := s.Agents[1:]

	// Hub decomposes task
	subtasks, err := s.decomposeTask(ctx, hub, task)
	if err != nil {
		return nil, fmt.Errorf("hub decomposition failed: %w", err)
	}

	// Fan out to spokes in parallel
	var wg sync.WaitGroup
	var mu sync.Mutex
	results := make([]ExecutionResult, 0, len(spokes))

	ctx, cancel := context.WithTimeout(ctx, s.Config.Timeout)
	defer cancel()

	for i, subtask := range subtasks {
		spoke := spokes[i%len(spokes)]
		wg.Add(1)
		go func(sp *Agent, st string) {
			defer wg.Done()
			result, err := s.executeTask(ctx, sp, st)
			mu.Lock()
			defer mu.Unlock()
			if err != nil {
				results = append(results, ExecutionResult{
					Subtask:   st,
					Output:    "",
					Success:   false,
					Error:     err.Error(),
					Timestamp: time.Now(),
				})
			} else {
				results = append(results, *result)
			}
		}(spoke, subtask)
	}

	wg.Wait()

	// Hub aggregates
	aggregated := s.aggregateResults(results)
	results = append(results, ExecutionResult{
		Subtask:   "aggregation",
		Output:    aggregated,
		Success:   true,
		Timestamp: time.Now(),
	})

	return results, nil
}

// Execute runs the appropriate topology based on configuration
func (s *SwarmOrchestrator) Execute(ctx context.Context, task string) ([]ExecutionResult, error) {
	switch s.Config.Topology {
	case TopologyHierarchical:
		return s.HierarchicalExecute(ctx, task)
	case TopologyMesh:
		return s.MeshExecute(ctx, task)
	case TopologyRing:
		return s.RingExecute(ctx, task)
	case TopologyStar:
		return s.StarExecute(ctx, task)
	default:
		return s.MeshExecute(ctx, task)
	}
}

// decomposeTask uses an agent to decompose a task into subtasks
func (s *SwarmOrchestrator) decomposeTask(ctx context.Context, agent *Agent, task string) ([]string, error) {
	// Use the decomposer wrapper with current strategy
	decomposer := &SimpleDecomposer{}
	wrapper := NewDecomposerWrapper(decomposer)

	strategy := s.Evolver.GetNextStrategy()
	subtasks, err := wrapper.DecomposeWithStrategy(ctx, task, strategy)
	if err != nil {
		return nil, err
	}

	if len(subtasks) == 0 {
		return []string{task}, nil
	}
	return subtasks, nil
}

// executeTask runs a single task via an agent
func (s *SwarmOrchestrator) executeTask(ctx context.Context, agent *Agent, task string) (*ExecutionResult, error) {
	start := time.Now()

	// Build agent-specific prompt
	prompt := agent.BuildPrompt(task)

	// Route to appropriate provider
	complexity := s.estimateComplexity(task)
	config := s.Router.Route(prompt, complexity)

	// Execute via HTTP (placeholder - would call actual LLM API)
	output, err := s.callLLM(ctx, config, prompt)

	duration := time.Since(start)

	if err != nil {
		return &ExecutionResult{
			Subtask:  agent.Name,
			Output:   "",
			Success:  false,
			Error:    err.Error(),
			Duration: duration,
			Timestamp: time.Now(),
		}, nil // Return result with error flag, not the error
	}

	return &ExecutionResult{
		Subtask:   agent.Name,
		Output:    output,
		Success:   true,
		Duration:  duration,
		Timestamp: time.Now(),
	}, nil
}

// estimateComplexity estimates task complexity
func (s *SwarmOrchestrator) estimateComplexity(task string) ComplexityLevel {
	tokens := estimateTokens(task)
	if tokens < 50 {
		return ComplexitySimple
	}
	if tokens < 500 {
		return ComplexityMedium
	}
	return ComplexityComplex
}

// aggregateResults combines multiple results into one
func (s *SwarmOrchestrator) aggregateResults(results []ExecutionResult) string {
	var sb strings.Builder
	sb.WriteString("=== Aggregated Results ===\n\n")

	successCount := 0
	for _, r := range results {
		if r.Success {
			successCount++
			sb.WriteString(fmt.Sprintf("[%s] SUCCESS:\n%s\n\n", r.Subtask, r.Output))
		} else {
			sb.WriteString(fmt.Sprintf("[%s] FAILED: %s\n\n", r.Subtask, r.Error))
		}
	}

	sb.WriteString(fmt.Sprintf("=== Summary: %d/%d successful ===\n", successCount, len(results)))
	return sb.String()
}

// callLLM makes an API call to the LLM provider (placeholder)
func (s *SwarmOrchestrator) callLLM(ctx context.Context, config ModelConfig, prompt string) (string, error) {
	// TODO: Implement actual LLM API call
	// For now, return a placeholder that indicates the call would happen
	return fmt.Sprintf("[Would call %s/%s with %d tokens]", config.Provider.String(), config.Model, estimateTokens(prompt)), nil
}
