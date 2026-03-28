# Agent Load Balancing — a2a-router

**Date**: 2026-03-28
**Feature**: Agent Load Balancing for Capability-Based Routing
**Status**: Approved

---

## 1. Overview

Add load-based routing to a2a-router so when messages specify a capability requirement (not a specific agent ID), the router selects the least-loaded agent with matching capability. Leverages existing `agent.load` from heartbeats and `QueueMonitor` data. No external dependencies.

---

## 2. Architecture

### Key Insight

Current `directRoute()` routes by `message.to` (agent ID). This feature adds a new routing mode: when `message.to` is a capability keyword, use load-aware capability matching.

### Components

- **LoadBalancer** class (`src/protocols/load-balancing/load-balancer.js`) — scores agents by load
- **Enhanced `matchBestAgent()`** — integrates load scoring into existing capability matching
- **New MCP tool `a2a_get_agent_loads`** — exposes current load scores

### File Structure

```
src/
├── protocols/
│   ├── capability-registry.js      # MODIFY: enhance match() with load scores
│   ├── monitoring/
│   │   └── queue-monitor.js       # existing
│   └── load-balancing/            # NEW
│       └── load-balancer.js       # NEW: LoadBalancer class
├── router.js                       # MODIFY: add selectByCapability()
└── server.js                      # MODIFY: add a2a_get_agent_loads tool
test/
├── unit/
│   ├── load-balancer.test.js      # NEW
│   └── capability-registry.test.js # MODIFY: add load scoring tests
└── integration/
    └── load-balancing.test.js     # NEW
```

---

## 3. Routing Flow

### New Message Format (Capability-Based)

```javascript
// When message.to is a capability keyword:
{
  id: 'msg-123',
  type: 'TASK',
  to: 'capability:coding',  // routing by capability
  from: 'alice',
  payload: { task: 'build feature' }
}
```

### Routing Logic

```
routeMessage(message)
    │
    ├─ to === 'broadcast' → broadcast()
    ├─ to === 'router' → handleRouterMessage()
    ├─ to.startsWith('capability:') → capabilityRoute()  [NEW]
    └─ to is agentId → directRoute() [existing]
```

### `capabilityRoute()` Implementation

```javascript
capabilityRoute(message) {
  const capability = message.to.replace('capability:', '');

  // Find best agent by capability using enhanced matching
  const matches = this.capabilityRegistry.match(capability, {
    loadThreshold: 1.0,  // Don't filter by load in match
    limit: 10
  });

  if (matches.length === 0) {
    // No agents available, queue it
    this.enqueue(message);
    return { success: true, queued: true, reason: 'NO_AGENTS_FOR_CAPABILITY' };
  }

  // Select agent with best load score (matches are already sorted by score)
  const best = matches[0];
  const agent = this.agents.get(best.agentId);

  if (agent.status === 'offline') {
    this.enqueue(message);
    return { success: true, queued: true, reason: 'AGENT_OFFLINE' };
  }

  return this.deliver(message, agent);
}
```

---

## 4. Enhanced CapabilityRegistry.match()

The existing `match()` already factors in `agent.load`. This spec clarifies the formula and adds tie-breaking.

### Existing Formula (lines 95-128)

```javascript
score = matchScore + recencyBonus - (agent.load * 10);
// matchScore: exact=10, prefix=5, contains=3
// recencyBonus: +1 if heartbeat within 30s
// agent.load: 0-1 from heartbeat
```

### Score Range

| Component | Range | Notes |
|----------|-------|-------|
| matchScore | 3-10 | capability match quality |
| recencyBonus | 0-1 | recency of heartbeat |
| load penalty | 0-10 | `agent.load * 10` |

### Tie-Breaking

When scores tie, prefer agent with:
1. Lower `load` value (less busy)
2. More recent heartbeat (higher `lastHeartbeat`)

---

## 5. LoadBalancer Class

For external load querying and MCP tool support.

```javascript
export class LoadBalancer {
  constructor(router) {
    this.router = router;
  }

  // Get load scores for all agents or filtered by capability
  getAgentLoads(capability = null) {
    const agents = [];

    for (const [agentId, agent] of this.router.agents) {
      if (capability && !agent.capabilities.has(capability)) continue;

      const queueStats = this.getQueueStatsForAgent(agentId);
      const score = this.calculateScore(agent, queueStats);

      agents.push({
        id: agentId,
        capabilities: Array.from(agent.capabilities),
        status: agent.status,
        load: agent.load,
        queueSize: queueStats.size,
        avgWaitTime: queueStats.avgWaitTime,
        score
      });
    }

    return agents.sort((a, b) => b.score - a.score);
  }

  calculateScore(agent, queueStats) {
    const queueScore = Math.max(0, 100 - queueStats.size);
    const statusScore = agent.status === 'idle' ? 100 : 50;
    const loadScore = (1 - agent.load) * 100;

    return queueScore * 0.3 + statusScore * 0.2 + loadScore * 0.5;
  }

  getQueueStatsForAgent(agentId) {
    // Returns aggregate queue stats for messages destined to this agent
    // For now, return global queue stats (per-priority is too granular)
    return this.router.queueMonitor.getQueueStats();
  }
}
```

---

## 6. MCP Tools

### a2a_get_agent_loads

```javascript
{
  name: 'a2a_get_agent_loads',
  description: 'Get load scores for all registered agents',
  inputSchema: {
    type: 'object',
    properties: {
      capability: {
        type: 'string',
        description: 'Filter agents by capability'
      }
    }
  }
}
```

Returns:
```javascript
{
  success: true,
  agents: [
    {
      id: 'alice',
      capabilities: ['coding', 'review'],
      status: 'idle',
      load: 0.3,
      queueSize: 5,
      avgWaitTime: 1200,
      score: 72.5
    }
  ]
}
```

---

## 7. Edge Cases

| Scenario | Behavior |
|----------|----------|
| No agents with capability | Message queued |
| All matching agents offline | Message queued |
| All queues full | Message dropped |
| Tie in score | Lower load wins, then recent heartbeat |
| Single agent | Always select it |

---

## 8. Tech Notes

- **No external dependencies** — pure Node.js
- **Reuses existing `match()`** — capabilityRegistry.match() already factors in load
- **Minimal new code** — mostly wiring existing components
- **Backward compatible** — existing agent-ID routing unchanged
