package core

import (
	"fmt"
	"sync"

	"github.com/openclaw/multi-agent-discuss/pkg/executor"
	"github.com/openclaw/multi-agent-discuss/pkg/orchestrator"
	"github.com/openclaw/multi-agent-discuss/pkg/proto"
	"github.com/openclaw/multi-agent-discuss/pkg/toolclient"
	"github.com/openclaw/multi-agent-discuss/pkg/transport"
)

type PeerConnection struct {
	Info   *proto.AgentInfo
	Port   int
}

type Agent struct {
	ID           string
	Name         string
	Port         int
	Capabilities []*proto.Capability
	Peers        map[string]*PeerConnection
	exec        *executor.Executor
	toolClient   *toolclient.ToolClient
	orchestrator *orchestrator.OrchestratorAgent
	mu           sync.RWMutex
}

func NewAgent(id, name string, port int, caps []*proto.Capability) *Agent {
	exec := executor.NewExecutor(id)
	exec.SetupTools()
	return &Agent{
		ID:           id,
		Name:         name,
		Port:         port,
		Capabilities: caps,
		Peers:        make(map[string]*PeerConnection),
		exec:        exec,
	}
}

func (a *Agent) AddPeer(peer *PeerConnection) {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.Peers[peer.Info.Id] = peer
}

func (a *Agent) RemovePeer(id string) {
	a.mu.Lock()
	defer a.mu.Unlock()
	delete(a.Peers, id)
}

func (a *Agent) GetPeers() map[string]*PeerConnection {
	a.mu.RLock()
	defer a.mu.RUnlock()
	return a.Peers
}

func (a *Agent) GetPeer(id string) (*PeerConnection, bool) {
	a.mu.RLock()
	defer a.mu.RUnlock()
	p, ok := a.Peers[id]
	return p, ok
}

// GetExecutor returns the agent's executor for use with the dispatcher.
func (a *Agent) GetExecutor() *executor.Executor {
	return a.exec
}

// GetOrchestrator returns the agent's orchestrator for task decomposition and parallel execution.
func (a *Agent) GetOrchestrator() *orchestrator.OrchestratorAgent {
	return a.orchestrator
}

// AgentInfo returns the agent's own AgentInfo for sharing with peers.
func (a *Agent) AgentInfo() *proto.AgentInfo {
	return &proto.AgentInfo{
		Id:           a.ID,
		Name:         a.Name,
		Port:         int32(a.Port),
		Capabilities: a.Capabilities,
	}
}

// InvokeTool invokes a tool on a peer agent by ID.
// It dials the peer, creates a temporary ToolClient, invokes the tool, and returns.
func (a *Agent) InvokeTool(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
	// Find peer by ID from discovery
	peer, ok := a.GetPeer(peerID)
	if !ok {
		return nil, fmt.Errorf("peer not found: %s", peerID)
	}

	// Dial peer via transport
	addr := fmt.Sprintf("localhost:%d", peer.Info.Port)
	client, err := transport.DialAgent(addr, a.AgentInfo())
	if err != nil {
		return nil, fmt.Errorf("dial peer %s: %w", peerID, err)
	}
	defer client.Close()

	// Create ToolClient and invoke tool
	tc := toolclient.NewToolClient(client, a.ID)
	return tc.InvokeTool(tool, args)
}
