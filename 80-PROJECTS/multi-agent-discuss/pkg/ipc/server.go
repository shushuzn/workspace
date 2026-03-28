package ipc

import (
	"bufio"
	"context"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"sync"
	"time"

	"github.com/openclaw/multi-agent-discuss/pkg/core"
	"github.com/openclaw/multi-agent-discuss/pkg/group"
	"github.com/openclaw/multi-agent-discuss/pkg/proto"
)

// Message represents an IPC request/response message
type Message struct {
	Cmd     string `json:"cmd"`
	PeerID  string `json:"peerId,omitempty"`
	Message string `json:"message,omitempty"`
	GroupID string `json:"groupId,omitempty"`
}

// Response represents an IPC response
type Response struct {
	OK   bool            `json:"ok"`
	Data json.RawMessage `json:"data,omitempty"`
	Err  string          `json:"error,omitempty"`
}

// PeerDiscovery is the interface for getting peers
type PeerDiscovery interface {
	GetPeers() []*proto.AgentInfo
}

// Server is the IPC server that listens for CLI commands
type Server struct {
	addr      string
	ln        net.Listener
	agent     *core.Agent
	disc      PeerDiscovery
	grpMgr    *group.GroupManager
	msgHistory []MessageEntry
	mu        sync.RWMutex
	running   bool
	stopCh    chan struct{}
}

// MessageEntry represents a message in history
type MessageEntry struct {
	Timestamp time.Time
	From      string
	To        string
	Content   string
}

// NewServer creates a new IPC server
// agentPort is used to compute IPC port = agentPort + 10000
func NewServer(agentPort int, agent *core.Agent, disc PeerDiscovery, grpMgr *group.GroupManager) *Server {
	return &Server{
		addr:       fmt.Sprintf("localhost:%d", agentPort+10000),
		agent:      agent,
		disc:       disc,
		grpMgr:     grpMgr,
		msgHistory: make([]MessageEntry, 0, 100),
		stopCh:     make(chan struct{}),
	}
}

// Start begins listening for IPC connections
func (s *Server) Start() error {
	ln, err := net.Listen("tcp", s.addr)
	if err != nil {
		return fmt.Errorf("failed to listen on %s: %w", s.addr, err)
	}
	s.ln = ln
	s.mu.Lock()
	s.running = true
	s.mu.Unlock()

	go s.acceptLoop()
	return nil
}

// Stop gracefully shuts down the IPC server
func (s *Server) Stop() error {
	s.mu.Lock()
	s.running = false
	s.mu.Unlock()

	close(s.stopCh)
	if s.ln != nil {
		return s.ln.Close()
	}
	return nil
}

func (s *Server) acceptLoop() {
	for {
		conn, err := s.ln.Accept()
		if err != nil {
			select {
			case <-s.stopCh:
				return
			default:
				continue
			}
		}
		go s.handleConn(conn)
	}
}

func (s *Server) handleConn(conn net.Conn) {
	defer conn.Close()

	reader := bufio.NewReader(conn)
	for {
		// Read length-prefixed JSON (4-byte header, little-endian)
		var length uint32
		if err := binary.Read(reader, binary.LittleEndian, &length); err != nil {
			return
		}

		if length > 65536 { // Sanity limit
			return
		}

		data := make([]byte, length)
		if _, err := io.ReadFull(reader, data); err != nil {
			return
		}

		var msg Message
		if err := json.Unmarshal(data, &msg); err != nil {
			s.sendResponse(conn, &Response{OK: false, Err: "invalid JSON"})
			continue
		}

		resp := s.handleMessage(&msg)
		s.sendResponse(conn, resp)
	}
}

func (s *Server) sendResponse(conn net.Conn, resp *Response) {
	data, err := json.Marshal(resp)
	if err != nil {
		return
	}

	// Length prefix (little-endian)
	if err := binary.Write(conn, binary.LittleEndian, uint32(len(data))); err != nil {
		return
	}
	conn.Write(data)
}

