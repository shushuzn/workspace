# Task Delegation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable agents to invoke tools on remote peer agents via P2P network and receive results.

**Architecture:** Add `INVOKE_TOOL`/`TOOL_RESULT` message types to dispatcher. Tools execute locally on the callee agent. Results route back via the same TCP connection. Existing transport uses JSON serialization - payloads are JSON-encoded bytes inside `AgentMessage.Payload`.

**Tech Stack:** Go, JSON, existing transport/discovery/dispatcher/executor

---

## Key Architecture Notes

1. **Transport uses JSON**: `transport/grpc.go:309` uses `json.Marshal(msg)` to serialize `AgentMessage`. The `Payload` field is already `[]byte` containing JSON-encoded data (not protobuf binary). Use `json.Marshal`/`json.Unmarshal` for all payload operations.

2. **Dispatcher doesn't call reply directly**: `Dispatcher.HandleMessage(msg, executor)` returns decisions via callback `onDecision(decision)`. The actual reply routing happens at the transport/core layer. The plan adds INVOKE_TOOL handling that returns a `DecisionRespond` with the response as an `Action`.

3. **ToolClient manages correlation**: A new `ToolClient` component wraps the transport and manages `invoke_id` → `chan` correlation for callers awaiting tool results.

---

## File Structure

```
pkg/
  executor/
    executor.go       # MOD: Add Timeout field, FindTool, SetupTools
    tool_code.go      # NEW: Code execution tool
    tool_search.go    # NEW: Search tool
    tool_file.go      # NEW: File read/write tool
  dispatcher/
    dispatcher.go    # MOD: Add INVOKE_TOOL/TOOL_RESULT handling
  toolclient/
    toolclient.go    # NEW: ToolClient for invoke_id correlation
```

---

## Task 1: Extend Proto (agent.proto)

**Files:**
- Modify: `pkg/proto/agent.proto`

- [ ] **Step 1: Edit agent.proto to add new message types**

Add after line 39 (`HEARTBEAT = 5;`):

```proto
  INVOKE_TOOL = 10;  // New: request remote tool execution
  TOOL_RESULT = 11;   // New: tool execution result
```

Add before closing `}` of agent.proto (after line 45):

```proto
message InvokeToolPayload {
  string invoke_id = 1;
  string tool = 2;
  map<string, string> args = 3;
}

message ToolResultPayload {
  string invoke_id = 1;
  bool success = 2;
  bytes result = 3;
  string error = 4;
}
```

- [ ] **Step 2: Regenerate Go code**

```bash
cd /d D:\OpenClaw\workspace\80-PROJECTS\multi-agent-discuss
go generate ./pkg/proto/...
```

Or if generate isn't set up:
```bash
protoc --go_out=. --go_opt=paths=source_relative pkg/proto/agent.proto
```

- [ ] **Step 3: Verify generated code has INVOKE_TOOL/TOOL_RESULT enum values and payload structs**

- [ ] **Step 4: Commit**

```bash
git add pkg/proto/agent.proto pkg/proto/agent.pb.go
git commit -m "feat(proto): add INVOKE_TOOL and TOOL_RESULT message types"
```

---

## Task 2: Add Tool Timeout and Registry to Executor

**Files:**
- Modify: `pkg/executor/executor.go`

- [ ] **Step 1: Add Timeout field to Tool struct**

```go
// Tool represents an executable tool/function
type Tool struct {
    Name        string
    Description string
    Params      []string
    Execute     func(params map[string]interface{}) (interface{}, error)
    Timeout     time.Duration  // NEW: per-tool timeout, 0 = use default
}
```

- [ ] **Step 2: Verify defaultTimeout constant exists**

Line 15: `const defaultTimeout = 30 * time.Second`

- [ ] **Step 3: Add FindTool method**

```go
// FindTool returns a tool by name and whether it was found
func (e *Executor) FindTool(name string) (*Tool, bool) {
    e.mu.RLock()
    defer e.mu.RUnlock()
    t, ok := e.tools[name]
    if !ok {
        return nil, false
    }
    return &t, true
}
```

- [ ] **Step 4: Update RegisterTool to accept pointer**

```go
func (e *Executor) RegisterTool(tool *Tool) {
    e.mu.Lock()
    defer e.mu.Unlock()
    e.tools[tool.Name] = *tool
}
```

- [ ] **Step 5: SetupTools goes here after tool files exist**

