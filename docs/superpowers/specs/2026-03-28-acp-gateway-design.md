# ACP Gateway Integration Design

**Date:** 2026-03-28
**Project:** 80-PROJECTS/a2a-router
**Type:** Protocol Integration
**Status:** Draft

## Context

GitHub trending repo `agentclientprotocol/agent-client-protocol` defines a standard protocol for connecting editors to agents. The `a2a-router` project implements agent-to-agent routing with registry, priority queues, and message routing. This design proposes integrating ACP as a protocol adapter layer.

## Problem Statement

The `a2a-router` currently uses a proprietary message format. As the ACP standard emerges, there's an opportunity to make `a2a-router` ACP-compatible, enabling it to route messages between:
- ACP-native agents (editors, IDEs)
- Existing A2A agents

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  A2A Router                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Registry │  │  Queues  │  │ Messages │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       └────────────┴────────────┘                       │
│                    │                                     │
│              ┌─────▼─────┐                              │
│              │  Router   │                              │
│              └─────┬─────┘                              │
└────────────────────┼────────────────────────────────────┘
                     │
              ┌──────▼──────┐
              │ ACP Gateway │  ← NEW: ACP adapter layer
              └──────┬──────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   Editor/CLI   ACP Agent   ACP Registry
```

## Components

### 1. ACPGateway

**File:** `src/protocols/acp-gateway.js`

**Responsibility:**
- Bidirectional protocol translation (ACP ↔ A2A)
- Agent identity mapping (ACP ID ↔ internal ID)
- Message format conversion

**API:**
```javascript
class ACPGateway extends EventEmitter {
  constructor(a2aRouter)  // injected dependency

  // ACP → A2A
  handleACPMessage(acpMessage, agentId)

  // A2A → ACP
  sendToACP(a2aMessage, acpAgentId)

  // Lifecycle
  start()
  stop()
}
```

### 2. ACPParser

**File:** `src/protocols/acp-parser.js`

**Responsibility:**
- Parse ACP JSON-RPC 2.0 messages
- Serialize A2A messages to ACP format
- Validate required fields

**ACP Message Schema:**
```json
{
  "jsonrpc": "2.0",
  "method": "agent.request",
  "params": {
    "capabilities": ["code-completion", "refactor"],
    "metadata": { "priority": "HIGH" }
  },
  "id": "msg-uuid"
}
```

### 3. ACPAgentAdapter

**File:** `src/protocols/acp-adapter.js`

**Responsibility:**
- Register ACP agents in A2A registry
- Translate ACP capabilities array ↔ A2A Set
- Translate ACP heartbeat ↔ A2A heartbeat

**Mapping:**
| ACP Field | A2A Field | Notes |
|-----------|------------|-------|
| `agent.id` | `AgentInfo.id` | Direct map |
| `capabilities[]` | `AgentInfo.capabilities` | Array ↔ Set |
| `metadata.priority` | Queue selection | Map to CRITICAL/HIGH/NORMAL/LOW |
| heartbeat | heartbeat | Translate interval |

## Data Flow

### Flow 1: ACP Agent → A2A Agent

```
ACP JSON-RPC Message
    ↓
ACPGateway.handleACPMessage()
    ↓
ACPParser.parse() → Internal Message
    ↓
A2A Router.route() → Target Agent
    ↓
Agent receives internal message
```

### Flow 2: A2A Agent → ACP Agent

```
Internal result message
    ↓
ACPGateway.sendToACP()
    ↓
ACPParser.toACP() → ACP JSON-RPC Response
    ↓
External ACP agent receives response
```

## Protocol Translation Rules

### Message ID
- ACP uses string UUIDs
- A2A uses incremental integers
- Gateway maintains `idMap: Map<string, number>` for translation

### Capabilities
- ACP: `string[]` (e.g., `["code-completion", "refactor"]`)
- A2A: `Set<string>`
- Direct conversion, no semantic translation

### Priority Mapping
| ACP priority | A2A queue |
|--------------|-----------|
| "URGENT" | CRITICAL |
| "HIGH" | HIGH |
| "NORMAL" | NORMAL |
| "LOW" | LOW |

### Error Handling
- ACP errors → A2A error format
- A2A errors → ACP JSON-RPC error response (`code: -32000`)
- Unknown agent → ACP `method_not_found` response

## Configuration

```javascript
{
  "acpGateway": {
    "enabled": true,
    "port": 7890,           // ACP listener port
    "idMapTTL": 3600,       // seconds to keep ID mapping
    "heartbeatInterval": 30000  // ms
  }
}
```

## Testing

| Test | Description |
|------|-------------|
| `test/acp-parser.test.js` | Parse known ACP messages, verify output |
| `test/acp-gateway.test.js` | Gateway translates message round-trip |
| `test/integration/acp-a2a.test.js` | ACP agent registers → A2A agent sends message |

## Files to Create/Modify

| File | Action |
|------|--------|
| `src/protocols/acp-gateway.js` | Create |
| `src/protocols/acp-parser.js` | Create |
| `src/protocols/acp-adapter.js` | Create |
| `src/router.js` | Modify: add ACPGateway integration |
| `test/acp-parser.test.js` | Create |
| `test/acp-gateway.test.js` | Create |

## Implementation Notes

1. **Dependency Injection**: ACPGateway receives `a2aRouter` instance, doesn't import it directly
2. **Backwards Compatible**: ACP is opt-in via config flag
3. **No Schema Changes**: A2A internal message format unchanged
4. **Graceful Degradation**: If ACP fails to parse, log and drop message

## Success Criteria

- [ ] ACP agents can register with `a2a-router` via ACPGateway
- [ ] Messages flow from ACP agents → A2A agents
- [ ] Responses flow back from A2A → ACP agents
- [ ] All existing A2A functionality unchanged
- [ ] Unit tests pass for ACP parser and gateway
