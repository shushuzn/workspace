# Task Delegation System Design

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable agents to delegate tasks to other agents via tools over P2P network.

**Architecture:** P2P对等网络，任意agent可发起任务或执行任务。基于现有TCP transport + discovery层实现。

**Tech Stack:** Go, JSON, existing transport/discovery/dispatcher/executor

---

## 1. Overview

Task Delegation allows an agent to invoke a tool on a remote peer agent and receive the result. The system uses protobuf messages with `invoke_id` for request-response correlation.

## 2. Proto Extension

### 2.1 New Message Types
Extend `proto.MessageType` enum in `pkg/proto/agent.proto`:
```proto
enum MessageType {
  TEXT = 0;
  TASK = 1;
  INVITE = 2;
  RESPONSE = 3;
  FORWARD = 4;
  HEARTBEAT = 5;
  INVOKE_TOOL = 10;  // New: request remote tool execution
  TOOL_RESULT = 11;   // New: tool execution result
}
```

### 2.2 Payload Messages
Define payload messages in `pkg/proto/agent.proto`:
```proto
message InvokeToolPayload {
  string invoke_id = 1;          // UUID to correlate request/response
  string tool = 2;               // tool name e.g. "code", "search"
  map<string, string> args = 3;  // tool-specific arguments
}

message ToolResultPayload {
  string invoke_id = 1;   // Must match invoke_id from InvokeToolPayload
  bool success = 2;
  bytes result = 3;         // JSON-encoded tool-specific result
  string error = 4;        // Error message if !success
}
```

### 2.3 AgentInfo Capabilities
The `AgentInfo.capabilities` field uses existing `Capability` proto message:
```proto
message Capability {
  string name = 1;              // e.g. "tool:code", "tool:search"
  string description = 2;
  repeated string params = 3;   // e.g. ["lang", "script"]
}
```

## 3. Tool System

### 3.1 Tool Interface
```go
type Tool interface {
    Name() string              // e.g. "code", "search"
    Description() string
    Execute(args map[string]interface{}) (interface{}, error)
    Timeout() time.Duration
}
```

### 3.2 Built-in Tools

| Tool | Name in Capability | Description | Args |
|------|---------------------|-------------|------|
| `code` | `tool:code` | Execute code in sandboxed environment | `{"lang": "python\|bash", "script": "..."}` |
| `search` | `tool:search` | Search the web or knowledge base | `{"query": "...", "limit": 5}` |
| `file_read` | `tool:file_read` | Read file contents | `{"path": "/absolute/path"}` |
| `file_write` | `tool:file_write` | Write content to file | `{"path": "/absolute/path", "content": "..."}` |

### 3.3 Tool Registration
Tools are registered at agent startup via the capabilities list:

```go
capabilities := []proto.Capability{
    {Name: "tool:code", Description: "Execute code in sandboxed environment", Params: []string{"lang", "script"}},
    {Name: "tool:search", Description: "Search web or knowledge base", Params: []string{"query", "limit"}},
    {Name: "tool:file_read", Description: "Read file contents", Params: []string{"path"}},
    {Name: "tool:file_write", Description: "Write content to file", Params: []string{"path", "content"}},
}
agent := core.NewAgent(id, name, port, capabilities)
```

### 3.4 Timeout
Default timeout is 30 seconds per tool execution. If tool execution exceeds timeout, return `ToolResultPayload{success: false, error: "tool execution timeout after 30s"}`.

## 4. Dispatcher Integration

### 4.1 Tool Registry Interface
```go
type ToolRegistry interface {
    FindTool(toolName string) (Tool, bool)  // e.g. "code" → CodeTool
}
```

Each agent maintains a local `ToolRegistry` containing its available tools.

### 4.2 Dispatcher INVOKE_TOOL Handling
When Dispatcher receives a message with `type == INVOKE_TOOL`:
1. Parse `payload` as `InvokeToolPayload`
2. Extract `tool` name (strip "tool:" prefix) and `args`
3. Look up tool in local `ToolRegistry`
4. If not found: send `ToolResultPayload{success: false, error: "tool not found: xxx"}`
5. If found: execute with timeout (30s default from tool.Timeout())
6. Send `TOOL_RESULT` message back to sender via existing reply mechanism

### 4.3 Response Routing (invoke_id correlation)
The existing transport `handleMessages` passes a `reply` function. The sender:
1. Generates a unique `invoke_id` (UUID) before sending
2. Keeps a local `pendingRequests map[string]chan ToolResultPayload`
3. Sends the message and waits on the channel
4. On receiving `TOOL_RESULT`, looks up channel by `invoke_id` and delivers the result

This is handled in a new `ToolClient` component that wraps the transport.

## 5. Transport Integration

### 5.1 Existing Transport
Uses existing TCP transport with protobuf message framing from transport/grpc.go.

### 5.2 Response Routing
Tool results are sent back to the sender via the same TCP connection using the existing `reply` function in `handleMessages`.

## 6. Flow

### 6.1 Alice invokes tool on Bob

```
Alice (port 19101)                    Bob (port 19102)
      |                                     |
      |  1. Discovery (existing)           |
      |<----------------------------------->|
      |                                     |
      |  2. TCP connection to Bob           |
      |----------------------------------->|
      |                                     |
      |  3. Send: INVOKE_TOOL payload       |
      |    {invoke_id: "uuid",             |
      |     tool: "code",                   |
      |     args: {script: "print(1)"}}    |
      |----------------------------------->|
      |                                     |
      |  4. Bob Dispatcher routes to        |
      |     CodeToolExecutor                |
      |                                     |
      |  5. Execute with 30s timeout       |
      |                                     |
      |  6. Send: TOOL_RESULT payload       |
      |    {invoke_id: "uuid",             |
      |     success: true,                 |
      |     result: {output: "1\n"}}      |
      |<-----------------------------------|
      |                                     |
      |  7. Alice receives result          |
```

## 7. File Structure

```
pkg/
  executor/
    executor.go       # Existing task executor
    tools.go          # NEW: Tool interface and registry
    tool_code.go      # NEW: Code execution tool (Python/Shell)
    tool_search.go    # NEW: Search tool (web + local)
    tool_file.go      # NEW: File read/write tool
  dispatcher/
    dispatcher.go     # MOD: Add INVOKE_TOOL handling
  proto/
    agent.proto       # MOD: Add INVOKE_TOOL, TOOL_RESULT, payload messages
```

## 8. Edge Cases

| Case | Handling |
|------|----------|
| Unknown tool name | Return `ToolResultPayload{success: false, error: "tool not found: xxx"}` |
| Tool execution timeout | Return `ToolResultPayload{success: false, error: "tool execution timeout after 30s"}` |
| Tool execution panic | Catch panic, return `ToolResultPayload{success: false, error: "tool execution panic: xxx"}` |
| Peer disconnects mid-execution | Task fails, sender's pending request times out |
| Invalid args | Return `ToolResultPayload{success: false, error: "invalid args for tool xxx: expected..."}` |
| invoke_id collision | Use UUID to avoid collision |

## 9. Testing

- Unit tests for each tool executor
- Integration test: Alice invokes Bob's code tool, verifies result
- Integration test: Alice invokes Bob's search tool, verifies result
- Timeout test: verify 30s timeout works
- Error test: verify unknown tool returns proper error