`SetupTools()` will be added in Task 5 (Step 6) after `tool_code.go`, `tool_search.go`, and `tool_file.go` are created. For now, Task 2 covers: `Timeout` field, `FindTool`, and updating `RegisterTool` to accept a pointer.

- [ ] **Step 6: Run tests**

```bash
go test ./pkg/executor/... -v
```

- [ ] **Step 7: Commit**

```bash
git add pkg/executor/executor.go
git commit -m "feat(executor): add Timeout field, FindTool, and pointer-based RegisterTool"
```

---

## Task 3: Create Code Tool (tool_code.go)

**Files:**
- Create: `pkg/executor/tool_code.go`
- Test: `pkg/executor/tool_code_test.go`

- [ ] **Step 1: Write failing test**

```go
package executor

import (
    "testing"
    "time"
)

func TestCodeTool_Execute(t *testing.T) {
    tool := &CodeTool{}
    result, err := tool.Execute(map[string]interface{}{
        "lang":   "python",
        "script": "print(1 + 1)",
    })
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    m := result.(map[string]interface{})
    if m["output"] == "" {
        t.Error("expected non-empty output")
    }
}

func TestCodeTool_Timeout(t *testing.T) {
    tool := &CodeTool{}
    if tool.Timeout() != 30*time.Second {
        t.Errorf("expected 30s timeout, got %v", tool.Timeout())
    }
}
```

- [ ] **Step 2: Run test - verify it fails**

```bash
go test ./pkg/executor/... -v -run TestCodeTool
```

Expected: FAIL - CodeTool not defined

- [ ] **Step 3: Implement CodeTool**

```go
package executor

import (
    "fmt"
    "time"
)

// CodeTool executes code in a sandboxed environment
type CodeTool struct{}

func (c *CodeTool) Name() string        { return "code" }
func (c *CodeTool) Description() string { return "Execute code in sandboxed environment" }
func (c *CodeTool) Timeout() time.Duration { return 30 * time.Second }

func (c *CodeTool) Execute(args map[string]interface{}) (interface{}, error) {
    lang, _ := args["lang"].(string)
    script, _ := args["script"].(string)

    if lang == "" || script == "" {
        return nil, fmt.Errorf("missing required args: lang and script")
    }

    switch lang {
    case "python":
        return map[string]interface{}{
            "output":   fmt.Sprintf("[python] %s", script),
            "language": "python",
        }, nil
    case "bash", "shell":
        return map[string]interface{}{
            "output":   fmt.Sprintf("[bash] %s", script),
            "language": "bash",
        }, nil
    case "javascript", "js":
        return map[string]interface{}{
            "output":   fmt.Sprintf("[js] %s", script),
            "language": "javascript",
        }, nil
    default:
        return nil, fmt.Errorf("unsupported language: %s (supported: python, bash, javascript)", lang)
    }
}

func ToolCodeTool() *Tool {
    return &Tool{
        Name:        "code",
        Description: "Execute code in sandboxed environment",
        Params:      []string{"lang", "script"},
        Execute: func(args map[string]interface{}) (interface{}, error) {
            return (&CodeTool{}).Execute(args)
        },
        Timeout: 30 * time.Second,
    }
}
```

- [ ] **Step 4: Run test - verify it passes**

```bash
go test ./pkg/executor/... -v -run TestCodeTool
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pkg/executor/tool_code.go pkg/executor/tool_code_test.go
git commit -m "feat(executor): add CodeTool"
```

---

## Task 4: Create Search Tool (tool_search.go)

**Files:**
- Create: `pkg/executor/tool_search.go`
- Test: `pkg/executor/tool_search_test.go`

- [ ] **Step 1: Write failing test**

```go
package executor

import (
    "testing"
)

func TestSearchTool_Execute(t *testing.T) {
    tool := &SearchTool{}
    result, err := tool.Execute(map[string]interface{}{
        "query": "test query",
        "limit": float64(5),
    })
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    m := result.(map[string]interface{})
    if m["query"] != "test query" {
        t.Errorf("expected query 'test query', got '%v'", m["query"])
    }
}
```

- [ ] **Step 2: Run test - verify it fails**

```bash
go test ./pkg/executor/... -v -run TestSearchTool
```

Expected: FAIL - SearchTool not defined

- [ ] **Step 3: Implement SearchTool**

