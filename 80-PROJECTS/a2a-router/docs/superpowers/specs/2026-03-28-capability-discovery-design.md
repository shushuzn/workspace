# Capability Discovery & Broadcast - Design Specification

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add capability change broadcasting and smart matching to the A2A router, enabling agents to receive real-time notifications when capabilities are added/removed/updated.

**Architecture:** Extend the existing EventEmitter-based router with a CapabilityRegistry that maintains a capability-to-agents index, emits change events, and supports weighted scoring for smart agent selection. The system upgrades the existing simple DISCOVER message into a pub/sub model with load-aware matching.

**Tech Stack:** Node.js ES Modules, existing EventEmitter pattern, JSON-RPC 2.0 for MCP layer

---

## 1. Overview

The A2A router currently supports capability-based discovery through a simple substring match in `handleDiscovery()`. This upgrade adds:

- **Capability change events** — agents subscribe to capability topics and receive notifications
- **Smart agent matching** — weighted scoring based on capability match, load, and recency
- **Backward compatibility** — existing `a2a_discover` tool continues to work

---

## 2. Components

### 2.1 CapabilityRegistry

**File:** `src/protocols/capability-registry.js` (new)

Maintains:
- `capabilityIndex: Map<capability, Set<agentId>>` — inverted index for fast lookup
- `subscriptions: Map<agentId, Set<capability>>` — who subscribed to what
- `agentScores: Map<agentId, number>` — last computed match score

**Methods:**
- `register(agentId, capabilities)` — update index, emit `capability:added`
- `unregister(agentId)` — remove from index, emit `capability:removed`
- `updateCapabilities(agentId, newCapabilities)` — diff and emit changes
- `match(query, options)` — weighted scoring: exact match > prefix match > fuzzy, load factor, recency
- `subscribe(agentId, capabilities)` — add to subscription list
- `unsubscribe(agentId, capabilities)` — remove from subscription list
- `broadcast(agentId, event)` — notify all subscribers of capability change

### 2.2 Router Changes

**File:** `src/router.js`

**Changes:**
- Add `this.capabilityRegistry = new CapabilityRegistry(this)`
- In `registerAgent()`: call `capabilityRegistry.register()`
- In `unregisterAgent()`: call `capabilityRegistry.unregister()`
- Extend `heartbeat()`: recompute scores on load change
- New method: `matchBestAgent(query, constraints)` — delegate to registry with load awareness
- New method: `subscribeCapabilities(agentId, capabilities)` — subscription management

### 2.3 MCP Tools

**File:** `src/server.js`

**New tools:**
```javascript
{
  name: 'a2a_subscribe_capabilities',
  description: 'Subscribe to capability change notifications',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string' },
      capabilities: { type: 'array', items: { type: 'string' } }
    },
    required: ['agentId', 'capabilities']
  }
},
{
  name: 'a2a_match_agent',
  description: 'Find best agent by capabilities with load scoring',
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Capability to search for' },
      loadThreshold: { type: 'number', default: 0.9, description: 'Max load to consider' },
      limit: { type: 'number', default: 5, description: 'Max results' }
    },
    required: ['query']
  }
}
```

### 2.4 Event Types

**New events emitted by router:**
- `capability:added` — `{ agentId, capabilities }`
- `capability:removed` — `{ agentId, capabilities }`
- `capability:updated` — `{ agentId, oldCapabilities, newCapabilities }`
- `agent:matched` — `{ requesterId, matchedAgent, score }`

---

## 3. Data Flow

### Registration Flow
```
Agent calls registerAgent(id, [coding, review])
  → Router.registerAgent()
  → CapabilityRegistry.register(id, [coding, review])
  → Update capabilityIndex: { coding: [id], review: [id] }
  → Emit 'capability:added' for each capability
  → Subscribed agents receive notification via 'message:deliver'
```

### Discovery Flow
```
Agent calls a2a_discover({ query: 'code' })
  → Router.handleDiscovery()
  → CapabilityRegistry.match('code')
  → Score each agent: exact match=10, prefix=5, load penalty, recency bonus
  → Return sorted matches
```

### Subscription Flow
```
Agent calls a2a_subscribe_capabilities({ agentId: 'X', capabilities: ['coding'] })
  → Router.subscribeCapabilities('X', ['coding'])
  → CapabilityRegistry.subscribe('X', ['coding'])
  → When agent 'Y' registers with 'coding', agent 'X' gets notified
```

---

## 4. Matching Algorithm

**Score = matchScore - loadPenalty + recencyBonus**

| Factor | Weight | Description |
|--------|--------|-------------|
| exactMatch | 10 | capability === query |
| prefixMatch | 5 | capability.startsWith(query) |
| containsMatch | 3 | capability.includes(query) |
| loadPenalty | -load * 10 | Lower load = higher score |
| recencyBonus | +1 | If agent active in last 30s |

**Example:** Query "code", agents:
- `coder`: exact match + low load (0.2) = 10 - 2 + 1 = **9**
- `code-review`: contains match + high load (0.8) = 3 - 8 + 0 = **-5**

---

## 5. Backward Compatibility

- Existing `a2a_discover` returns same format, now powered by `CapabilityRegistry.match()`
- Existing `handleDiscovery()` delegates to registry
- No breaking changes to message format

---

## 6. Testing

**Unit tests:**
- `test/unit/capability-registry.test.js` — registry methods
- `test/unit/router-discovery.test.js` — discovery delegation

**Integration test:**
- `test/integration/capability-discovery.test.js` — full flow

---

## 7. Files to Create/Modify

| File | Action |
|------|--------|
| `src/protocols/capability-registry.js` | Create |
| `src/router.js` | Modify — add registry, matchBestAgent, subscribeCapabilities |
| `src/server.js` | Modify — add 2 new MCP tools |
| `test/unit/capability-registry.test.js` | Create |
| `test/unit/router-discovery.test.js` | Create |
| `test/integration/capability-discovery.test.js` | Create |
