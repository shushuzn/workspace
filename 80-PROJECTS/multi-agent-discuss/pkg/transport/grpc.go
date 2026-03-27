package transport

import (
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"sync"
	"time"

	"github.com/openclaw/multi-agent-discuss/pkg/proto"
)

// MessageHandler handles incoming messages from a peer connection.
type MessageHandler interface {
	HandleMessage(msg *proto.AgentMessage, reply func(*proto.AgentMessage))
}

// Server represents a TCP server that handles agent connections.
type Server struct {
	ln      net.Listener
	handler MessageHandler
	mu      sync.RWMutex
	closed  bool
}

// Addr returns the address the server is listening on.
func (s *Server) Addr() string {
	s.mu.RLock()
	defer s.mu.RUnlock()
	if s.ln == nil {
		return ""
	}
	return s.ln.Addr().String()
}

// Close stops the server and closes the listener.
func (s *Server) Close() error {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.closed = true
	if s.ln == nil {
		return nil
	}
	return s.ln.Close()
}

// Client represents a connection to a remote agent.
type Client struct {
	conn    net.Conn
	sendCh  chan *proto.AgentMessage
	recvCh  chan *proto.AgentMessage
	errCh   chan error
	closeCh chan struct{}
	wg      sync.WaitGroup
	mu      sync.Mutex
	closed  bool
}

// Send sends a message to the remote agent.
func (c *Client) Send(msg *proto.AgentMessage) error {
	c.mu.Lock()
	if c.closed {
		c.mu.Unlock()
		return fmt.Errorf("connection closed")
	}
	c.mu.Unlock()

	select {
	case c.sendCh <- msg:
		return nil
	case <-c.closeCh:
		return fmt.Errorf("connection closed")
	}
}

// Recv receives a message from the remote agent.
func (c *Client) Recv() (*proto.AgentMessage, error) {
	select {
	case msg, ok := <-c.recvCh:
		if !ok {
			return nil, fmt.Errorf("connection closed")
		}
		return msg, nil
	case err, ok := <-c.errCh:
		if !ok {
			return nil, fmt.Errorf("connection closed")
		}
		return nil, err
	case <-c.closeCh:
		return nil, fmt.Errorf("connection closed")
	}
}

// Close closes the client connection.
func (c *Client) Close() error {
	c.mu.Lock()
	if c.closed {
		c.mu.Unlock()
		return nil
	}
	c.closed = true
	c.mu.Unlock()

	close(c.closeCh)
	c.wg.Wait()
	return c.conn.Close()
}

// StartServer starts a TCP server on the given port and dispatches
// incoming messages to the handler.
func StartServer(port int, handler MessageHandler) (*Server, error) {
	ln, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		return nil, fmt.Errorf("listen: %w", err)
	}

	s := &Server{
		ln:      ln,
		handler: handler,
	}

	go s.acceptLoop()
	return s, nil
}

func (s *Server) acceptLoop() {
	for {
		conn, err := s.ln.Accept()
		if err != nil {
			s.mu.RLock()
			closed := s.closed
			s.mu.RUnlock()
			if closed {
				return
			}
			continue
		}
		go s.handleConn(conn)
	}
}

func (s *Server) handleConn(conn net.Conn) {
	defer conn.Close()

	// Read initial AgentInfo from client
	info, err := readAgentInfo(conn)
	if err != nil {
		return
	}

	client := &Client{
		conn:    conn,
		sendCh:  make(chan *proto.AgentMessage, 100),
		recvCh:  make(chan *proto.AgentMessage, 100),
		errCh:   make(chan error, 1),
		closeCh: make(chan struct{}),
	}

	// Start goroutine to send messages
	client.wg.Add(1)
	go func() {
		defer client.wg.Done()
		for msg := range client.sendCh {
			if err := writeMessage(conn, msg); err != nil {
				select {
				case client.errCh <- err:
				default:
				}
				return
			}
		}
	}()

	// Start goroutine to receive messages
	client.wg.Add(1)
	go func() {
		defer client.wg.Done()
		defer close(client.recvCh)
		for {
			msg, err := readMessage(conn)
			if err != nil {
				if err != io.EOF {
					select {
					case client.errCh <- err:
					default:
					}
				}
				return
			}
			select {
			case client.recvCh <- msg:
			case <-client.closeCh:
				return
			}
		}
	}()

	// Handle messages using the handler
	s.handleMessages(client, info)
}

func (s *Server) handleMessages(client *Client, peerInfo *proto.AgentInfo) {
	for {
		select {
		case msg, ok := <-client.recvCh:
			if !ok {
				return
			}
			// Create a reply function that sends back to this client
			reply := func(response *proto.AgentMessage) {
				client.Send(response)
			}
			s.handler.HandleMessage(msg, reply)

		case <-client.closeCh:
			return
		}
	}
}