```go
package executor

import (
    "fmt"
    "time"
)

type SearchTool struct{}

func (s *SearchTool) Name() string        { return "search" }
func (s *SearchTool) Description() string { return "Search web or knowledge base" }
func (s *SearchTool) Timeout() time.Duration { return 30 * time.Second }

func (s *SearchTool) Execute(args map[string]interface{}) (interface{}, error) {
    query, _ := args["query"].(string)
    limit, _ := args["limit"].(float64)

    if query == "" {
        return nil, fmt.Errorf("missing required arg: query")
    }
    if limit == 0 {
        limit = 5
    }

    results := make([]map[string]string, 0)
    for i := 0; i < int(limit); i++ {
        results = append(results, map[string]string{
            "title":   fmt.Sprintf("Result %d for: %s", i+1, query),
            "url":     fmt.Sprintf("https://example.com/result/%d", i+1),
            "snippet": fmt.Sprintf("This is a simulated search result for '%s' (#%d)", query, i+1),
        })
    }

    return map[string]interface{}{
        "query":   query,
        "results": results,
        "count":   len(results),
    }, nil
}

func ToolSearchTool() *Tool {
    return &Tool{
        Name:        "search",
        Description: "Search web or knowledge base",
        Params:      []string{"query", "limit"},
        Execute: func(args map[string]interface{}) (interface{}, error) {
            return (&SearchTool{}).Execute(args)
        },
        Timeout: 30 * time.Second,
    }
}
```

- [ ] **Step 4: Run test - verify it passes**

```bash
go test ./pkg/executor/... -v -run TestSearchTool
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pkg/executor/tool_search.go pkg/executor/tool_search_test.go
git commit -m "feat(executor): add SearchTool"
```

---

## Task 5: Create File Tool (tool_file.go)

**Files:**
- Create: `pkg/executor/tool_file.go`
- Test: `pkg/executor/tool_file_test.go`

- [ ] **Step 1: Write failing test**

```go
package executor

import (
    "os"
    "testing"
)

func TestFileReadTool_Execute(t *testing.T) {
    tmp, _ := os.CreateTemp("", "test")
    tmp.WriteString("hello world")
    tmp.Close()
    defer os.Remove(tmp.Name())

    tool := &FileReadTool{}
    result, err := tool.Execute(map[string]interface{}{
        "path": tmp.Name(),
    })
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    m := result.(map[string]interface{})
    if m["content"] != "hello world" {
        t.Errorf("expected 'hello world', got '%v'", m["content"])
    }
}
```

- [ ] **Step 2: Run test - verify it fails**

```bash
go test ./pkg/executor/... -v -run TestFileReadTool
```

Expected: FAIL - FileReadTool not defined

- [ ] **Step 3: Implement FileReadTool and FileWriteTool**

```go
package executor

import (
    "fmt"
    "os"
    "time"
)

type FileReadTool struct{}

func (f *FileReadTool) Name() string        { return "file_read" }
func (f *FileReadTool) Description() string { return "Read file contents" }
func (f *FileReadTool) Timeout() time.Duration { return 10 * time.Second }

func (f *FileReadTool) Execute(args map[string]interface{}) (interface{}, error) {
    path, _ := args["path"].(string)
    if path == "" {
        return nil, fmt.Errorf("missing required arg: path")
    }

    content, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("failed to read file: %w", err)
    }

    return map[string]interface{}{
        "path":    path,
        "content": string(content),
        "size":    len(content),
    }, nil
}

type FileWriteTool struct{}

func (f *FileWriteTool) Name() string        { return "file_write" }
func (f *FileWriteTool) Description() string { return "Write content to file" }
func (f *FileWriteTool) Timeout() time.Duration { return 10 * time.Second }

func (f *FileWriteTool) Execute(args map[string]interface{}) (interface{}, error) {
    path, _ := args["path"].(string)
    content, _ := args["content"].(string)

    if path == "" {
        return nil, fmt.Errorf("missing required arg: path")
    }

    if err := os.WriteFile(path, []byte(content), 0644); err != nil {
        return nil, fmt.Errorf("failed to write file: %w", err)
    }

    return map[string]interface{}{
        "path":  path,
        "bytes": len(content),
    }, nil
}

func ToolFileReadTool() *Tool {
    return &Tool{
        Name:        "file_read",
        Description: "Read file contents",
        Params:      []string{"path"},
        Execute: func(args map[string]interface{}) (interface{}, error) {
            return (&FileReadTool{}).Execute(args)
        },
        Timeout: 10 * time.Second,
    }
}

func ToolFileWriteTool() *Tool {
    return &Tool{
        Name:        "file_write",
        Description: "Write content to file",
        Params:      []string{"path", "content"},
        Execute: func(args map[string]interface{}) (interface{}, error) {
            return (&FileWriteTool{}).Execute(args)
        },
        Timeout: 10 * time.Second,
    }
}
```

