package core

import (
	"sync"

	"github.com/openclaw/multi-agent-discuss/pkg/proto"
)

type PeerConnection struct {
	Info   *proto.AgentInfo
	Port   int
}

type Agent struct {
	ID           string
	Name         string
	Port         int
	Capabilities []proto.Capability
	Peers        map[string]*PeerConnection
	mu           sync.RWMutex
}

func NewAgent(id, name string, port int, caps []proto.Capability) *Agent {
	return &Agent{
		ID:           id,
		Name:         name,
		Port:         port,
		Capabilities: caps,
		Peers:        make(map[string]*PeerConnection),
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
