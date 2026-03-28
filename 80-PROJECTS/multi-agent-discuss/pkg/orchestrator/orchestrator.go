package orchestrator

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/openclaw/multi-agent-discuss/pkg/core"
)

// TaskRequest represents a single task invocation request
type TaskRequest struct {
	PeerID string
	Tool   string
	Args   map[string]string
}

// OrchestratorAgent orchestrates task decomposition and parallel execution
type OrchestratorAgent struct {
	agentID    string
	decomposer LLMDecomposer
	invokeFn   func(peerID, tool string, args map[string]string) (map[string]interface{}, error)
	peers      func() map[string]*core.PeerConnection
}

// NewOrchestratorAgent creates a new OrchestratorAgent
func NewOrchestratorAgent(
	agentID string,
	decomposer LLMDecomposer,
	invokeFn func(peerID, tool string, args map[string]string) (map[string]interface{}, error),
	peers func() map[string]*core.PeerConnection,
) *OrchestratorAgent {
	return &OrchestratorAgent{
		agentID:    agentID,
		decomposer: decomposer,
		invokeFn:   invokeFn,
		peers:      peers,
	}
}

// Process orchestrates a task: decompose via LLM, dispatch to peers, return first result
func (o *OrchestratorAgent) Process(ctx context.Context, task string) (string, error) {
	// Step 1: Decompose task via LLM
	subtasks, err := o.decomposer.Decompose(ctx, task)
	if err != nil {
		return "", err
	}

	if len(subtasks) == 0 {
		return "", fmt.Errorf("task could not be decomposed")
	}

	// Step 2: Get available peers
	peerMap := o.peers()
	if len(peerMap) == 0 {
		return "", fmt.Errorf("no peer agents available")
	}

	// Convert map to slice
	peers := make([]string, 0, len(peerMap))
	for id := range peerMap {
		peers = append(peers, id)
	}

	// Step 3: Build requests - one per subtask per peer
	requests := make([]TaskRequest, 0, len(subtasks)*len(peers))
	for _, subtask := range subtasks {
		for _, peerID := range peers {
			requests = append(requests, TaskRequest{
				PeerID: peerID,
				Tool:   "code",
				Args: map[string]string{
					"script": subtask,
					"lang":   "bash",
				},
			})
		}
	}

	// Step 4: Race for first result
	timeout := 30 * time.Second
	if deadline, ok := ctx.Deadline(); ok {
		timeout = time.Until(deadline)
		if timeout <= 0 {
			return "", fmt.Errorf("orchestration timeout")
		}
	}

	result, err := raceResults(ctx, requests, o.invokeFn, timeout)
	if err != nil {
		return "", err
	}

	return result, nil
}

// raceResults runs requests in parallel and returns the first successful result
func raceResults(
	ctx context.Context,
	requests []TaskRequest,
	invokeFn func(peerID, tool string, args map[string]string) (map[string]interface{}, error),
	timeout time.Duration,
) (string, error) {
	if len(requests) == 0 {
		return "", fmt.Errorf("no requests to execute")
	}

	type result struct {
		value string
		err   error
	}

	resultCh := make(chan result, 1)
	sem := make(chan struct{}, 10) // Max 10 parallel
	var wg sync.WaitGroup

	for _, req := range requests {
		select {
		case <-ctx.Done():
			break
		default:
		}

		wg.Add(1)
		go func(r TaskRequest) {
			defer wg.Done()

			select {
			case sem <- struct{}{}:
			case <-ctx.Done():
				return
			}
			defer func() { <-sem }()

			execCtx, cancel := context.WithTimeout(ctx, timeout)
			defer cancel()

			res, err := invokeFn(r.PeerID, r.Tool, r.Args)
			if err != nil {
				return
			}

			if resultMap, ok := res["result"]; ok {
				if resultStr, ok := resultMap.(string); ok {
					select {
					case resultCh <- result{value: resultStr}:
					default:
					}
				}
			}
		}(req)
	}

	go func() {
		wg.Wait()
		close(resultCh)
	}()

	select {
	case res := <-resultCh:
		if res.err != nil {
			return "", res.err
		}
		return res.value, nil
	case <-ctx.Done():
		return "", fmt.Errorf("orchestration cancelled")
	case <-time.After(timeout):
		return "", fmt.Errorf("all subtasks failed after timeout")
	}
}
