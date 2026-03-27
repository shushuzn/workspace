package executor

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"time"
)

const defaultTimeout = 30 * time.Second

// Task types
const (
	TaskTypeRead  = "READ"
	TaskTypeWrite = "WRITE"
	TaskTypeTool  = "TOOL"
	TaskTypeCode  = "CODE"
)

// Task represents a task to be executed
type Task struct {
	ID      string
	Type    string
	Payload []byte
	Context *TaskContext
}

// TaskContext provides additional context for task execution
type TaskContext struct {
	WorkingDir string
	Env        map[string]string
	Timeout    time.Duration
}

// TaskResult represents the result of a task execution
type TaskResult struct {
	TaskID     string
	Success    bool
	Output     []byte
	Error      string
	ExecutedBy string
	Duration   time.Duration
}

// Tool represents an executable tool/function
type Tool struct {
	Name        string
	Description string
	Params      []string
	Execute     func(params map[string]interface{}) (interface{}, error)
}

// Executor executes tasks for an agent
type Executor struct {
	agentID string
	tools   map[string]Tool
	mu      sync.RWMutex
}

// NewExecutor creates a new Executor for the given agent ID
func NewExecutor(agentID string) *Executor {
	return &Executor{
		agentID: agentID,
		tools:   make(map[string]Tool),
	}
}

// RegisterTool registers a tool with the executor
func (e *Executor) RegisterTool(tool Tool) {
	e.mu.Lock()
	defer e.mu.Unlock()
	e.tools[tool.Name] = tool
}

// ListTools returns a list of all registered tools
func (e *Executor) ListTools() []*Tool {
	e.mu.RLock()
	defer e.mu.RUnlock()

	tools := make([]*Tool, 0, len(e.tools))
	for _, tool := range e.tools {
		t := tool
		tools = append(tools, &t)
	}
	return tools
}

// CanHandle returns true if the executor can handle the given task type
func (e *Executor) CanHandle(taskType string) bool {
	switch taskType {
	case TaskTypeRead, TaskTypeWrite, TaskTypeTool, TaskTypeCode:
		return true
	default:
		return false
	}
}

// ExecuteTask executes a task and returns the result
func (e *Executor) ExecuteTask(task *Task) (*TaskResult, error) {
	start := time.Now()

	if task == nil {
		return &TaskResult{
			Success:    false,
			Error:      "task is nil",
			ExecutedBy: e.agentID,
			Duration:   time.Since(start),
		}, fmt.Errorf("task is nil")
	}

	timeout := defaultTimeout
	if task.Context != nil && task.Context.Timeout > 0 {
		timeout = task.Context.Timeout
	}

	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	resultCh := make(chan *TaskResult, 1)

	go func() {
		result := e.executeTask(task)
		result.ExecutedBy = e.agentID
		result.Duration = time.Since(start)
		resultCh <- result
	}()

	select {
	case <-ctx.Done():
		return &TaskResult{
			TaskID:     task.ID,
			Success:    false,
			Error:      fmt.Sprintf("task execution timed out after %v", timeout),
			ExecutedBy: e.agentID,
			Duration:   time.Since(start),
		}, ctx.Err()
	case result := <-resultCh:
		return result, nil
	}
}

func (e *Executor) executeTask(task *Task) *TaskResult {
	switch task.Type {
	case TaskTypeRead:
		return e.handleRead(task)
	case TaskTypeWrite:
		return e.handleWrite(task)
	case TaskTypeTool:
		return e.handleTool(task)
	case TaskTypeCode:
		return e.handleCode(task)
	default:
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("unknown task type: %s", task.Type),
		}
	}
}

// handleRead handles READ tasks
func (e *Executor) handleRead(task *Task) *TaskResult {
	var payload struct {
		Path string `json:"path"`
		URL  string `json:"url"`
	}

	if err := json.Unmarshal(task.Payload, &payload); err != nil {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("failed to parse READ payload: %v", err),
		}
	}

	var content []byte
	var err error

	if payload.URL != "" {
		content, err = e.readFromURL(payload.URL)
	} else if payload.Path != "" {
		content, err = e.readFromFile(payload.Path, task.Context)
	} else {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   "READ task requires either 'path' or 'url' field",
		}
	}

	if err != nil {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   err.Error(),
		}
	}

	return &TaskResult{
		TaskID:  task.ID,
		Success: true,
		Output:  content,
	}
}

