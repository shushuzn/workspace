package dispatcher

import (
	"encoding/json"
	"fmt"
	"log"
	"strings"
	"sync"
	"time"

	"github.com/openclaw/multi-agent-discuss/pkg/proto"
)

// State represents the current state of the dispatcher
type State int

const (
	StateIdle State = iota
	StateProcessing
	StateNeedHelp
	StateWaiting
)

func (s State) String() string {
	switch s {
	case StateIdle:
		return "IDLE"
	case StateProcessing:
		return "PROCESSING"
	case StateNeedHelp:
		return "NEED_HELP"
	case StateWaiting:
		return "WAITING"
	default:
		return "UNKNOWN"
	}
}

// DecisionType represents the type of decision made by the dispatcher
type DecisionType int

const (
	DecisionForward DecisionType = iota
	DecisionProcessTask
	DecisionRequestHelp
	DecisionRespond
	DecisionIgnore
	DecisionOrchestrate // New: handle ORCHESTRATE messages
)

func (d DecisionType) String() string {
	switch d {
	case DecisionForward:
		return "FORWARD"
	case DecisionProcessTask:
		return "PROCESS_TASK"
	case DecisionRequestHelp:
		return "REQUEST_HELP"
	case DecisionRespond:
		return "RESPOND"
	case DecisionIgnore:
		return "IGNORE"
	case DecisionOrchestrate:
		return "ORCHESTRATE"
	default:
		return "UNKNOWN"
	}
}

// Decision represents a decision made by the dispatcher about how to handle a message
type Decision struct {
	Type         DecisionType
	Message      *proto.AgentMessage
	Action       interface{}
	ResponseType proto.MessageType // Set when Type is DecisionRespond to specify outgoing message type
}

// Task represents a task to be executed
type Task struct {
	ID        string
	Type      string
	Payload   []byte
	SenderID  string
	CreatedAt time.Time
}

// TaskResult represents the result of a task execution
type TaskResult struct {
	TaskID     string
	Success    bool
	Output     []byte
	Error      string
	ExecutedBy string
}

// TaskExecutor is the interface for executing tasks
type TaskExecutor interface {
	CanExecute(task *Task) bool
	Execute(task *Task) (*TaskResult, error)
}

// Dispatcher is the brain of each agent that decides how to handle messages
type Dispatcher struct {
	agentID    string
	state      State
	peers      func() []*proto.AgentInfo
	executor   TaskExecutor
	onDecision func(decision *Decision)
	replyFn    func(*proto.AgentMessage) // function to send reply to peer

	mu         sync.RWMutex
	activeTask *Task
}

// NewDispatcher creates a new Dispatcher instance
func NewDispatcher(agentID string, peersProvider func() []*proto.AgentInfo) *Dispatcher {
	return &Dispatcher{
		agentID: agentID,
		state:   StateIdle,
		peers:   peersProvider,
	}
}

// HandleMessage processes an incoming message and returns a decision
// replyFn is called to send responses back to the peer (may be nil)
func (d *Dispatcher) HandleMessage(msg *proto.AgentMessage, executor TaskExecutor, replyFn func(*proto.AgentMessage)) {
	d.mu.Lock()
	defer d.mu.Unlock()

	d.executor = executor
	d.replyFn = replyFn

	decision := d.makeDecision(msg)

	// Non-blocking decision callback
	go func() {
		if d.onDecision != nil {
			d.onDecision(decision)
		}
	}()

	// Send reply if decision requires response
	if decision.Type == DecisionRespond && d.replyFn != nil && decision.ResponseType != 0 {
		response := d.buildResponse(decision)
		if response != nil {
			go func() {
				d.replyFn(response)
			}()
		}
	}
}

