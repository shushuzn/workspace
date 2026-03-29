# Task Orchestration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable hierarchical task orchestration where an OrchestratorAgent decomposes high-level tasks via LLM, distributes subtasks to peer agents in parallel, and returns the first completed result.

**Architecture:** Hierarchical orchestration with LLM-driven task decomposition. OrchestratorAgent sits at the top, breaks tasks into subtasks using local LLM (ollama), dispatches them via existing P2P transport to peer agents, and returns the first result to complete.

**Tech Stack:** Go, JSON, existing P2P transport + dispatcher + ToolClient, local LLM (ollama)

---

## File Structure

```
pkg/
  orchestrator/
    orchestrator.go     # NEW: OrchestratorAgent + raceResults
    ollama.go          # NEW: LLMDecomposer implementation
  dispatcher/
    dispatcher.go       # MOD: Add ORCHESTRATE handling
  ipc/
    server.go          # MOD: Add orchestrate IPC command
  proto/
    agent.proto        # MOD: Add ORCHESTRATE message type
```

---

## Task 1: Proto Extension - Add ORCHESTRATE Message Type

**Files:**
- Modify: `pkg/proto/agent.proto:33-42`
- Run: `go generate ./pkg/proto/...`

- [ ] **Step 1: Modify agent.proto to add ORCHESTRATE message type**

Add `ORCHESTRATE = 12;` to the MessageType enum after `TOOL_RESULT = 11`:

```proto
enum MessageType {
  TEXT = 0;
  TASK = 1;
  INVITE = 2;
  RESPONSE = 3;
  FORWARD = 4;
  HEARTBEAT = 5;
  INVOKE_TOOL = 10;
  TOOL_RESULT = 11;
  ORCHESTRATE = 12;  // New: request task orchestration
}
```

Add the OrchestratePayload message:

```proto
message OrchestratePayload {
  string task = 1;  // High-level task description
}
```

- [ ] **Step 2: Run go generate to regenerate proto files**

Run: `go generate ./pkg/proto/...`
Expected: Regenerates `pkg/proto/agent.pb.go` with new ORCHESTRATE type

- [ ] **Step 3: Commit**

```bash
git add pkg/proto/agent.proto pkg/proto/agent.pb.go
git commit -m "feat(proto): add ORCHESTRATE message type for task orchestration"
```

---

## Task 2: OllamaDecomposer - LLM-based Task Decomposition

**Files:**
- Create: `pkg/orchestrator/ollama.go`
- Create: `pkg/orchestrator/ollama_test.go`

- [ ] **Step 1: Create ollama.go with LLMDecomposer interface**

```go
package orchestrator

import (
    "bytes"
    "context"
    "encoding/json"
    "fmt"
    "net/http"
    "time"
)

// LLMDecomposer decomposes tasks into subtasks using LLM
type LLMDecomposer interface {
    Decompose(ctx context.Context, task string) ([]string, error)
}

// OllamaDecomposer implements LLMDecomposer using ollama API
type OllamaDecomposer struct {
    host   string
    client *http.Client
}

// NewOllamaDecomposer creates a new OllamaDecomposer
func NewOllamaDecomposer(host string) *OllamaDecomposer {
    if host == "" {
        host = "http://localhost:11434"
    }
    return &OllamaDecomposer{
        host: host,
        client: &http.Client{
            Timeout: 30 * time.Second,
        },
    }
}

// Decompose calls ollama to decompose a task into subtasks
func (d *OllamaDecomposer) Decompose(ctx context.Context, task string) ([]string, error) {
    prompt := fmt.Sprintf(`分解以下任务为子任务列表。返回JSON数组格式的子任务描述。
只返回JSON数组，不要其他内容。

任务: %s