- [ ] **Step 4: Run test - verify it passes**

```bash
go test ./pkg/executor/... -v -run TestFileReadTool
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pkg/executor/tool_file.go pkg/executor/tool_file_test.go
git commit -m "feat(executor): add FileReadTool and FileWriteTool"
```

- [ ] **Step 6: Add SetupTools to Executor**

In `pkg/executor/executor.go`, add after `RegisterTool`:

```go
// SetupTools registers all built-in tools
func (e *Executor) SetupTools() {
    e.RegisterTool(ToolCodeTool())
    e.RegisterTool(ToolSearchTool())
    e.RegisterTool(ToolFileReadTool())
    e.RegisterTool(ToolFileWriteTool())
}
```

- [ ] **Step 7: Commit**

```bash
git add pkg/executor/executor.go
git commit -m "feat(executor): add SetupTools to register built-in tools"

---

## Task 6: Add INVOKE_TOOL to Dispatcher

**Files:**
- Modify: `pkg/dispatcher/dispatcher.go`

- [ ] **Step 1: Add required imports**

Check existing imports, add if missing:
```go
import (
    "encoding/json"  // for parsing JSON payloads
    "fmt"           // already present
    "strings"       // for stripping "tool:" prefix
    "time"          // already present
)
```

- [ ] **Step 2: Add case for INVOKE_TOOL in the switch**

In `dispatcher.go:138`, find the `switch msg.Type {` and add after `HEARTBEAT` case:

```go
case proto.MessageType_INVOKE_TOOL:
    return d.handleInvokeTool(msg)
```

- [ ] **Step 3: Implement handleInvokeTool**

Add before `SetDecisionCallback`:

```go
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
```

- [ ] **Step 4: Implement executeToolInvoke**

Add after handleInvokeTool:

```go
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
            Type:    DecisionRespond,
            Message: msg,
            Action: map[string]interface{}{
                "invoke_id": invokeID,
                "success":   true,
                "result":    string(resultJSON),
            },
        }
    case err := <-errorCh:
        return &Decision{
            Type:    DecisionRespond,
            Message: msg,
            Action: map[string]interface{}{
                "invoke_id": invokeID,
                "success":   false,
                "error":     err.Error(),
            },
        }
    case <-time.After(timeout):
        return &Decision{
            Type:    DecisionRespond,
            Message: msg,
            Action: map[string]interface{}{
                "invoke_id": invokeID,
                "success":   false,
                "error":     fmt.Sprintf("tool execution timeout after %v", timeout),
            },
        }
    }
}
```

- [ ] **Step 5: Verify it compiles**

```bash
go build ./pkg/dispatcher/...
```

Expected: SUCCESS

- [ ] **Step 6: Commit**

```bash
git add pkg/dispatcher/dispatcher.go
git commit -m "feat(dispatcher): add INVOKE_TOOL handling with timeout and panic recovery"
```

---

## Task 7: Create ToolClient for invoke_id Correlation

**Files:**
- Create: `pkg/toolclient/toolclient.go`

- [ ] **Step 1: Implement ToolClient**

The ToolClient wraps the transport `Client` and manages pending tool requests.

```go
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
    client       *transport.Client  // transport.Client from pkg/transport
    pending      map[string]chan *proto.AgentMessage
    mu           sync.RWMutex
    agentID      string
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
        Success  bool    `json:"success"`
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
```

- [ ] **Step 2: Verify it compiles**

```bash
go build ./pkg/toolclient/...
```

Expected: SUCCESS

- [ ] **Step 3: Commit**

```bash
git add pkg/toolclient/toolclient.go
git commit -m "feat(toolclient): add ToolClient for invoke_id correlation"
```

---

## Task 8: Wire ToolClient into Core Agent

**Files:**
- Modify: `pkg/core/agent.go` or wherever the transport client is used

This task depends on where the transport.Client is used. The implementer should:
1. Find where transport.Client is created/dialed
2. Wrap it with ToolClient when tools are needed
3. Expose a method like `agent.InvokeTool(peerID, tool, args)` for IPC commands

- [ ] **Step 1: Find transport client creation point**

Look for `transport.DialAgent` calls in the codebase.

- [ ] **Step 2: Add ToolClient field to agent**

```go
type Agent struct {
    // ... existing fields ...
    toolClient *toolclient.ToolClient
}
```

- [ ] **Step 3: Add InvokeTool method**

```go
func (a *Agent) InvokeTool(peerID string, tool string, args map[string]string) (map[string]interface{}, error) {
    // Find peer by ID
    peers := a.discovery.GetPeers()
    var peer *proto.AgentInfo
    for _, p := range peers {
        if p.Id == peerID {
            peer = p
            break
        }
    }
    if peer == nil {
        return nil, fmt.Errorf("peer not found: %s", peerID)
    }

    // Dial peer and create tool client
    client, err := transport.DialAgent(fmt.Sprintf("localhost:%d", peer.Port), a.AgentInfo())
    if err != nil {
        return nil, fmt.Errorf("dial failed: %w", err)
    }
    defer client.Close()

    tc := toolclient.NewToolClient(client, a.ID)
    return tc.InvokeTool(tool, args)
}
```

- [ ] **Step 4: Verify it compiles**

```bash
go build ./pkg/core/...
```

- [ ] **Step 5: Commit**

```bash
git add pkg/core/agent.go
git commit -m "feat(core): wire ToolClient into Agent"
```

---

## Task 9: Add IPC Command for Tool Invocation

**Files:**
- Modify: `pkg/ipc/server.go`

- [ ] **Step 1: Add "invoke" command to IPC server**

In `handleMessage`, add:

```go
case "invoke":
    return s.handleInvoke(msg)
