package discovery

import (
	"context"
	"fmt"
	"net"
	"sync"

	"github.com/openclaw/multi-agent-discuss/pkg/proto"
)

type Discovery struct {
	agentID    string
	port       int
	peers      map[string]*proto.AgentInfo
	onDiscover func(*proto.AgentInfo)
	onRemove   func(string)
	ln         net.Listener
	stopCh     chan struct{}
	mu         sync.RWMutex
}

func NewDiscovery(agentID string, port int) *Discovery {
	return &Discovery{
		agentID: agentID,
		port:    port,
		peers:   make(map[string]*proto.AgentInfo),
		stopCh:  make(chan struct{}),
	}
}

func (d *Discovery) Start(ctx context.Context, info *proto.AgentInfo, onDiscover func(*proto.AgentInfo), onRemove func(string)) error {
	d.onDiscover = onDiscover
	d.onRemove = onRemove

	// Start broadcast discovery server
	discPort := 5353 + (d.port % 1000)
	ln, err := net.Listen("tcp", fmt.Sprintf(":%d", discPort))
	if err != nil {
		return fmt.Errorf("listen for discovery: %w", err)
	}
	d.ln = ln

	go d.acceptLoop(ctx, info)

	// Broadcast our presence
	go d.announce(info)

	return nil
}

func (d *Discovery) acceptLoop(ctx context.Context, localInfo *proto.AgentInfo) {
	for {
		conn, err := d.ln.Accept()
		if err != nil {
			select {
			case <-d.stopCh:
				return
			case <-ctx.Done():
				return
			default:
				continue
			}
		}
		go d.handleConnection(conn.(*net.TCPConn), localInfo)
	}
}

func (d *Discovery) handleConnection(conn net.Conn, localInfo *proto.AgentInfo) {
	defer conn.Close()

	// Send our info
	fmt.Fprintf(conn, "AGENT:%s:%d:%s\n", localInfo.Id, localInfo.Port, localInfo.Name)

	// Read peer info
	buf := make([]byte, 1024)
	n, err := conn.Read(buf)
	if err != nil {
		return
	}

	var peerID string
	var peerPort int
	var peerName string
	if _, err := fmt.Sscanf(string(buf[:n]), "AGENT:%s:%d:%s", &peerID, &peerPort, &peerName); err == nil {
		if peerID != localInfo.Id {
			peerInfo := &proto.AgentInfo{
				Id:   peerID,
				Name: peerName,
				Port: int32(peerPort),
			}
			d.addPeer(peerInfo)
		}
	}
}

func (d *Discovery) announce(info *proto.AgentInfo) {
	// Try to connect to known discovery ports on localhost
	for i := 0; i < 10; i++ {
		discPort := 5353 + i*10
		if discPort == 5353+(d.port%1000) {
			continue // skip our own port
		}
		conn, err := net.Dial("tcp", fmt.Sprintf("localhost:%d", discPort))
		if err != nil {
			continue
		}
		fmt.Fprintf(conn, "AGENT:%s:%d:%s\n", info.Id, info.Port, info.Name)
		conn.Close()
	}
}

func (d *Discovery) addPeer(info *proto.AgentInfo) {
	d.mu.Lock()
	defer d.mu.Unlock()

	if _, exists := d.peers[info.Id]; !exists {
		d.peers[info.Id] = info
		if d.onDiscover != nil {
			d.onDiscover(info)
		}
	}
}

func (d *Discovery) Stop() {
	close(d.stopCh)
	if d.ln != nil {
		d.ln.Close()
	}
}

func (d *Discovery) GetPeers() []*proto.AgentInfo {
	d.mu.RLock()
	defer d.mu.RUnlock()

	result := make([]*proto.AgentInfo, 0, len(d.peers))
	for _, p := range d.peers {
		result = append(result, p)
	}
	return result
}
