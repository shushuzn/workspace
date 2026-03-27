package discovery

import (
	"context"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net"
	"sync"
	"time"

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

	// Broadcast our presence periodically
	go d.announcePeriodic(info)

	return nil
}

func (d *Discovery) announcePeriodic(info *proto.AgentInfo) {
	// Announce immediately
	d.announce(info)
	// Then repeat every 2 seconds
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-d.stopCh:
			return
		case <-ticker.C:
			d.announce(info)
		}
	}
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
		go d.handleConnection(conn, localInfo)
	}
}

func (d *Discovery) handleConnection(conn net.Conn, localInfo *proto.AgentInfo) {
	defer conn.Close()

	// Read length-prefixed message
	var length [4]byte
	if _, err := io.ReadFull(conn, length[:]); err != nil {
		return
	}
	size := binary.BigEndian.Uint32(length[:])
	if size > 4096 {
		return
	}

	data := make([]byte, size)
	if _, err := io.ReadFull(conn, data); err != nil {
		return
	}

	var peerInfo proto.AgentInfo
	if err := json.Unmarshal(data, &peerInfo); err != nil {
		return
	}

	if peerInfo.Id == localInfo.Id {
		return
	}

	// Add peer
	d.addPeer(&peerInfo)

	// Send our info back
	selfData, _ := json.Marshal(&proto.AgentInfo{
		Id:   localInfo.Id,
		Name: localInfo.Name,
		Port: localInfo.Port,
	})
	var selfLen [4]byte
	binary.BigEndian.PutUint32(selfLen[:], uint32(len(selfData)))
	if _, err := conn.Write(selfLen[:]); err != nil {
		return
	}
	conn.Write(selfData)
}

func (d *Discovery) announce(info *proto.AgentInfo) {
	concurrency := 100
	sem := make(chan struct{}, concurrency)
	var wg sync.WaitGroup
	found := 0
	connected := 0

	for port := 5000; port < 6000; port++ {
		if port == 5353+(d.port%1000) {
			continue
		}

		wg.Add(1)
		go func(p int) {
			defer wg.Done()
			sem <- struct{}{}
			defer func() { <-sem }()

			conn, err := net.DialTimeout("tcp", fmt.Sprintf("localhost:%d", p), 50*time.Millisecond)
			if err != nil {
				return
			}
			connected++

			// Send our info as JSON length-prefixed message
			data, _ := json.Marshal(info)
			var length [4]byte
			binary.BigEndian.PutUint32(length[:], uint32(len(data)))

			if _, err := conn.Write(length[:]); err != nil {
				conn.Close()
				return
			}
			if _, err := conn.Write(data); err != nil {
				conn.Close()
				return
			}

			// Read peer's response (length-prefixed)
			var peerLen [4]byte
			conn.SetReadDeadline(time.Now().Add(100 * time.Millisecond))
			if _, err := io.ReadFull(conn, peerLen[:]); err != nil {
				conn.Close()
				return
			}

			peerSize := binary.BigEndian.Uint32(peerLen[:])
			if peerSize > 4096 {
				conn.Close()
				return
			}

			peerData := make([]byte, peerSize)
			if _, err := io.ReadFull(conn, peerData); err != nil {
				conn.Close()
				return
			}
			conn.Close()

			var peerInfo proto.AgentInfo
			if err := json.Unmarshal(peerData, &peerInfo); err != nil {
				return
			}

			if peerInfo.Id != info.Id {
				d.addPeer(&peerInfo)
				found++
				log.Printf("[discovery] [%s] Found peer %s at port %d", info.Name, peerInfo.Name, peerInfo.Port)
			}
		}(port)
	}
	wg.Wait()
	log.Printf("[discovery] [%s] Broadcast complete, connected=%d found=%d", info.Name, connected, found)
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
