# Agent Load Balancing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add capability-based routing with load balancing — when `message.to` starts with `capability:`, route to the least-loaded matching agent.

**Architecture:** Add `capabilityRoute()` to router using existing `CapabilityRegistry.match()` (already has load-based scoring). New `LoadBalancer` class exposes load scores via MCP tool. Tie-breaking added to match() for score ties.

**Tech Stack:** Node.js (no deps), Jest ES modules, existing codebase patterns

---

## File Structure

```
src/
├── protocols/
│   ├── capability-registry.js      # MODIFY: add tie-breaking to match()
│   ├── monitoring/
│   │   └── queue-monitor.js       # existing
│   └── load-balancing/            # NEW
│       └── load-balancer.js       # NEW: LoadBalancer class
├── router.js                       # MODIFY: add capabilityRoute()
└── server.js                      # MODIFY: add a2a_get_agent_loads tool
test/
├── unit/
│   ├── load-balancer.test.js      # NEW
│   └── capability-registry.test.js # MODIFY: add tie-breaking tests
└── integration/
    └── load-balancing.test.js     # NEW
```

---

## Task 1: Add Tie-Breaking to CapabilityRegistry.match()

**Files:**
- Modify: `src/protocols/capability-registry.js:128` (sort line)
- Test: `test/unit/capability-registry.test.js`

- [ ] **Step 1: Write failing test — tie-breaking prefers lower load**

```javascript
test('match() tie-breaking prefers lower load', () => {
  // Register two agents with same capability
  router.registerAgent('alice', ['coding']);
  router.registerAgent('bob', ['coding']);

  // Set same heartbeat time but different loads
  router.heartbeat('alice', 'idle', 0.2, 0); // load=0.2
  router.heartbeat('bob', 'idle', 0.8, 0);    // load=0.8

  const matches = registry.match('coding', { loadThreshold: 1.0, limit: 5 });
  expect(matches[0].agentId).toBe('alice'); // lower load wins
  expect(matches[1].agentId).toBe('bob');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/capability-registry.test.js --testNamePattern="tie-breaking"`
Expected: FAIL — alice is not first (sort is by score only)

- [ ] **Step 3: Write failing test — tie-breaking prefers recent heartbeat**

```javascript
test('match() tie-breaking prefers recent heartbeat', () => {
  router.registerAgent('alice', ['coding']);
  router.registerAgent('bob', ['coding']);

  // Same load, but bob's heartbeat is more recent
  router.heartbeat('alice', 'idle', 0.5, 0);
  router.heartbeat('bob', 'idle', 0.5, 0);

  // Bob's heartbeat is more recent
  const bob = router.agents.get('bob');
  bob.lastHeartbeat = Date.now() + 1000;

  const matches = registry.match('coding', { loadThreshold: 1.0, limit: 5 });
  expect(matches[0].agentId).toBe('bob'); // more recent wins
});
```

- [ ] **Step 4: Run test to verify it fails**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/capability-registry.test.js --testNamePattern="recent heartbeat"`
Expected: FAIL — bob is not first

- [ ] **Step 5: Implement tie-breaking in match() sort**

Find line 128 in `src/protocols/capability-registry.js`:
```javascript
return scored.sort((a, b) => b.score - a.score).slice(0, limit);
```

Replace with:
```javascript
return scored.sort((a, b) => {
  if (b.score !== a.score) return b.score - a.score;
  if (a.load !== b.load) return a.load - b.load;        // lower load wins
  return (b.lastHeartbeat || 0) - (a.lastHeartbeat || 0); // more recent wins
}).slice(0, limit);
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/capability-registry.test.js --testNamePattern="tie-breaking"`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/protocols/capability-registry.js test/unit/capability-registry.test.js
git commit -m "feat(capability-registry): add tie-breaking to match()

- Sort by score desc, then load asc, then lastHeartbeat desc
- Lower load wins ties, then more recent heartbeat"
```

---