func (s *Server) handleMessage(msg *Message) *Response {
	switch msg.Cmd {
	case "peers":
		return s.handlePeers()
	case "send":
		return s.handleSend(msg)
	case "groups":
		return s.handleGroups()
	case "status":
		return s.handleStatus()
	case "invoke":
		return s.handleInvoke(msg)
	case "orchestrate":
		return s.handleOrchestrate(msg)
	default:
		return &Response{OK: false, Err: fmt.Sprintf("unknown command: %s", msg.Cmd)}
	}
}

func (s *Server) handlePeers() *Response {
	peers := s.disc.GetPeers()

	type PeerInfo struct {
		ID           string   `json:"id"`
		Name         string   `json:"name"`
		Port         int32    `json:"port"`
		Capabilities []string `json:"capabilities"`
	}

	peerList := make([]PeerInfo, 0, len(peers))
	for _, p := range peers {
		caps := make([]string, 0, len(p.Capabilities))
		for _, c := range p.Capabilities {
			caps = append(caps, c.Name)
		}
		peerList = append(peerList, PeerInfo{
			ID:           p.Id,
			Name:         p.Name,
			Port:         p.Port,
			Capabilities: caps,
		})
	}

	data, _ := json.Marshal(peerList)
	return &Response{OK: true, Data: data}
}

func (s *Server) handleSend(msg *Message) *Response {
	if msg.PeerID == "" {
		return &Response{OK: false, Err: "peerId required"}
	}
	if msg.Message == "" {
		return &Response{OK: false, Err: "message required"}
	}

	// Record in history
	s.mu.Lock()
	s.msgHistory = append(s.msgHistory, MessageEntry{
		Timestamp: time.Now(),
		From:      s.agent.ID,
		To:        msg.PeerID,
		Content:   msg.Message,
	})
	if len(s.msgHistory) > 100 {
		s.msgHistory = s.msgHistory[len(s.msgHistory)-100:]
	}
	s.mu.Unlock()

	data, _ := json.Marshal(map[string]string{"sent": "ok", "from": s.agent.ID, "to": msg.PeerID})
	return &Response{OK: true, Data: data}
}

func (s *Server) handleGroups() *Response {
	groups := s.grpMgr.GetGroups()

	type GroupInfo struct {
		ID   string `json:"id"`
		Name string `json:"name"`
	}

	groupList := make([]GroupInfo, 0, len(groups))
	for _, g := range groups {
		groupList = append(groupList, GroupInfo{
			ID:   g.ID,
			Name: g.Name,
		})
	}

	data, _ := json.Marshal(groupList)
	return &Response{OK: true, Data: data}
}

func (s *Server) handleStatus() *Response {
	peers := s.disc.GetPeers()
	groups := s.grpMgr.GetGroups()

	s.mu.RLock()
	historyLen := len(s.msgHistory)
	s.mu.RUnlock()

	status := map[string]interface{}{
		"agentId":          s.agent.ID,
		"agentName":        s.agent.Name,
		"agentPort":        s.agent.Port,
		"peerCount":        len(peers),
		"groupCount":       len(groups),
		"msgHistoryCount":  historyLen,
	}

	data, _ := json.Marshal(status)
	return &Response{OK: true, Data: data}
}

func (s *Server) handleInvoke(msg *Message) *Response {
	if msg.PeerID == "" {
		return &Response{OK: false, Err: "peerId required"}
	}
	if msg.Message == "" {
		return &Response{OK: false, Err: "message required"}
	}

	var payload struct {
		Tool string         `json:"tool"`
		Args map[string]string `json:"args"`
	}
	if err := json.Unmarshal([]byte(msg.Message), &payload); err != nil {
		return &Response{OK: false, Err: fmt.Sprintf("invalid invoke payload: %v", err)}
	}
	if payload.Tool == "" {
		return &Response{OK: false, Err: "tool required"}
	}

	result, err := s.agent.InvokeTool(msg.PeerID, payload.Tool, payload.Args)
	if err != nil {
		return &Response{OK: false, Err: err.Error()}
	}

	data, _ := json.Marshal(result)
	return &Response{OK: true, Data: data}
}

