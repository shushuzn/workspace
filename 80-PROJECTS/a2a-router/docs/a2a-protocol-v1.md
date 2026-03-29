# A2A Protocol v1.0 Specification

> **Agent-to-Agent Communication Protocol**
> 
> Version: 1.0  
> Status: Draft  
> Date: 2026-03-27

---

## 1. Overview

A2A (Agent-to-Agent) Protocol is a lightweight communication protocol designed for AI agents to collaborate, delegate tasks, and share information in a multi-agent ecosystem.

### 1.1 Design Goals

- **Simplicity**: Easy to implement in any language
- **Reliability**: Guaranteed message delivery with retries
- **Scalability**: Support 100+ agents concurrently
- **Extensibility**: Plugin architecture for custom message types
- **Interoperability**: Works with existing MCP (Model Context Protocol) infrastructure

### 1.2 Core Concepts

| Concept | Description |
|---------|-------------|
| **Agent** | An autonomous AI entity with unique ID and capabilities |
| **Message** | Unit of communication between agents |
| **Router** | Central hub that routes messages between agents |
| **Topic** | Named channel for pub/sub communication |
| **Capability** | Service that an agent can provide |

---

## 2. Message Format

### 2.1 Message Structure

```typescript
interface A2AMessage {
  // Required fields
  id: string;              // Unique message ID (UUID)
  type: MessageType;       // Message type
  priority: Priority;      // Message priority
  from: string;            // Source agent ID
  to: string;              // Target agent ID or 'broadcast'
  timestamp: number;       // Unix timestamp (ms)
  
  // Payload
  payload: any;            // Message-specific data
  
  // Optional metadata
  metadata?: {
    ttl?: number;          // Time to live (seconds)
    retry?: number;        // Retry count (default: 3)
    tags?: string[];       // Searchable tags
    correlationId?: string; // For request-response pairing
    timeout?: number;      // Response timeout (ms)
  };
}

enum MessageType {
  // Task delegation
  TASK = 'TASK',          // Request agent to perform task
  TASK_ACK = 'TASK_ACK',  // Task received acknowledgment
  TASK_RESULT = 'TASK_RESULT', // Task completion result
  
  // Query/Response
  QUERY = 'QUERY',        // Request information
  RESPONSE = 'RESPONSE',  // Response to query
  
  // Events
  EVENT = 'EVENT',        // Broadcast event
  HEARTBEAT = 'HEARTBEAT', // Agent health check
  
  // Lifecycle
  REGISTER = 'REGISTER',  // Agent registration
  UNREGISTER = 'UNREGISTER', // Agent unregistration
  DISCOVER = 'DISCOVER',  // Capability discovery
}

enum Priority {
  CRITICAL = 0,   // Immediate processing
  HIGH = 1,       // Process before normal
  NORMAL = 2,     // Standard priority
  LOW = 3,        // Background processing
}
```

### 2.2 Message Examples

#### Task Delegation
```json
{
  "id": "msg-001",
  "type": "TASK",
  "priority": "HIGH",
  "from": "patrol-agent",
  "to": "ai-roundtable",
  "timestamp": 1774623000000,
  "payload": {
    "task": "discuss_problem",
    "problemId": "problem-123",
    "topic": "ESLint errors in NewsHub",
    "context": "Found 15 lint errors..."
  },
  "metadata": {
    "ttl": 3600,
    "retry": 3,
    "timeout": 300000,
    "correlationId": "corr-001"
  }
}
```

#### Task Result
```json
{
  "id": "msg-002",
  "type": "TASK_RESULT",
  "priority": "NORMAL",
  "from": "ai-roundtable",
  "to": "patrol-agent",
  "timestamp": 1774623100000,
  "payload": {
    "taskId": "msg-001",
    "status": "success",
    "result": {
      "consensus": "Run eslint --fix",
      "confidence": 0.85
    }
  },
  "metadata": {
    "correlationId": "corr-001"
  }
}
```

#### Event Broadcast
```json
{
  "id": "msg-003",
  "type": "EVENT",
  "priority": "NORMAL",
  "from": "patrol-agent",
  "to": "broadcast",
  "timestamp": 1774623200000,
  "payload": {
    "event": "problem_detected",
    "problem": {
      "id": "problem-123",
      "title": "ESLint errors",
      "severity": "medium"
    }
  },
  "metadata": {
    "tags": ["lint", "code-quality"]
  }
}
```

#### Capability Discovery
```json
{
  "id": "msg-004",
  "type": "DISCOVER",
  "priority": "NORMAL",
  "from": "patrol-agent",
  "to": "broadcast",
  "timestamp": 1774623300000,
  "payload": {
    "query": "code-review"
  }
}
```

#### Discovery Response
```json
{
  "id": "msg-005",
  "type": "RESPONSE",
  "priority": "NORMAL",
  "from": "ai-roundtable",
  "to": "patrol-agent",
  "timestamp": 1774623301000,
  "payload": {
    "capabilities": [
      {
        "agentId": "ai-roundtable",
        "capabilities": ["discuss", "analyze", "decide"],
        "status": "idle",
        "load": 0.2
      }
    ]
  }
}
```

---

## 3. Agent Registration

### 3.1 Registration Message

```json
{
  "id": "reg-001",
  "type": "REGISTER",
  "priority": "HIGH",
  "from": "patrol-agent",
  "to": "router",
  "timestamp": 1774623000000,
  "payload": {
    "agentId": "patrol-agent",
    "capabilities": ["scan", "lint-check", "plan-execution"],
    "metadata": {
      "version": "1.0.0",
      "supportedProtocols": ["a2a-v1"]
    }
  }
}
```