## Task 2: LoadBalancer Class

**Files:**
- Create: `src/protocols/load-balancing/load-balancer.js`
- Test: `test/unit/load-balancer.test.js`

- [ ] **Step 1: Write failing test — LoadBalancer initializes**

```javascript
import { LoadBalancer } from '../../src/protocols/load-balancing/load-balancer.js';

describe('LoadBalancer', () => {
  let router;
  let loadBalancer;

  beforeEach(() => {
    router = {
      agents: new Map(),
      queueMonitor: { getQueueStats: () => ({ queues: { CRITICAL: { size: 0 }, HIGH: { size: 0 }, NORMAL: { size: 5 }, LOW: { size: 0 } } }) }
    };
    loadBalancer = new LoadBalancer(router);
  });

  test('initializes with router reference', () => {
    expect(loadBalancer.router).toBe(router);
  });

  test('getAgentLoads returns empty for no agents', () => {
    const result = loadBalancer.getAgentLoads();
    expect(result).toEqual([]);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/load-balancer.test.js`
Expected: FAIL — LoadBalancer not found

- [ ] **Step 3: Create LoadBalancer class**

```javascript
// src/protocols/load-balancing/load-balancer.js
export class LoadBalancer {
  constructor(router) {
    this.router = router;
  }

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
    const stats = this.router.queueMonitor.getQueueStats();
    const totalSize = Object.values(stats.queues).reduce((sum, q) => sum + q.size, 0);
    const totalWait = Object.values(stats.queues).reduce((sum, q) => sum + (q.avgWaitTime * q.size), 0);
    return {
      size: totalSize,
      avgWaitTime: totalSize > 0 ? Math.round(totalWait / totalSize) : 0
    };
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/load-balancer.test.js`
Expected: PASS

- [ ] **Step 5: Write failing test — getAgentLoads filters by capability**

```javascript
test('getAgentLoads filters by capability', () => {
  router.agents.set('alice', { id: 'alice', capabilities: new Set(['coding', 'review']), status: 'idle', load: 0.3, lastHeartbeat: Date.now() });
  router.agents.set('bob', { id: 'bob', capabilities: new Set(['review']), status: 'idle', load: 0.5, lastHeartbeat: Date.now() });

  const result = loadBalancer.getAgentLoads('coding');
  expect(result.length).toBe(1);
  expect(result[0].id).toBe('alice');
});
```

- [ ] **Step 6: Run test to verify it fails**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/load-balancer.test.js --testNamePattern="filters by capability"`
Expected: FAIL — capability check uses Set.has()

- [ ] **Step 7: Fix capability check**

In `getAgentLoads()`, change:
```javascript
if (capability && !agent.capabilities.has(capability)) continue;
```

To check if any capability contains the query:
```javascript
if (capability && !Array.from(agent.capabilities).some(c => c.toLowerCase().includes(capability.toLowerCase()))) continue;
```

- [ ] **Step 8: Run test to verify it passes**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/load-balancer.test.js --testNamePattern="filters by capability"`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add src/protocols/load-balancing/load-balancer.js test/unit/load-balancer.test.js
git commit -m "feat(load-balancing): add LoadBalancer class

- getAgentLoads() returns agents sorted by score
- calculateScore() weights queue, status, and load
- Filters by capability when specified"
```

---

## Task 3: capabilityRoute() in Router

**Files:**
- Modify: `src/router.js` (add capabilityRoute, modify routeMessage)
- Test: `test/unit/capability-routing.test.js` (create new)

- [ ] **Step 1: Write failing test — capabilityRoute() selects best agent**

First, create `test/unit/capability-routing.test.js` with the test:

```javascript
import { A2ARouter } from '../../src/router.js';