// makeDecision implements the decision logic based on message type and state
func (d *Dispatcher) makeDecision(msg *proto.AgentMessage) *Decision {
	log.Printf("[dispatcher:%s] makeDecision state=%s msg_type=%s sender=%s",
		d.agentID, d.state.String(), msg.Type.String(), msg.SenderId)

	switch msg.Type {
	case proto.MessageType_TEXT:
		// TEXT messages are acknowledged with a response
		return &Decision{
			Type:    DecisionRespond,
			Message: msg,
			Action:  map[string]interface{}{"ack": true, "text": "acknowledged"},
		}

	case proto.MessageType_TASK:
		return d.handleTaskMessage(msg)

	case proto.MessageType_RESPONSE:
		// RESPONSE messages are routed back to the original requester
		return &Decision{
			Type:    DecisionRespond,
			Message: msg,
			Action:  map[string]interface{}{"response": true},
		}

	case proto.MessageType_INVITE:
		// INVITE messages indicate joining a group discussion
		return &Decision{
			Type:    DecisionProcessTask,
			Message: msg,
			Action:  map[string]interface{}{"join": true},
		}

	case proto.MessageType_FORWARD:
		// FORWARD messages need to be examined for routing
		if msg.ShouldForward && !d.hasVisited(msg) {
			return &Decision{
				Type:    DecisionForward,
				Message: msg,
				Action:  map[string]interface{}{"forward": true},
			}
		}
		return &Decision{
			Type:    DecisionIgnore,
			Message: msg,
			Action:  nil,
		}

	case proto.MessageType_HEARTBEAT:
		// Heartbeats are ignored but responded to keep connection alive
		return &Decision{
			Type:    DecisionRespond,
			Message: msg,
			Action:  map[string]interface{}{"heartbeat": true},
		}

	case proto.MessageType_INVOKE_TOOL:
		return d.handleInvokeTool(msg)

	case proto.MessageType_ORCHESTRATE:
		return d.handleOrchestrateMessage(msg)

	default:
		return &Decision{
			Type:    DecisionIgnore,
			Message: msg,
			Action:  nil,
		}
	}
}

// handleTaskMessage handles TASK type messages with specific routing logic
func (d *Dispatcher) handleTaskMessage(msg *proto.AgentMessage) *Decision {
	// Check if message was already visited by this agent
	if d.hasVisited(msg) {
		log.Printf("[dispatcher:%s] message already visited, ignoring", d.agentID)
		return &Decision{
			Type:    DecisionIgnore,
			Message: msg,
			Action:  nil,
		}
	}

	// Check if ShouldForward is set and we haven't reached max hops
	if msg.ShouldForward && msg.HopCount < msg.MaxHops {
		return &Decision{
			Type:    DecisionForward,
			Message: msg,
			Action:  map[string]interface{}{"forward": true},
		}
	}

	// Create task from message
	task := &Task{
		ID:        msg.Id,
		Type:      string(msg.Payload),
		Payload:   msg.Payload,
		SenderID:  msg.SenderId,
		CreatedAt: time.Now(),
	}

	// Check if executor can handle the task
	if d.executor != nil && d.executor.CanExecute(task) {
		d.activeTask = task
		return &Decision{
			Type:    DecisionProcessTask,
			Message: msg,
			Action:  task,
		}
	}

	// If we're already processing and can't handle more, request help
	if d.state == StateProcessing {
		return &Decision{
			Type:    DecisionRequestHelp,
			Message: msg,
			Action:  map[string]interface{}{"request_help": true},
		}
	}

	// Check if we have the capability to handle this task
	if d.canHandleTask(task) {
		d.activeTask = task
		return &Decision{
			Type:    DecisionProcessTask,
			Message: msg,
			Action:  task,
		}
	}

	// We cannot handle this task, request help from peers
	return &Decision{
		Type:    DecisionRequestHelp,
		Message: msg,
		Action:  map[string]interface{}{"request_help": true},
	}
}

// hasVisited checks if this agent has already processed the message
func (d *Dispatcher) hasVisited(msg *proto.AgentMessage) bool {
	for _, visitedID := range msg.Visited {
		if visitedID == d.agentID {
			return true
		}
	}
	return false
}

// canHandleTask checks if this agent has the capability to handle the task
func (d *Dispatcher) canHandleTask(task *Task) bool {
	// Default implementation: agents can handle basic text tasks
	// This can be extended with capability matching
	return true
}

func (d *Dispatcher) handleInvokeTool(msg *proto.AgentMessage) *Decision {
	// Parse JSON payload (transport uses json.Marshal, not proto)
	var payload struct {
		InvokeID string            `json:"invoke_id"`
		Tool    string            `json:"tool"`
		Args    map[string]string `json:"args"`
	}
	if err := json.Unmarshal(msg.Payload, &payload); err != nil {
		return &Decision{
			Type:    DecisionRespond,
			Message: msg,
			Action:  map[string]interface{}{"error": fmt.Sprintf("failed to parse payload: %v", err)},
		}
	}

	return d.executeToolInvoke(msg, payload.InvokeID, payload.Tool, payload.Args)
}

