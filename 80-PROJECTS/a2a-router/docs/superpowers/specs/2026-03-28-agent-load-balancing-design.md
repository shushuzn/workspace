# Agent Load Balancing — a2a-router

**Date**: 2026-03-28
**Feature**: Agent Load Balancing for Task Routing
**Status**: Approved

---

## 1. Overview

Add load-based routing to a2a-router so tasks are intelligently dispatched to the least-loaded agent with matching capabilities. Leverages the existing QueueMonitor data for routing decisions. No external dependencies.

---

## 2. Architecture

### Components

- **LoadBalancer** class (`src/protocols/load-balancing/load-balancer.js`) — scores agents by queue stats
- **Modified `directRoute()`** in `src/router.js` — uses LoadBalancer for target selection
- **New MCP tool `a2a_get_agent_loads`** — exposes current load scores

### File Structure

```
src/
├── protocols/
│   ├── capability-registry.js      # existing
│   ├── monitoring/
│   │   └── queue-monitor.js       # existing (QueueMonitor)
│   └── load-balancing/            # NEW
│       └── load-balancer.js       # NEW: LoadBalancer class
├── router.js                       # MODIFY: directRoute uses LoadBalancer
└── server.js                      # MODIFY: add a2a_get_agent_loads tool
test/
├── unit/
│   ├── load-balancer.test.js      # NEW
│   └── router-monitoring.test.js   # existing
└── integration/
    └── load-balancing.test.js     # NEW
```

---

## 3. LoadBalancer Class

```javascript
class LoadBalancer {
  constructor(router) {
    this.router = router;
  }

  // Returns agents sorted by load score (highest first)
  rankAgentsByLoad(capability) {
    const agents = this.getAgentsWithCapability(capability);
    const stats = this.router.queueMonitor.getQueueStats();

    return agents
      .map(agent => ({
        agent,
        score: this.calculateScore(agent, stats)
      }))
      .sort((a, b) => b.score - a.score);
  }

  calculateScore(agent, stats) {
    const queueStats = stats.queues;
    const agentQueueSize = this.getAgentQueueSize(agent.id, queueStats);
    const agentWaitTime = this.getAgentWaitTime(agent.id, queueStats);

    // Score components (0-100 each)
    const queueScore = Math.max(0, 100 - agentQueueSize);
    const waitScore = Math.max(0, 100 - (agentWaitTime / 100));
    const statusScore = agent.status === 'idle' ? 100 : 50;

    // Weighted average
    return queueScore * 0.5 + waitScore * 0.3 + statusScore * 0.2;
  }

  selectBestAgent(capability) {
    const ranked = this.rankAgentsByLoad(capability);
    return ranked.length > 0 ? ranked[0].agent : null;
  }
}
```

### Scoring Formula

| Component | Weight | Calculation |
|----------|--------|-------------|
| Queue Size | 50% | `100 - min(queueSize, 100)` |
| Avg Wait Time | 30% | `100 - min(avgWaitTime / 100, 100)` |
| Status | 20% | `idle=100, busy=50` |

---

## 4. Routing Integration

### Modified `directRoute()`

```javascript
directRoute(message) {
  const targetAgents = this.findAgentsByCapability(message.targetCapability);

  if (targetAgents.length === 0) {
    return { success: false, error: 'NO_AGENTS_FOR_CAPABILITY' };
  }

  // Use LoadBalancer to select best agent
  const bestAgent = this.loadBalancer.selectBestAgent(message.targetCapability);

  if (!bestAgent || bestAgent.status === 'offline') {
    this.enqueue(message);
    return { success: true, queued: true };
  }

  return this.deliver(message, bestAgent);
}
```

---

## 5. MCP Tools

### a2a_get_agent_loads

```javascript
{
  name: 'a2a_get_agent_loads',
  description: 'Get load scores for all registered agents',
  inputSchema: {
    type: 'object',
    properties: {
      capability: { type: 'string', description: 'Filter by capability' }
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
      score: 85.4
    },
    // ...
  ]
}
```

---

## 6. Data Flow

```
Agent heartbeat → updates agent.load → routeMessage called
                                            ↓
                          LoadBalancer ranks by queue stats
                                            ↓
                        Select best agent, deliver or enqueue
```

---

## 7. Edge Cases

| Scenario | Behavior |
|----------|----------|
| All agents offline | Message queued |
| No agents with capability | Message queued to default |
| All queues full | Message dropped, stats.messagesDropped++ |
| Single agent | Always select that agent |
| Tie in score | Select by smallest queue size |

---

## 8. Tech Notes

- **No external dependencies** — pure Node.js
- **Synchronous scoring** — no async overhead
- **Leverages QueueMonitor** — existing data reused, no duplication
- **Thread-safe** — single-threaded JS, no locks needed