describe('Capability Routing', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
  });

  test('capabilityRoute() routes to best matching agent', () => {
  router.registerAgent('alice', ['coding']);
  router.registerAgent('bob', ['coding']);
  router.heartbeat('alice', 'idle', 0.2, 0); // lower load
  router.heartbeat('bob', 'idle', 0.8, 0);    // higher load

  const msg = {
    id: 'test-1',
    type: 'TASK',
    priority: 'NORMAL',
    from: 'tester',
    to: 'capability:coding',
    timestamp: Date.now(),
    payload: { task: 'build feature' }
  };

  const result = router.routeMessage(msg);
  expect(result.delivered).toBe(true);
  expect(result.agent).toBe('alice'); // lower load wins
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/capability-routing.test.js`
Expected: FAIL — capabilityRoute not defined

- [ ] **Step 3: Add capabilityRoute() to router**

Add after `directRoute()` method in `src/router.js`:

```javascript
/**
 * Route message by capability requirement
 */
capabilityRoute(message) {
  const capability = message.to.replace('capability:', '');

  // Find best agent by capability using existing match()
  const matches = this.capabilityRegistry.match(capability, {
    loadThreshold: 1.0,  // Don't filter by load in match, we want options
    limit: 10
  });

  if (matches.length === 0) {
    this.enqueue(message);
    return { success: true, queued: true, reason: 'NO_AGENTS_FOR_CAPABILITY' };
  }

  // Select agent with best score (matches are already sorted)
  const best = matches[0];
  const agent = this.agents.get(best.agentId);

  if (!agent || agent.status === 'offline') {
    this.enqueue(message);
    return { success: true, queued: true, reason: 'AGENT_OFFLINE' };
  }

  return this.deliver(message, agent);
}
```

- [ ] **Step 4: Modify routeMessage() to detect capability routing**

Find in `routeMessage()`:
```javascript
if (message.to === 'broadcast') {
  return this.broadcast(message);
} else if (message.to === 'router') {
  return this.handleRouterMessage(message);
} else {
  return this.directRoute(message);
}
```

Replace `else` clause:
```javascript
} else if (message.to.startsWith('capability:')) {
  return this.capabilityRoute(message);
} else {
  return this.directRoute(message);
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/capability-routing.test.js --testNamePattern="capabilityRoute"`
Expected: PASS

- [ ] **Step 6: Write failing test — queues when no agents available**

Add to `test/unit/capability-routing.test.js`:

```javascript
test('capabilityRoute() queues when no agents match', () => {
  router.registerAgent('alice', ['review']); // no coding capability

  const msg = {
    id: 'test-2',
    type: 'TASK',
    priority: 'NORMAL',
    from: 'tester',
    to: 'capability:coding',
    timestamp: Date.now(),
    payload: { task: 'build feature' }
  };

  const result = router.routeMessage(msg);
  expect(result.queued).toBe(true);
  expect(result.reason).toBe('NO_AGENTS_FOR_CAPABILITY');
});
```

- [ ] **Step 7: Run test to verify it passes**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/capability-routing.test.js --testNamePattern="queues when no agents"`
Expected: PASS

- [ ] **Step 8: Write failing test — queues when agent offline**

Add to `test/unit/capability-routing.test.js`:

```javascript
test('capabilityRoute() queues when matching agent offline', () => {
  router.registerAgent('alice', ['coding']);
  router.agents.get('alice').status = 'offline';

  const msg = {
    id: 'test-3',
    type: 'TASK',
    priority: 'NORMAL',
    from: 'tester',
    to: 'capability:coding',
    timestamp: Date.now(),
    payload: { task: 'build feature' }
  };

  const result = router.routeMessage(msg);
  expect(result.queued).toBe(true);
  expect(result.reason).toBe('AGENT_OFFLINE');
});
```

- [ ] **Step 9: Run test to verify it passes**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/capability-routing.test.js --testNamePattern="queues when matching agent offline"`
Expected: PASS

- [ ] **Step 10: Commit**

```bash
git add src/router.js test/unit/capability-routing.test.js
git commit -m "feat(router): add capabilityRoute() for capability-based routing

- routeMessage() detects to.startsWith('capability:') pattern
- capabilityRoute() uses CapabilityRegistry.match() for load-aware selection
- Queues message when no agents available or agent offline"
```

---

## Task 4: MCP Tool a2a_get_agent_loads

**Files:**
- Modify: `src/server.js` (add tool definition and handler)
- Create: `test/integration/mcp-loads.test.js`

- [ ] **Step 1: Write failing test — tool definition exists**

Create `test/integration/mcp-loads.test.js`:

```javascript
test('a2a_get_agent_loads tool is registered', async () => {
  const tools = await server.handleRequest({ method: 'tools/list' }, { onerror: () => {} });
  const toolNames = tools.tools.map(t => t.name);
  expect(toolNames).toContain('a2a_get_agent_loads');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/integration/mcp-loads.test.js --testNamePattern="a2a_get_agent_loads tool is registered"`
Expected: FAIL — tool not in list

- [ ] **Step 3: Add tool definition to TOOLS array**

Add after the `a2a_update_agent_capabilities` tool definition in `src/server.js`:

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

- [ ] **Step 4: Add handler in switch statement**

Add case after `a2a_update_agent_capabilities`:

```javascript
case 'a2a_get_agent_loads': {
  const { capability } = args;
  const loadBalancer = new LoadBalancer(router);
  const agents = loadBalancer.getAgentLoads(capability || null);
  return {
    content: [{
      type: 'text',
      text: JSON.stringify({ success: true, agents }, null, 2)
    }]
  };
}
```

- [ ] **Step 5: Add import for LoadBalancer at top of file**

Add after existing imports:
```javascript
import { LoadBalancer } from './protocols/load-balancing/load-balancer.js';
```

- [ ] **Step 6: Run test to verify it passes**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/integration/mcp-loads.test.js --testNamePattern="a2a_get_agent_loads tool is registered"`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/server.js test/integration/mcp-loads.test.js
git commit -m "feat(server): add a2a_get_agent_loads MCP tool

- Returns load scores for all agents or filtered by capability
- Uses LoadBalancer.getAgentLoads() for scoring"
```

---

## Task 5: Integration Test

**Files:**
- Create: `test/integration/load-balancing.test.js`

- [ ] **Step 1: Write integration test — end-to-end capability routing**

```javascript
test('end-to-end: capability routing selects lowest load agent', () => {
  const router = new A2ARouter({ heartbeatTimeout: 60000 });

  // Register agents with different loads
  router.registerAgent('agent-a', ['coding']);
  router.registerAgent('agent-b', ['coding']);
  router.registerAgent('agent-c', ['review']);

  router.heartbeat('agent-a', 'idle', 0.1, 0); // lowest load
  router.heartbeat('agent-b', 'idle', 0.9, 0); // highest load
  router.heartbeat('agent-c', 'idle', 0.2, 0);

  // Deliver a capability-based message
  const msg = {
    id: 'e2e-1',
    type: 'TASK',
    priority: 'NORMAL',
    from: 'coordinator',
    to: 'capability:coding',
    timestamp: Date.now(),
    payload: { task: 'implement feature' }
  };

  let deliveredTo = null;
  router.on('message:deliver', (message, agent) => {
    deliveredTo = agent.id;
  });

  const result = router.routeMessage(msg);
  expect(result.delivered).toBe(true);
  expect(deliveredTo).toBe('agent-a'); // lowest load selected
});
```

- [ ] **Step 2: Run test to verify it passes**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/integration/load-balancing.test.js`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add test/integration/load-balancing.test.js
git commit -m "test(integration): add load balancing end-to-end test"
```

---

## Final Verification

Run all tests:
```bash
node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/ --silent
```

Expected: All tests pass (46+ total)

Verify server starts:
```bash
timeout 5 node --experimental-vm-modules src/server.js 2>&1 | head -20
```

Expected: "Tools available:" includes "a2a_get_agent_loads"
