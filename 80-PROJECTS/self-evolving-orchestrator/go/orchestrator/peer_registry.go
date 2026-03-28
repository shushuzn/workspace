package orchestrator

import (
	"sync"
	"time"
)

// AgentStatus represents peer status
type AgentStatus string

const (
	StatusIdle    AgentStatus = "idle"
	StatusActive AgentStatus = "active"
	StatusError  AgentStatus = "error"
	StatusOffline AgentStatus = "offline"
)

// PeerInfo holds peer agent information
type PeerInfo struct {
	ID           string
	Name         string
	Capabilities []string
	Status       AgentStatus
	Load         float64
	LastSeen     time.Time
}

// PeerRegistry manages available peer agents
type PeerRegistry struct {
	peers map[string]*PeerInfo
	mu    sync.RWMutex
}

// NewPeerRegistry creates a new peer registry
func NewPeerRegistry() *PeerRegistry {
	return &PeerRegistry{
		peers: make(map[string]*PeerInfo),
	}
}

// Register adds or updates a peer
func (r *PeerRegistry) Register(peer *PeerInfo) {
	r.mu.Lock()
	defer r.mu.Unlock()
	peer.LastSeen = time.Now()
	r.peers[peer.ID] = peer
}

// Unregister removes a peer
func (r *PeerRegistry) Unregister(id string) bool {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, exists := r.peers[id]; exists {
		delete(r.peers, id)
		return true
	}
	return false
}

// Get retrieves a peer by ID
func (r *PeerRegistry) Get(id string) (*PeerInfo, bool) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	peer, exists := r.peers[id]
	return peer, exists
}

// List returns all peers
func (r *PeerRegistry) List() []*PeerInfo {
	r.mu.RLock()
	defer r.mu.RUnlock()
	peers := make([]*PeerInfo, 0, len(r.peers))
	for _, peer := range r.peers {
		peers = append(peers, peer)
	}
	return peers
}

// ListByCapability returns peers with a specific capability
func (r *PeerRegistry) ListByCapability(capability string) []*PeerInfo {
	r.mu.RLock()
	defer r.mu.RUnlock()
	var peers []*PeerInfo
	for _, peer := range r.peers {
		for _, cap := range peer.Capabilities {
			if cap == capability {
				peers = append(peers, peer)
				break
			}
		}
	}
	return peers
}

// UpdateStatus updates a peer's status
func (r *PeerRegistry) UpdateStatus(id string, status AgentStatus) bool {
	r.mu.Lock()
	defer r.mu.Unlock()
	if peer, exists := r.peers[id]; exists {
		peer.Status = status
		peer.LastSeen = time.Now()
		return true
	}
	return false
}