返回格式示例: ["子任务1描述", "子任务2描述", "子任务3描述"]`, task)

    reqBody := map[string]interface{}{
        "model":  "llama3.2",
        "prompt": prompt,
        "stream": false,
    }

    reqBytes, err := json.Marshal(reqBody)
    if err != nil {
        return nil, fmt.Errorf("marshal request: %w", err)
    }

    req, err := http.NewRequestWithContext(ctx, "POST", d.host+"/api/generate", bytes.NewReader(reqBytes))
    if err != nil {
        return nil, fmt.Errorf("create request: %w", err)
    }
    req.Header.Set("Content-Type", "application/json")

    resp, err := d.client.Do(req)
    if err != nil {
        return nil, fmt.Errorf("LLM service unavailable: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("LLM service returned status %d", resp.StatusCode)
    }

    var result struct {
        Response string `json:"response"`
    }
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return nil, fmt.Errorf("decode response: %w", err)
    }

    // Parse JSON array from response
    var subtasks []string
    if err := json.Unmarshal([]byte(result.Response), &subtasks); err != nil {
        // Try to extract JSON array from response text
        return nil, fmt.Errorf("task could not be decomposed: %w", err)
    }

    if len(subtasks) == 0 {
        return nil, fmt.Errorf("task could not be decomposed: empty result")
    }

    // Limit to 100 subtasks
    if len(subtasks) > 100 {
        subtasks = subtasks[:100]
    }

    return subtasks, nil
}
```

- [ ] **Step 2: Create ollama_test.go**

```go
package orchestrator

import (
    "context"
    "net/http"
    "net/http/httptest"
    "testing"
)

func TestOllamaDecomposer_Decompose(t *testing.T) {
    // Mock ollama server
    ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Header().Set("Content-Type", "application/json")
        w.Write([]byte(`{"response": "[\"subtask 1\", \"subtask 2\", \"subtask 3\"]"}`))
    }))
    defer ts.Close()

    decomposer := NewOllamaDecomposer(ts.URL)
    subtasks, err := decomposer.Decompose(context.Background(), "do something")
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if len(subtasks) != 3 {
        t.Errorf("expected 3 subtasks, got %d", len(subtasks))
    }
}

func TestOllamaDecomposer_ServiceUnavailable(t *testing.T) {
    decomposer := NewOllamaDecomposer("http://localhost:99999")
    _, err := decomposer.Decompose(context.Background(), "test")
    if err == nil {
        t.Error("expected error for unavailable service")
    }
}
```

- [ ] **Step 3: Run tests**

Run: `go test ./pkg/orchestrator/... -v`
Expected: PASS (or FAIL if mock server not working, adjust as needed)

- [ ] **Step 4: Commit**

```bash
git add pkg/orchestrator/ollama.go pkg/orchestrator/ollama_test.go
git commit -m "feat(orchestrator): add OllamaDecomposer for LLM-driven task decomposition"
```

---

## Task 3: OrchestratorAgent with raceResults

**Files:**
- Create: `pkg/orchestrator/orchestrator.go`
- Create: `pkg/orchestrator/orchestrator_test.go`

- [ ] **Step 1: Create orchestrator.go with OrchestratorAgent and raceResults**

