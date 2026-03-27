package toolclient

import (
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/openclaw/multi-agent-discuss/pkg/proto"
	"github.com/openclaw/multi-agent-discuss/pkg/transport"
)

const defaultToolTimeout = 35 * time.Second // slightly longer than tool's 30s

// ToolClient manages remote tool invocations and correlates responses
type ToolClient struct {
	client  *transport.Client
	pending map[string]chan *proto.AgentMessage
	mu      sync.RWMutex
	agentID string
}

// NewToolClient creates a new ToolClient
func NewToolClient(client *transport.Client, agentID string) *ToolClient {
	tc := &ToolClient{
		client:  client,
		pending: make(map[string]chan *proto.AgentMessage),
		agentID: agentID,
	}
	// Start listening for responses in background
	go tc.recvLoop()
	return tc
}

// InvokeTool sends a tool invocation to a peer and waits for the result
func (tc *ToolClient) InvokeTool(tool string, args map[string]string) (map[string]interface{}, error) {
	invokeID := uuid.New().String()

	// Create response channel
	ch := make(chan *proto.AgentMessage, 1)
	tc.mu.Lock()
	tc.pending[invokeID] = ch
	tc.mu.Unlock()

	// Build payload
	payload := map[string]interface{}{
		"invoke_id": invokeID,
		"tool":      tool,
		"args":      args,
	}
	payloadBytes, _ := json.Marshal(payload)

	// Send message
	msg := &proto.AgentMessage{
		Id:        invokeID,
		Type:      proto.MessageType_INVOKE_TOOL,
		SenderId:  tc.agentID,
		Timestamp: time.Now().UnixNano(),
		Payload:   payloadBytes,
	}

	if err := tc.client.Send(msg); err != nil {
		tc.mu.Lock()
		delete(tc.pending, invokeID)
		tc.mu.Unlock()
		return nil, fmt.Errorf("failed to send: %w", err)
	}

	// Wait for result with timeout
	select {
	case resp := <-ch:
		tc.mu.Lock()
		delete(tc.pending, invokeID)
		tc.mu.Unlock()
		return tc.parseResult(resp)
	case <-time.After(defaultToolTimeout):
		tc.mu.Lock()
		delete(tc.pending, invokeID)
		tc.mu.Unlock()
		return nil, fmt.Errorf("tool invocation timeout after %v", defaultToolTimeout)
	}
}

func (tc *ToolClient) recvLoop() {
	for {
		msg, err := tc.client.Recv()
		if err != nil {
			return
		}
		tc.deliver(msg)
	}
}

func (tc *ToolClient) deliver(msg *proto.AgentMessage) {
	// Parse the invoke_id from payload
	var payload struct {
		InvokeID string `json:"invoke_id"`
	}
	if err := json.Unmarshal(msg.Payload, &payload); err != nil {
		return
	}

	tc.mu.RLock()
	ch, ok := tc.pending[payload.InvokeID]
	tc.mu.RUnlock()

	if ok {
		select {
		case ch <- msg:
		default:
		}
	}
}

func (tc *ToolClient) parseResult(msg *proto.AgentMessage) (map[string]interface{}, error) {
	var result struct {
		InvokeID string `json:"invoke_id"`
		Success  bool   `json:"success"`
		Result   string `json:"result"`
		Error    string `json:"error"`
	}
	if err := json.Unmarshal(msg.Payload, &result); err != nil {
		return nil, fmt.Errorf("failed to parse result: %w", err)
	}

	if !result.Success {
		return nil, fmt.Errorf("tool error: %s", result.Error)
	}

	if result.Result == "" {
		return nil, nil
	}

	var parsed map[string]interface{}
	if err := json.Unmarshal([]byte(result.Result), &parsed); err != nil {
		return nil, nil
	}
	return parsed, nil
}
