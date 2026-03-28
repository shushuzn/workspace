package orchestrator

import (
	"context"
	"testing"
	"time"
)

// MockDecomposer always returns the same subtasks
type MockDecomposer struct {
	subtasks []string
	err      error
}

func (m *MockDecomposer) Decompose(ctx context.Context, task string) ([]string, error) {
	if m.err != nil {
		return nil, m.err
	}
	return m.subtasks, nil
}

// TestOrchestratorAgent_Process tests the full orchestration flow with mocked dependencies
func TestOrchestratorAgent_Process(t *testing.T) {
	// Create a mock invoke function
	mockInvoke := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
		return map[string]interface{}{"result": "done: " + args["script"]}, nil
	}

	// Create mock peers
	mockPeers := func() map[string]*PeerConnection {
		return map[string]*PeerConnection{
			"peer1": {Info: struct{ ID, Name string }{ID: "peer1", Name: "Peer1"}},
			"peer2": {Info: struct{ ID, Name string }{ID: "peer2", Name: "Peer2"}},
		}
	}

	orch := NewOrchestratorAgent(
		"test-agent",
		&MockDecomposer{subtasks: []string{"do thing 1", "do thing 2"}},
		mockInvoke,
		mockPeers,
	)

	ctx := context.Background()
	result, err := orch.Process(ctx, "do things")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if result == "" {
		t.Error("expected non-empty result")
	}
	t.Logf("Orchestration result: %s", result)
}

// TestOrchestratorAgent_NoPeers tests error handling when no peers are available
func TestOrchestratorAgent_NoPeers(t *testing.T) {
	mockInvoke := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
		return nil, nil
	}

	mockPeers := func() map[string]*PeerConnection {
		return map[string]*PeerConnection{} // No peers
	}

	orch := NewOrchestratorAgent(
		"test-agent",
		&MockDecomposer{subtasks: []string{"do thing 1"}},
		mockInvoke,
		mockPeers,
	)

	ctx := context.Background()
	_, err := orch.Process(ctx, "do things")
	if err == nil {
		t.Error("expected error when no peers available")
	}
}

// TestOrchestratorAgent_DecomposeError tests error handling when decomposition fails
func TestOrchestratorAgent_DecomposeError(t *testing.T) {
	mockInvoke := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
		return nil, nil
	}

	mockPeers := func() map[string]*PeerConnection {
		return map[string]*PeerConnection{
			"peer1": {Info: struct{ ID, Name string }{ID: "peer1"}},
		}
	}

	orch := NewOrchestratorAgent(
		"test-agent",
		&MockDecomposer{err: context.DeadlineExceeded},
		mockInvoke,
		mockPeers,
	)

	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()

	_, err := orch.Process(ctx, "do things")
	if err == nil {
		t.Error("expected error when decomposition fails")
	}
}

// TestOrchestratorAgent_EmptySubtasks tests error handling when no subtasks are generated
func TestOrchestratorAgent_EmptySubtasks(t *testing.T) {
	mockInvoke := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
		return nil, nil
	}

	mockPeers := func() map[string]*PeerConnection {
		return map[string]*PeerConnection{
			"peer1": {Info: struct{ ID, Name string }{ID: "peer1"}},
		}
	}

	orch := NewOrchestratorAgent(
		"test-agent",
		&MockDecomposer{subtasks: []string{}}, // Empty subtasks
		mockInvoke,
		mockPeers,
	)

	ctx := context.Background()
	_, err := orch.Process(ctx, "do things")
	if err == nil {
		t.Error("expected error when no subtasks generated")
	}
}