func (d *Dispatcher) executeToolInvoke(msg *proto.AgentMessage, invokeID, toolName string, args map[string]string) *Decision {
	if d.executor == nil {
		return &Decision{
			Type:    DecisionRespond,
			Message: msg,
			Action: map[string]interface{}{
				"invoke_id": invokeID,
				"success":   false,
				"error":     "no executor configured",
			},
		}
	}

	// Strip "tool:" prefix if present
	name := toolName
	if strings.HasPrefix(name, "tool:") {
		name = strings.TrimPrefix(name, "tool:")
	}

	tool, found := d.executor.FindTool(name)
	if !found {
		return &Decision{
			Type:    DecisionRespond,
			Message: msg,
			Action: map[string]interface{}{
				"invoke_id": invokeID,
				"success":   false,
				"error":     fmt.Sprintf("tool not found: %s", name),
			},
		}
	}

	timeout := 30 * time.Second
	if tool.Timeout > 0 {
		timeout = tool.Timeout
	}

	// Convert args to interface{}
	ifaceArgs := make(map[string]interface{})
	for k, v := range args {
		ifaceArgs[k] = v
	}

	// Execute with timeout and panic recovery
	resultCh := make(chan interface{}, 1)
	errorCh := make(chan error, 1)

	go func() {
		defer func() {
			if r := recover(); r != nil {
				errorCh <- fmt.Errorf("panic: %v", r)
			}
		}()
		result, err := tool.Execute(ifaceArgs)
		if err != nil {
			errorCh <- err
			return
		}
		resultCh <- result
	}()

	select {
	case result := <-resultCh:
		resultJSON, _ := json.Marshal(result)
		return &Decision{
			Type:         DecisionRespond,
			Message:      msg,
			Action: map[string]interface{}{
				"invoke_id": invokeID,
				"success":   true,
				"result":    string(resultJSON),
			},
			ResponseType: proto.MessageType_TOOL_RESULT,
		}
	case err := <-errorCh:
		return &Decision{
			Type:         DecisionRespond,
			Message:      msg,
			Action: map[string]interface{}{
				"invoke_id": invokeID,
				"success":   false,
				"error":     err.Error(),
			},
			ResponseType: proto.MessageType_TOOL_RESULT,
		}
	case <-time.After(timeout):
		return &Decision{
			Type:         DecisionRespond,
			Message:      msg,
			Action: map[string]interface{}{
				"invoke_id": invokeID,
				"success":   false,
				"error":     fmt.Sprintf("tool execution timeout after %v", timeout),
			},
			ResponseType: proto.MessageType_TOOL_RESULT,
		}
	}
}

// buildResponse constructs an AgentMessage from a Decision
func (d *Dispatcher) buildResponse(decision *Decision) *proto.AgentMessage {
	action, ok := decision.Action.(map[string]interface{})
	if !ok {
		return nil
	}

	payloadJSON, err := json.Marshal(action)
	if err != nil {
		log.Printf("[dispatcher:%s] failed to marshal response action: %v", d.agentID, err)
		return nil
	}

	return &proto.AgentMessage{
		Id:        fmt.Sprintf("reply-%d", time.Now().UnixNano()),
		Timestamp: time.Now().Unix(),
		SenderId:  d.agentID,
		Type:      decision.ResponseType,
		Payload:   payloadJSON,
	}
}

// SetDecisionCallback sets the callback function to be called when a decision is made
func (d *Dispatcher) SetDecisionCallback(callback func(*Decision)) {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.onDecision = callback
}

// GetState returns the current state of the dispatcher
func (d *Dispatcher) GetState() State {
	d.mu.RLock()
	defer d.mu.RUnlock()
	return d.state
}

// SetState sets the current state of the dispatcher
func (d *Dispatcher) SetState(state State) {
	d.mu.Lock()
	defer d.mu.Unlock()
	log.Printf("[dispatcher:%s] state transition: %s -> %s", d.agentID, d.state.String(), state.String())
	d.state = state
}

// GetActiveTask returns the currently active task if any
func (d *Dispatcher) GetActiveTask() *Task {
	d.mu.RLock()
	defer d.mu.RUnlock()
	return d.activeTask
}

// ClearActiveTask clears the currently active task
func (d *Dispatcher) ClearActiveTask() {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.activeTask = nil
}

// TransitionState performs a state transition with logging
func (d *Dispatcher) TransitionState(newState State) {
	d.SetState(newState)
}

// handleOrchestrateMessage handles ORCHESTRATE message type
func (d *Dispatcher) handleOrchestrateMessage(msg *proto.AgentMessage) *Decision {
	// Parse task from payload
	var payload struct {
		Task string `json:"task"`
	}
	if err := json.Unmarshal(msg.Payload, &payload); err != nil {
		return &Decision{
			Type:    DecisionRespond,
			Message: msg,
			Action:  map[string]interface{}{"error": fmt.Sprintf("failed to parse payload: %v", err)},
		}
	}

	// Orchestrator is typically used via IPC, not P2P dispatcher
	// Return an error indicating this path is not supported
	return &Decision{
		Type:    DecisionRespond,
		Message: msg,
		Action:  map[string]interface{}{"error": "orchestrator not available via P2P, use IPC command instead"},
	}
}