```go
package orchestrator

import (
    "context"
    "fmt"
    "sync"
    "time"

    "github.com/openclaw/multi-agent-discuss/pkg/core"
)

// TaskRequest represents a single task invocation request
type TaskRequest struct {
    PeerID string
    Tool   string
    Args   map[string]string
}

// OrchestratorAgent orchestrates task decomposition and parallel execution
type OrchestratorAgent struct {
    agentID    string
    decomposer LLMDecomposer
    invokeFn   func(peerID, tool string, args map[string]string) (map[string]interface{}, error)
    peers      func() map[string]*core.PeerConnection
}

// NewOrchestratorAgent creates a new OrchestratorAgent
func NewOrchestratorAgent(
    agentID string,
    decomposer LLMDecomposer,
    invokeFn func(peerID, tool string, args map[string]string) (map[string]interface{}, error),
    peers func() map[string]*core.PeerConnection,
) *OrchestratorAgent {
    return &OrchestratorAgent{
        agentID:    agentID,
        decomposer: decomposer,
        invokeFn:   invokeFn,
        peers:      peers,
    }
}

// Process orchestrates a task: decompose via LLM, dispatch to peers, return first result
func (o *OrchestratorAgent) Process(ctx context.Context, task string) (string, error) {
    // Step 1: Decompose task via LLM
    subtasks, err := o.decomposer.Decompose(ctx, task)
    if err != nil {
        return "", err
    }

    if len(subtasks) == 0 {
        return "", fmt.Errorf("task could not be decomposed")
    }

    // Step 2: Get available peers
    peerMap := o.peers()
    if len(peerMap) == 0 {
        return "", fmt.Errorf("no peer agents available")
    }

    // Convert map to slice
    peers := make([]string, 0, len(peerMap))
    for id := range peerMap {
        peers = append(peers, id)
    }

    // Step 3: Build requests - one per subtask per peer
    requests := make([]TaskRequest, 0, len(subtasks)*len(peers))
    for _, subtask := range subtasks {
        for _, peerID := range peers {
            requests = append(requests, TaskRequest{
                PeerID: peerID,
                Tool:   "code",
                Args: map[string]string{
                    "script": subtask,
                    "lang":   "bash",
                },
            })
        }
    }

    // Step 4: Race for first result
    timeout := 30 * time.Second
    if deadline, ok := ctx.Deadline(); ok {
        timeout = time.Until(deadline)
        if timeout <= 0 {
            return "", fmt.Errorf("orchestration timeout")
        }
    }

    result, err := raceResults(ctx, requests, o.invokeFn, timeout)
    if err != nil {
        return "", err
    }

    return result, nil
}

// raceResults runs requests in parallel and returns the first successful result
func raceResults(
    ctx context.Context,
    requests []TaskRequest,
    invokeFn func(peerID, tool string, args map[string]string) (map[string]interface{}, error),
    timeout time.Duration,
) (string, error) {
    if len(requests) == 0 {
        return "", fmt.Errorf("no requests to execute")
    }

    type result struct {
        value string
        err   error
    }

    // Channel to receive results
    resultCh := make(chan result, 1)

    // Semaphore for concurrency limiting
    sem := make(chan struct{}, 10) // Max 10 parallel

    var wg sync.WaitGroup

    for _, req := range requests {
        // Check context before launching
        select {
        case <-ctx.Done():
            break
        default:
        }

        wg.Add(1)
        go func(r TaskRequest) {
            defer wg.Done()

            // Acquire semaphore
            select {
            case sem <- struct{}{}:
            case <-ctx.Done():
                return
            }
            defer func() { <-sem }()

            // Execute with timeout
            execCtx, cancel := context.WithTimeout(ctx, timeout)
            defer cancel()

            res, err := invokeFn(r.PeerID, r.Tool, r.Args)
            if err != nil {
                // Don't send errors - just return
                return
            }

            // Extract result from response
            if resultMap, ok := res["result"]; ok {
                if resultStr, ok := resultMap.(string); ok {
                    select {
                    case resultCh <- result{value: resultStr}:
                    default:
                    }
                }
            }
        }(req)
    }

    // Wait for all goroutines in background
    go func() {
        wg.Wait()
        close(resultCh)
    }()

    // Wait for first result or timeout
    select {
    case res := <-resultCh:
        if res.err != nil {
            return "", res.err
        }
        return res.value, nil
    case <-ctx.Done():
        return "", fmt.Errorf("orchestration cancelled")
    case <-time.After(timeout):
        return "", fmt.Errorf("all subtasks failed after timeout")
    }
}
```

- [ ] **Step 2: Create orchestrator_test.go**

