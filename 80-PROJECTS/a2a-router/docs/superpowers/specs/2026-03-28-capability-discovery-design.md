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
- `subscriptions: Map<capability, Set<agentId>>` — capability → subscribers (inverted subscription index)
- `router: A2ARouter` — reference to router for event emission

**Methods:**
- `register(agentId, capabilities)` — update index, emit `capability:added` via router
- `unregister(agentId)` — remove from index + clean subscriptions, emit `capability:removed`
- `updateCapabilities(agentId, newCapabilities)` — diff and emit `capability:updated`
- `match(query, options)` — weighted scoring + hard filter by loadThreshold, return top-N
- `subscribe(agentId, capabilities)` — add to subscription index (capability → Set<agentId>)
- `unsubscribe(agentId, capabilities)` — remove from subscription index
- `notifySubscribers(capability, event)` — emit `message:deliver` to all subscribers

### 2.2 Router Changes

**File:** `src/router.js`

**Changes:**
- Add `this.capabilityRegistry = new CapabilityRegistry(this)`
- In `registerAgent()`: call `capabilityRegistry.register()`
- In `unregisterAgent()`: call `capabilityRegistry.unregister()` (handles subscription cleanup)
- Extend `heartbeat()`: recompute scores on load change (optional, for display only)
- New method: `matchBestAgent(query, constraints)` — delegate to registry with load awareness
- New method: `subscribeCapabilities(agentId, capabilities)` — add subscription
- New method: `unsubscribeCapabilities(agentId, capabilities)` — remove subscription
- New method: `updateAgentCapabilities(agentId, capabilities)` — call registry.updateCapabilities()

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
      agentId: { type: 'string', description: 'Agent subscribing (must be the requesting agent)' },
      capabilities: { type: 'array', items: { type: 'string' } }
    },
    required: ['agentId', 'capabilities']
  },
  note: 'Validation: agentId must match the authenticated requesting agent to prevent subscription spoofing'
},
{
  name: 'a2a_match_agent',
  description: 'Find best agent by capabilities with load scoring',
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Capability to search for' },
      loadThreshold: { type: 'number', default: 0.9, description: 'Max load to consider (hard filter)' },
      limit: { type: 'number', default: 5, description: 'Max results' }
    },
    required: ['query']
  },
  returns: {
    success: true,
    matches: [
      { agentId: 'coder', score: 9, capabilities: ['coding'], status: 'idle', load: 0.2 },
      ...
    ]
  }
},
{
  name: 'a2a_update_agent_capabilities',
  description: 'Update an agent capabilities after initial registration',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string', description: 'Agent to update' },
      capabilities: { type: 'array', items: { type: 'string' } }
    },
    required: ['agentId', 'capabilities']
  }
}
```

### 2.4 Event Types

**New events emitted by router:**
- `capability:added` — `{ agentId, capabilities[] }` — emitted when agent registers or updates capabilities
- `capability:removed` — `{ agentId, capabilities[] }` — emitted on unregister or capability removal
- `capability:updated` — `{ agentId, oldCapabilities[], newCapabilities[] }` — emitted on capability changes

**Note:** Events are emitted via the router's EventEmitter. CapabilityRegistry stores a reference to the router and calls `router.emit()` for propagation to MCP transport layer.

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

**Score = matchScore + recencyBonus - (load × 10)**

| Factor | Weight | Description |
|--------|--------|-------------|
| exactMatch | 10 | capability === query |
| prefixMatch | 5 | capability.startsWith(query) |
| containsMatch | 3 | capability.includes(query) |
| loadPenalty | -load * 10 | Lower load = higher score |
| recencyBonus | +1 | If `lastHeartbeat` within last 30s, else 0; fallback to `registeredAt` if no heartbeat |

**Threshold semantics:** `loadThreshold` is a **hard filter** — agents with load > threshold are excluded entirely from results. `match()` returns top-N results sorted by score descending.

**Edge cases:**
- Agent with no `lastHeartbeat`: use `registeredAt` for recency bonus
- Agent with load=0.9 and threshold=0.9: included (exact match on boundary)
- Agent with load=0.91 and threshold=0.9: excluded (above threshold)

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
| `src/protocols/capability-registry.js` | Create — CapabilityRegistry class |
| `src/router.js` | Modify — add registry, matchBestAgent, subscribeCapabilities |
| `src/server.js` | Modify — add 3 new MCP tools |
| `test/unit/capability-registry.test.js` | Create |
| `test/unit/router-discovery.test.js` | Create |
| `test/integration/capability-discovery.test.js` | Create |

## 8. Implementation Notes

- **Cleanup on unregister:** `CapabilityRegistry.unregister()` removes agent from `capabilityIndex` AND iterates `subscriptions` to remove agent from all subscribed capability sets.
- **No `agentScores` cache:** Scores computed on-the-fly in `match()`, no persistent caching.
- **Subscriptions inverted index:** `subscriptions` maps `capability → Set<agentId>` (not agent → capabilities) for O(1) broadcast lookup.
- **Offline subscriber handling:** `notifySubscribers()` checks if subscriber exists in router.agents and status !== 'offline' before emitting `message:deliver`. Silently skips offline/dead subscribers — no error emitted.
- **Partial update failure:** If emit fails mid-update (e.g., transport error), continue with remaining subscribers. No rollback — events are fire-and-forget.