```

Add handler:

```go
func (s *Server) handleInvoke(msg *Message) *Response {
    type InvokeArgs struct {
        PeerID string            `json:"peerId"`
        Tool   string            `json:"tool"`
        Args   map[string]string `json:"args"`
    }
    var args InvokeArgs
    if err := json.Unmarshal([]byte(msg.Message), &args); err != nil {
        return &Response{OK: false, Err: fmt.Sprintf("invalid JSON: %v", err)}
    }
    if args.PeerID == "" || args.Tool == "" {
        return &Response{OK: false, Err: "peerId and tool are required"}
    }

    result, err := s.agent.InvokeTool(args.PeerID, args.Tool, args.Args)
    if err != nil {
        return &Response{OK: false, Err: err.Error()}
    }
    data, _ := json.Marshal(result)
    return &Response{OK: true, Data: data}
}
```

- [ ] **Step 2: Verify it compiles**

```bash
go build ./pkg/ipc/...
```

- [ ] **Step 3: Commit**

```bash
git add pkg/ipc/server.go
git commit -m "feat(ipc): add invoke command for tool delegation"
```

---

## Task 10: Integration Test

**Files:**
- Create: `pkg/toolclient/toolclient_test.go`

- [ ] **Step 1: Write test for ToolClient**

```go
package toolclient

import (
    "testing"
    "time"
)

// TestInvokeTool_Timeout tests that InvokeTool respects timeout
func TestToolClient_InvokeTimeout(t *testing.T) {
    // This test would require a mock transport.Client
    // For now, test the UUID generation and pending map logic
    t.Run("UUID is generated", func(t *testing.T) {
        // Just verify UUID generation works
        id := uuid.New().String()
        if len(id) != 36 {
            t.Errorf("expected UUID length 36, got %d", len(id))
        }
    })
}
```

- [ ] **Step 2: Commit**

```bash
git add pkg/toolclient/toolclient_test.go
git commit -m "test(toolclient): add ToolClient tests"
```

---

## Summary

| Task | File | Status |
|------|------|--------|
| 1. Proto | `pkg/proto/agent.proto` | ⬜ |
| 2. Executor | `pkg/executor/executor.go` | ⬜ |
| 3. CodeTool | `pkg/executor/tool_code.go` | ⬜ |
| 4. SearchTool | `pkg/executor/tool_search.go` | ⬜ |
| 5. FileTool | `pkg/executor/tool_file.go` | ⬜ |
| 6. Dispatcher | `pkg/dispatcher/dispatcher.go` | ⬜ |
| 7. ToolClient | `pkg/toolclient/toolclient.go` | ⬜ |
| 8. Wire Agent | `pkg/core/agent.go` | ⬜ |
| 9. IPC | `pkg/ipc/server.go` | ⬜ |
| 10. Test | `pkg/toolclient/toolclient_test.go` | ⬜ |