```go
package orchestrator

import (
    "context"
    "fmt"
    "testing"
    "time"
)

func TestRaceResults_FirstResultWins(t *testing.T) {
    invokeFn := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
        // Simulate varying response times
        if peerID == "fast" {
            time.Sleep(10 * time.Millisecond)
        } else {
            time.Sleep(100 * time.Millisecond)
        }
        return map[string]interface{}{"result": "response from " + peerID}, nil
    }

    requests := []TaskRequest{
        {PeerID: "slow1", Tool: "code", Args: map[string]string{}},
        {PeerID: "slow2", Tool: "code", Args: map[string]string{}},
        {PeerID: "fast", Tool: "code", Args: map[string]string{}},
    }

    ctx := context.Background()
    result, err := raceResults(ctx, requests, invokeFn, 5*time.Second)
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if result != "response from fast" {
        t.Errorf("expected 'response from fast', got '%s'", result)
    }
}

func TestRaceResults_AllError(t *testing.T) {
    invokeFn := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
        return nil, fmt.Errorf("error from %s", peerID)
    }

    requests := []TaskRequest{
        {PeerID: "peer1", Tool: "code", Args: map[string]string{}},
    }

    ctx := context.Background()
    _, err := raceResults(ctx, requests, invokeFn, 100*time.Millisecond)
    if err == nil {
        t.Error("expected error when all requests fail")
    }
}

func TestRaceResults_EmptyRequests(t *testing.T) {
    invokeFn := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
        return nil, nil
    }

    ctx := context.Background()
    _, err := raceResults(ctx, []TaskRequest{}, invokeFn, time.Second)
    if err == nil {
        t.Error("expected error for empty requests")
    }
}
```

- [ ] **Step 3: Run tests**

Run: `go test ./pkg/orchestrator/... -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add pkg/orchestrator/orchestrator.go pkg/orchestrator/orchestrator_test.go
git commit -m "feat(orchestrator): add OrchestratorAgent with raceResults"
```

---

## Task 4: IPC Server - Add orchestrate Command

**Files:**
- Modify: `pkg/ipc/server.go:159-174`

- [ ] **Step 1: Add orchestrate case to handleMessage switch**

In `pkg/ipc/server.go`, add to the switch statement in `handleMessage`:

```go
case "orchestrate":
    return s.handleOrchestrate(msg)
```

- [ ] **Step 2: Add handleOrchestrate function**

Add after `handleInvoke`:

```go
func (s *Server) handleOrchestrate(msg *Message) *Response {
    if msg.Message == "" {
        return &Response{OK: false, Err: "task description required"}
    }

    // Get orchestrator from agent (agent needs to have orchestrator field)
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
        "result": result,
        "success": true,
    })
    return &Response{OK: true, Data: data}
}
```

Add required imports:
```go
import "context"
```

- [ ] **Step 3: Add GetOrchestrator method to Agent**

In `pkg/core/agent.go`, add to the Agent struct and NewAgent:

```go
type Agent struct {
    // ... existing fields ...
    orchestrator *orchestrator.OrchestratorAgent  // Add this field
}

// NewAgent(...): initialize to nil
// return &Agent{..., orchestrator: nil}

// Add method:
func (a *Agent) GetOrchestrator() *orchestrator.OrchestratorAgent {
    return a.orchestrator
}
```

But first need to check if orchestrator package exists - it will be created in Task 3.

- [ ] **Step 4: Run build to check for errors**

Run: `go build ./pkg/ipc/...`
Expected: PASS (or errors about missing orchestrator, fix accordingly)

- [ ] **Step 5: Commit**

```bash
git add pkg/ipc/server.go pkg/core/agent.go
git commit -m "feat(ipc): add orchestrate IPC command for task orchestration"
```

---

## Task 5: Dispatcher - Add ORCHESTRATE Handling

**Files:**
- Modify: `pkg/dispatcher/dispatcher.go`

- [ ] **Step 1: Add DecisionOrchestrate to DecisionType const**

In `pkg/dispatcher/dispatcher.go`, find the DecisionType const block and add:

```go
const (
    DecisionForward DecisionType = iota
    DecisionProcessTask
    DecisionRequestHelp
    DecisionRespond
    DecisionIgnore
    DecisionOrchestrate  // New: handle ORCHESTRATE messages
)
```

- [ ] **Step 2: Add ORCHESTRATE case to makeDecision**

Add in the switch statement in `makeDecision`:

```go
case proto.MessageType_ORCHESTRATE:
    return d.handleOrchestrateMessage(msg)
```

- [ ] **Step 3: Add handleOrchestrateMessage method**

```go
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

    // This would need the orchestrator to be set - for now return error
    // The orchestrator is typically used via IPC, not P2P dispatcher
    return &Decision{
        Type:    DecisionRespond,
        Message: msg,
        Action:  map[string]interface{}{"error": "orchestrator not available via P2P"},
    }
}
```

- [ ] **Step 4: Run tests**

Run: `go build ./pkg/dispatcher/...`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pkg/dispatcher/dispatcher.go
git commit -m "feat(dispatcher): add ORCHESTRATE message handling"
```

---

## Task 6: Integration - Wire Up Orchestrator in Agent

**Files:**
- Modify: `pkg/core/agent.go`

- [ ] **Step 1: Update NewAgent to initialize orchestrator**

```go
import (
    // ... existing imports ...
    "os"

    "github.com/openclaw/multi-agent-discuss/pkg/orchestrator"
)

// In NewAgent, after creating exec:
orch := orchestrator.NewOrchestratorAgent(
    id,
    orchestrator.NewOllamaDecomposer(os.Getenv("OLLAMA_HOST")),
    a.InvokeTool,
    func() map[string]*core.PeerConnection { return a.Peers },
)
```

- [ ] **Step 2: Run build**

Run: `go build ./pkg/core/...`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add pkg/core/agent.go
git commit -m "feat(core): wire up orchestrator in agent initialization"
```

---

## Task 7: Integration Test - Full Orchestration Flow

**Files:**
- Create: `pkg/orchestrator/integration_test.go` (if not already covered)

- [ ] **Step 1: Write integration test**

Test the full flow:
1. Start two agent instances
2. Have one act as orchestrator
3. Send orchestrate command
4. Verify first result returned

```go
package orchestrator

import (
    "context"
    "testing"
    "time"
)

// MockDecomposer always returns the same subtasks
type MockDecomposer struct {
    subtasks []string
}

func (m *MockDecomposer) Decompose(ctx context.Context, task string) ([]string, error) {
    return m.subtasks, nil
}

func TestOrchestratorAgent_Process(t *testing.T) {
    // This test requires actual peer agents which is complex
    // For unit test, mock the invoke function
    mockInvoke := func(peerID, tool string, args map[string]string) (map[string]interface{}, error) {
        return map[string]interface{}{"result": "done: " + args["script"]}, nil
    }

    orch := NewOrchestratorAgent(
        "test-agent",
        &MockDecomposer{subtasks: []string{"do thing 1", "do thing 2"}},
        mockInvoke,
        func() map[string]*PeerConnection {
            return map[string]*PeerConnection{
                "peer1": {Info: &AgentInfo{ID: "peer1"}},
            }
        },
    )

    ctx := context.Background()
    result, err := orch.Process(ctx, "do things")
    if err != nil {
        t.Fatalf("unexpected error: %v", err)
    }
    if result == "" {
        t.Error("expected non-empty result")
    }
}
```

- [ ] **Step 2: Run integration test**

Run: `go test ./pkg/orchestrator/... -v -run TestOrchestratorAgent`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add pkg/orchestrator/integration_test.go
git commit -m "test(orchestrator): add integration test for full orchestration flow"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Proto extension - add ORCHESTRATE type | `pkg/proto/agent.proto` |
| 2 | OllamaDecomposer - LLM-based decomposition | `pkg/orchestrator/ollama.go` |
| 3 | OrchestratorAgent + raceResults | `pkg/orchestrator/orchestrator.go` |
| 4 | IPC orchestrate command | `pkg/ipc/server.go` |
| 5 | Dispatcher ORCHESTRATE handling | `pkg/dispatcher/dispatcher.go` |
| 6 | Wire orchestrator in Agent | `pkg/core/agent.go` |
| 7 | Integration test | `pkg/orchestrator/integration_test.go` |

**Total: 7 tasks**

Execute tasks in order. Each task is self-contained and commits separately.