### 3.2 Heartbeat

```json
{
  "id": "hb-001",
  "type": "HEARTBEAT",
  "priority": "LOW",
  "from": "patrol-agent",
  "to": "router",
  "timestamp": 1774623600000,
  "payload": {
    "status": "healthy",
    "load": 0.3,
    "activeTasks": 2
  }
}
```

---

## 4. Routing Rules

### 4.1 Direct Routing

```
from: agent-a
to: agent-b
→ Router delivers directly to agent-b
```

### 4.2 Broadcast Routing

```
from: agent-a
to: broadcast
→ Router delivers to all registered agents except sender
```

### 4.3 Topic-based Routing (Future)

```
topic: "code-quality"
→ Router delivers to all agents subscribed to "code-quality"
```

### 4.4 Capability-based Routing (Future)

```
to: "capability:code-review"
→ Router finds agent with code-review capability and delivers
```

---

## 5. Error Handling

### 5.1 Error Message Format

```json
{
  "id": "err-001",
  "type": "RESPONSE",
  "priority": "HIGH",
  "from": "router",
  "to": "agent-a",
  "timestamp": 1774623000000,
  "payload": {
    "error": true,
    "errorCode": "AGENT_NOT_FOUND",
    "errorMessage": "Target agent 'agent-b' not found or offline",
    "originalMessageId": "msg-001"
  }
}
```

### 5.2 Error Codes

| Code | Description | Retryable |
|------|-------------|-----------|
| `AGENT_NOT_FOUND` | Target agent doesn't exist | No |
| `AGENT_OFFLINE` | Target agent is offline | Yes |
| `TIMEOUT` | Response timeout | Yes |
| `INVALID_MESSAGE` | Message format error | No |
| `RATE_LIMITED` | Too many messages | Yes |
| `INTERNAL_ERROR` | Router internal error | Yes |

---

## 6. Transport Layer

### 6.1 MCP (Model Context Protocol)

A2A Protocol is designed to work over MCP:

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Agent A │────→│  MCP    │────→│  MCP    │
│ (Client)│     │ Client  │     │ Server  │
└─────────┘     └─────────┘     └────┬────┘
                                     │
                                ┌────┴────┐
                                │  A2A    │
                                │ Router  │
                                └────┬────┘
                                     │
┌─────────┐     ┌─────────┐     ┌────┴────┐
│ Agent B │←────│  MCP    │←────│  MCP    │
│ (Client)│     │ Client  │     │ Server  │
└─────────┘     └─────────┘     └─────────┘
```

### 6.2 HTTP/WebSocket Alternative

For non-MCP environments:

```
POST /a2a/v1/messages
Content-Type: application/json

{
  "message": { ... },
  "auth": {
    "agentId": "patrol-agent",
    "token": "..."
  }
}
```

---

## 7. Security

### 7.1 Authentication

- Agents must authenticate with the router using API keys
- Each agent has a unique agent ID and secret
- Messages are signed with HMAC-SHA256

### 7.2 Authorization

- Agents can only send messages to allowed targets
- Broadcast permissions can be restricted
- Capability queries respect privacy settings

### 7.3 Message Integrity

```
Signature = HMAC-SHA256(
  key: agent_secret,
  data: message.id + message.timestamp + JSON.stringify(message.payload)
)
```

---

## 8. Implementation Guide

### 8.1 Agent SDK (Pseudo-code)

```javascript
class A2AClient {
  constructor(agentId, routerEndpoint, options = {}) {
    this.agentId = agentId;
    this.router = routerEndpoint;
    this.handlers = new Map();
    this.pending = new Map();
  }

  // Register with router
  async register(capabilities) {
    await this.send({
      type: 'REGISTER',
      to: 'router',
      payload: { agentId: this.agentId, capabilities }
    });
    this.startHeartbeat();
  }

  // Send message
  async send(message) {
    message.from = this.agentId;
    message.id = generateUUID();
    message.timestamp = Date.now();
    return this.transport.send(message);
  }

  // Send task and wait for result
  async call(targetAgent, task, options = {}) {
    const correlationId = generateUUID();
    const message = {
      type: 'TASK',
      to: targetAgent,
      priority: options.priority || 'NORMAL',
      payload: task,
      metadata: {
        correlationId,
        timeout: options.timeout || 30000
      }
    };

    return new Promise((resolve, reject) => {
      this.pending.set(correlationId, { resolve, reject });
      this.send(message);
      
      setTimeout(() => {
        this.pending.delete(correlationId);
        reject(new Error('Timeout'));
      }, options.timeout || 30000);
    });
  }

  // Subscribe to messages
  on(type, handler) {
    this.handlers.set(type, handler);
  }

  // Handle incoming message
  handleMessage(message) {
    // Handle response to pending request
    if (message.metadata?.correlationId) {
      const pending = this.pending.get(message.metadata.correlationId);
      if (pending) {
        pending.resolve(message.payload);
        this.pending.delete(message.metadata.correlationId);
        return;
      }
    }

    // Handle with registered handler
    const handler = this.handlers.get(message.type);
    if (handler) {
      handler(message);
    }
  }
}
```

---

## 9. Appendix

### 9.1 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-27 | Initial specification |

### 9.2 References

- [MCP Specification](https://modelcontextprotocol.io/)
- [OpenViking Documentation](https://github.com/1yibiao/OpenViking)
- [Multi-Agent Memory Mesh Design](../plans/2026-03-27-multi-agent-memory-mesh-implementation.md)

---

**Status:** ✅ Task 2.1 Complete — A2A Protocol v1.0 Specified
