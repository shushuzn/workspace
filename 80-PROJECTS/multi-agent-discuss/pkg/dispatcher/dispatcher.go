package dispatcher

import (
	"log"
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
	default:
		return "UNKNOWN"
	}
}

// Decision represents a decision made by the dispatcher about how to handle a message
type Decision struct {
	Type    DecisionType
	Message *proto.AgentMessage
	Action  interface{}
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
func (d *Dispatcher) HandleMessage(msg *proto.AgentMessage, executor TaskExecutor) {
	d.mu.Lock()
	defer d.mu.Unlock()

	d.executor = executor

	decision := d.makeDecision(msg)

	// Non-blocking decision callback
	go func() {
		if d.onDecision != nil {
			d.onDecision(decision)
		}
	}()
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