func (s *Server) handleOrchestrate(msg *Message) *Response {
	if msg.Message == "" {
		return &Response{OK: false, Err: "task description required"}
	}

	orch := s.agent.GetOrchestrator()
	if orch == nil {
		return &Response{OK: false, Err: "orchestrator not configured"}
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	result, err := orch.Process(ctx, msg.Message)
	if err != nil {
		return &Response{OK: false, Err: err.Error()}
	}

	data, _ := json.Marshal(map[string]interface{}{
		"result":  result,
		"success": true,
	})
	return &Response{OK: true, Data: data}
}

// Client is an IPC client for sending commands to a running agent
type Client struct {
	addr string
}

// NewClient creates an IPC client for the given agent port
func NewClient(agentPort int) *Client {
	return &Client{
		addr: fmt.Sprintf("localhost:%d", agentPort+10000),
	}
}

// Peers returns the list of peers from the agent
func (c *Client) Peers() ([]map[string]interface{}, error) {
	resp, err := c.send(&Message{Cmd: "peers"})
	if err != nil {
		return nil, err
	}
	if !resp.OK {
		return nil, fmt.Errorf("peers error: %s", resp.Err)
	}

	var peers []map[string]interface{}
	if err := json.Unmarshal(resp.Data, &peers); err != nil {
		return nil, err
	}
	return peers, nil
}

// Send sends a message to a peer
func (c *Client) Send(peerID, message string) error {
	resp, err := c.send(&Message{Cmd: "send", PeerID: peerID, Message: message})
	if err != nil {
		return err
	}
	if !resp.OK {
		return fmt.Errorf("send error: %s", resp.Err)
	}
	return nil
}

// Groups returns the list of groups from the agent
func (c *Client) Groups() ([]map[string]interface{}, error) {
	resp, err := c.send(&Message{Cmd: "groups"})
	if err != nil {
		return nil, err
	}
	if !resp.OK {
		return nil, fmt.Errorf("groups error: %s", resp.Err)
	}

	var groups []map[string]interface{}
	if err := json.Unmarshal(resp.Data, &groups); err != nil {
		return nil, err
	}
	return groups, nil
}

// Status returns the agent status
func (c *Client) Status() (map[string]interface{}, error) {
	resp, err := c.send(&Message{Cmd: "status"})
	if err != nil {
		return nil, err
	}
	if !resp.OK {
		return nil, fmt.Errorf("status error: %s", resp.Err)
	}

	var status map[string]interface{}
	if err := json.Unmarshal(resp.Data, &status); err != nil {
		return nil, err
	}
	return status, nil
}

func (c *Client) send(msg *Message) (*Response, error) {
	conn, err := net.DialTimeout("tcp", c.addr, 5*time.Second)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to IPC server at %s: %w", c.addr, err)
	}
	defer conn.Close()

	data, err := json.Marshal(msg)
	if err != nil {
		return nil, err
	}

	// Send length-prefixed (little-endian)
	if err := binary.Write(conn, binary.LittleEndian, uint32(len(data))); err != nil {
		return nil, err
	}
	if _, err := conn.Write(data); err != nil {
		return nil, err
	}

	// Read response
	reader := bufio.NewReader(conn)
	var length uint32
	if err := binary.Read(reader, binary.LittleEndian, &length); err != nil {
		return nil, err
	}

	if length > 65536 {
		return nil, fmt.Errorf("response too large")
	}

	respData := make([]byte, length)
	if _, err := io.ReadFull(reader, respData); err != nil {
		return nil, err
	}

	var resp Response
	if err := json.Unmarshal(respData, &resp); err != nil {
		return nil, err
	}

	return &resp, nil
}