func (e *Executor) readFromURL(url string) ([]byte, error) {
	resp, err := http.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch URL: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP request failed with status: %d", resp.StatusCode)
	}

	content := make([]byte, 0, 1024)
	buf := make([]byte, 4096)
	for {
		n, readErr := resp.Body.Read(buf)
		if n > 0 {
			content = append(content, buf[:n]...)
		}
		if readErr != nil {
			break
		}
	}

	return content, nil
}

func (e *Executor) readFromFile(path string, ctx *TaskContext) ([]byte, error) {
	workingDir := ""
	if ctx != nil {
		workingDir = ctx.WorkingDir
	}

	if !filepath.IsAbs(path) && workingDir != "" {
		path = filepath.Join(workingDir, path)
	}

	content, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("failed to read file: %w", err)
	}

	return content, nil
}

// handleWrite handles WRITE tasks
func (e *Executor) handleWrite(task *Task) *TaskResult {
	var payload struct {
		Path    string `json:"path"`
		Content string `json:"content"`
	}

	if err := json.Unmarshal(task.Payload, &payload); err != nil {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("failed to parse WRITE payload: %v", err),
		}
	}

	if payload.Path == "" {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   "WRITE task requires 'path' field",
		}
	}

	workingDir := ""
	if task.Context != nil {
		workingDir = task.Context.WorkingDir
	}

	filePath := payload.Path
	if !filepath.IsAbs(filePath) && workingDir != "" {
		filePath = filepath.Join(workingDir, filePath)
	}

	if err := os.WriteFile(filePath, []byte(payload.Content), 0644); err != nil {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("failed to write file: %v", err),
		}
	}

	return &TaskResult{
		TaskID:  task.ID,
		Success: true,
		Output:  []byte(fmt.Sprintf("Successfully wrote to %s", filePath)),
	}
}

// handleTool handles TOOL tasks
func (e *Executor) handleTool(task *Task) *TaskResult {
	var payload struct {
		Name   string                 `json:"name"`
		Params map[string]interface{} `json:"params"`
	}

	if err := json.Unmarshal(task.Payload, &payload); err != nil {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("failed to parse TOOL payload: %v", err),
		}
	}

	if payload.Name == "" {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   "TOOL task requires 'name' field",
		}
	}

	e.mu.RLock()
	tool, exists := e.tools[payload.Name]
	e.mu.RUnlock()

	if !exists {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("tool not found: %s", payload.Name),
		}
	}

	result, err := tool.Execute(payload.Params)
	if err != nil {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("tool execution failed: %v", err),
		}
	}

	output, err := json.Marshal(result)
	if err != nil {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("failed to marshal tool result: %v", err),
		}
	}

	return &TaskResult{
		TaskID:  task.ID,
		Success: true,
		Output:  output,
	}
}

// handleCode handles CODE tasks
func (e *Executor) handleCode(task *Task) *TaskResult {
	var payload struct {
		Language string `json:"language"`
		Code     string `json:"code"`
	}

	if err := json.Unmarshal(task.Payload, &payload); err != nil {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("failed to parse CODE payload: %v", err),
		}
	}

	if payload.Language == "" || payload.Code == "" {
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   "CODE task requires both 'language' and 'code' fields",
		}
	}

	// Only support safe, simple output for CODE tasks
	// Arbitrary code execution is not allowed for security
	language := strings.ToLower(payload.Language)
	switch language {
	case "text", "plaintext", "plain":
		return &TaskResult{
			TaskID:  task.ID,
			Success: true,
			Output:  []byte(payload.Code),
		}
	case "json":
		// Validate JSON
		if !json.Valid([]byte(payload.Code)) {
			return &TaskResult{
				TaskID:  task.ID,
				Success: false,
				Error:   "invalid JSON code",
			}
		}
		return &TaskResult{
			TaskID:  task.ID,
			Success: true,
			Output:  []byte(payload.Code),
		}
	default:
		return &TaskResult{
			TaskID:  task.ID,
			Success: false,
			Error:   fmt.Sprintf("unsupported code language: %s (only 'text', 'json' are supported for security)", payload.Language),
		}
	}
}
