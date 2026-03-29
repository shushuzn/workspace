# Task Orchestration System Design

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable hierarchical task orchestration where an OrchestratorAgent decomposes high-level tasks via LLM, distributes subtasks to peer agents in parallel, and returns the first completed result.

**Architecture:** Hierarchical orchestration with LLM-driven task decomposition. OrchestratorAgent sits at the top, breaks tasks into subtasks using local LLM (ollama), dispatches them via existing ToolClient/P2P transport to peer agents, and returns the first result to complete.

**Tech Stack:** Go, JSON, existing P2P transport + dispatcher + ToolClient, local LLM (ollama)

---

## 1. Overview

Task Orchestration enables a single agent to act as an orchestrator that:
1. Receives a complex high-level task via IPC
2. Decomposes it into parallelizable subtasks using LLM
3. Dispatches subtasks to available peer agents via P2P
4. Returns the first completed result to the caller

This follows the AutoGen OrchestratorAgent pattern adapted for the existing Go P2P multi-agent system.

---

## 2. Components

### 2.1 LLMDecomposer

Decomposes tasks using a local LLM (ollama).

```go
type LLMDecomposer interface {
    Decompose(ctx context.Context, task string) ([]string, error)
}

// Returns list of subtask descriptions, or error if decomposition fails
```

**Default implementation**: Calls ollama API at `http://localhost:11434` with a prompt that extracts subtasks as a JSON array of strings.

### 2.2 OrchestratorAgent

```go
type OrchestratorAgent struct {
    agentID    string
    decomposer LLMDecomposer
    invokeFn   func(peerID, tool string, args map[string]string) (map[string]interface{}, error)
    peers      func() map[string]*PeerConnection  // Note: returns map, not slice
}
```

**Process(task string) (string, error)**:
1. Call decomposer with timeout (30s) to get subtask list
2. Convert peers map to slice
3. If no peers available, return error
4. Dispatch all subtasks to all peers in parallel using `raceResults()`:
   - Launch one goroutine per subtask per peer
   - Use `select` with channels to wait for first result
   - Return immediately on first result
   - Cancel remaining requests (best-effort via context cancellation)
5. Return result or error

### 2.3 raceResults helper

```go
func raceResults(ctx context.Context, requests []TaskRequest, timeout time.Duration) (string, error) {
    // TaskRequest: {peerID string, tool string, args map[string]string}
    // Creates goroutine per request, races them with select
    // Returns first result or timeout error
}
```

---

## 3. IPC Protocol Extension

### 3.1 New IPC Command: orchestrate

Add to `ipc/server.go`:

```go
case "orchestrate":
    // Parse JSON payload: {task: "high level task description"}
    // Call orchestrator.Process(task)
    // Return result or error
```

### 3.2 New Message Type: ORCHESTRATE (P2P)

Add to `proto.MessageType`:
```proto
ORCHESTRATE = 12;  // New: request task orchestration
```

### 3.3 OrchestratePayload

```proto
message OrchestratePayload {
    string task = 1;  // High-level task description
}
```

---

## 4. Dispatcher Integration

### 4.1 New Decision: DecisionOrchestrate

In `pkg/dispatcher/dispatcher.go`, add `DecisionOrchestrate` to the DecisionType const block:

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

### 4.2 ORCHESTRATE Handler

When dispatcher receives `ORCHESTRATE` message:
1. Parse task from payload as `OrchestratePayload`
2. Create OrchestratorAgent with dependencies
3. Call `orchestrator.Process(task)` with timeout
4. Build response with result and send back via replyFn

---

## 5. SubTask Distribution

### 5.1 Peer Selection

For each subtask:
- Select all available peers (no capability matching in v1)
- Dispatch to all peers in parallel

### 5.2 Concurrency Bounding

- Max parallel goroutines: 10 (configurable via `MAX_PARALLEL_REQUESTS`)
- Use semaphore pattern to bound concurrency

---

## 6. Flow

```
CLI Client (port 19101+10000)    Orchestrator (port 19102)          Peer Agents
           |                              |                            |
           |  1. IPC: orchestrate         |                            |
           |  {task: "do X and Y"}       |                            |
           |----------------------------->|                            |
           |                              |                            |
           |                              |  2. LLM Decompose          |
           |                              |  ["do X", "do Y"]         |
           |                              |                            |
           |                              |  3. ToolClient race        |
           |                              |  do X → Agent1, Agent2     |
           |                              |  do Y → Agent1, Agent2    |
           |                              |--------------------------->|
           |                              |                            |
           |                              |  4. First result wins     |
           |                              |<---------------------------|
           |                              |                            |
           |  5. IPC response            |                            |
           |  {result: "...", success}   |                            |
           |<-----------------------------|                            |
```

---

## 7. File Structure

```
pkg/
  orchestrator/
    orchestrator.go     # NEW: OrchestratorAgent + raceResults
    ollama.go           # NEW: LLMDecomposer implementation using ollama
    doc.go              # NEW: package docs
  dispatcher/
    dispatcher.go       # MOD: Add DecisionOrchestrate + ORCHESTRATE case
  ipc/
    server.go           # MOD: Add orchestrate IPC command
  proto/
    agent.proto         # MOD: Add ORCHESTRATE message type + OrchestratePayload
```

---

## 8. Edge Cases

| Case | Handling |
|------|----------|
| LLM unavailable | Return error `LLM service unavailable` |
| LLM returns empty | Return error `task could not be decomposed` |
| LLM returns >100 subtasks | Truncate to first 100 |
| No peers available | Return error `no peer agents available` |
| All subtasks fail | Return error `all subtasks failed after timeout` |
| Timeout (30s default) | Return first result received or timeout error |
| Peer disconnects mid-request | Skip, wait for other results |
| Empty decomposition | Return error `task could not be decomposed` |

---

## 9. Configuration

```go
// Environment variables
OLLAMA_HOST=http://localhost:11434  // default
ORCHESTRATION_TIMEOUT=30s           // default 30 seconds
MAX_PARALLEL_REQUESTS=10            // default 10

// Agent initialization in pkg/core/agent.go
// Use agent.InvokeTool which handles peer dialing internally
orchestrator := orchestrator.NewOrchestratorAgent(
    agent.ID,
    ollama.NewOllamaDecomposer(os.Getenv("OLLAMA_HOST")),
    agent.InvokeTool,  // func(peerID, tool string, args map[string]string) (map[string]interface{}, error)
    agent.GetPeers,    // func() map[string]*PeerConnection
)
```

---

## 10. Testing

- Unit tests for `raceResults` with mock requests
- Unit tests for `OllamaDecomposer` (mock ollama HTTP responses)
- Unit tests for `OrchestratorAgent.Process()` with mock ToolClient
- Integration test: orchestrator → 3 peer agents, verify first result returned
- Error test: verify LLM failure returns proper error
- Timeout test: verify 30s timeout works