// DialAgent connects to a remote agent at the given address and
// exchanges initial AgentInfo to establish the connection.
func DialAgent(addr string, info *proto.AgentInfo) (*Client, error) {
	conn, err := net.DialTimeout("tcp", addr, 10*time.Second)
	if err != nil {
		return nil, fmt.Errorf("dial: %w", err)
	}

	// Send our AgentInfo first
	if err := writeAgentInfo(conn, info); err != nil {
		conn.Close()
		return nil, fmt.Errorf("send info: %w", err)
	}

	// Read peer's AgentInfo
	peerInfo, err := readAgentInfo(conn)
	if err != nil {
		conn.Close()
		return nil, fmt.Errorf("read peer info: %w", err)
	}
	_ = peerInfo // peer info received, connection established

	client := &Client{
		conn:    conn,
		sendCh:  make(chan *proto.AgentMessage, 100),
		recvCh:  make(chan *proto.AgentMessage, 100),
		errCh:   make(chan error, 1),
		closeCh: make(chan struct{}),
	}

	// Start goroutine to send messages
	client.wg.Add(1)
	go func() {
		defer client.wg.Done()
		for msg := range client.sendCh {
			if err := writeMessage(conn, msg); err != nil {
				select {
				case client.errCh <- err:
				default:
				}
				return
			}
		}
	}()

	// Start goroutine to receive messages
	client.wg.Add(1)
	go func() {
		defer client.wg.Done()
		defer close(client.recvCh)
		for {
			msg, err := readMessage(conn)
			if err != nil {
				if err != io.EOF {
					select {
					case client.errCh <- err:
					default:
					}
				}
				return
			}
			select {
			case client.recvCh <- msg:
			case <-client.closeCh:
				return
			}
		}
	}()

	return client, nil
}

// Length-prefixed framing: [4 bytes big-endian length][JSON payload]

func writeMessage(conn net.Conn, msg *proto.AgentMessage) error {
	data, err := json.Marshal(msg)
	if err != nil {
		return fmt.Errorf("marshal: %w", err)
	}

	// Write length prefix
	var length [4]byte
	binary.BigEndian.PutUint32(length[:], uint32(len(data)))
	if _, err := conn.Write(length[:]); err != nil {
		return fmt.Errorf("write length: %w", err)
	}

	// Write payload
	if _, err := conn.Write(data); err != nil {
		return fmt.Errorf("write data: %w", err)
	}

	return nil
}

func readMessage(conn net.Conn) (*proto.AgentMessage, error) {
	// Read length prefix
	var length [4]byte
	if _, err := io.ReadFull(conn, length[:]); err != nil {
		return nil, fmt.Errorf("read length: %w", err)
	}

	size := binary.BigEndian.Uint32(length[:])
	if size > 1024*1024*10 { // 10MB limit
		return nil, fmt.Errorf("message too large: %d", size)
	}

	// Read payload
	data := make([]byte, size)
	if _, err := io.ReadFull(conn, data); err != nil {
		return nil, fmt.Errorf("read data: %w", err)
	}

	var msg proto.AgentMessage
	if err := json.Unmarshal(data, &msg); err != nil {
		return nil, fmt.Errorf("unmarshal: %w", err)
	}

	return &msg, nil
}

func writeAgentInfo(conn net.Conn, info *proto.AgentInfo) error {
	data, err := json.Marshal(info)
	if err != nil {
		return fmt.Errorf("marshal: %w", err)
	}

	var length [4]byte
	binary.BigEndian.PutUint32(length[:], uint32(len(data)))
	if _, err := conn.Write(length[:]); err != nil {
		return fmt.Errorf("write length: %w", err)
	}

	if _, err := conn.Write(data); err != nil {
		return fmt.Errorf("write data: %w", err)
	}

	return nil
}

func readAgentInfo(conn net.Conn) (*proto.AgentInfo, error) {
	var length [4]byte
	if _, err := io.ReadFull(conn, length[:]); err != nil {
		return nil, fmt.Errorf("read length: %w", err)
	}

	size := binary.BigEndian.Uint32(length[:])
	if size > 1024*1024 { // 1MB limit
		return nil, fmt.Errorf("info too large: %d", size)
	}

	data := make([]byte, size)
	if _, err := io.ReadFull(conn, data); err != nil {
		return nil, fmt.Errorf("read data: %w", err)
	}

	var info proto.AgentInfo
	if err := json.Unmarshal(data, &info); err != nil {
		return nil, fmt.Errorf("unmarshal: %w", err)
	}

	return &info, nil
}
