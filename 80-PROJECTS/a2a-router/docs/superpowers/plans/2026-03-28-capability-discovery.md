# Capability Discovery & Broadcast Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add capability change broadcasting and smart matching to the A2A router.

**Architecture:** Extend the existing EventEmitter-based router with a CapabilityRegistry that maintains a capability-to-agents index, emits change events, and supports weighted scoring for smart agent selection.

**Tech Stack:** Node.js ES Modules, existing EventEmitter pattern, JSON-RPC 2.0 for MCP layer

---

## File Structure

| File | Action |
|------|--------|
| `src/protocols/capability-registry.js` | Create — CapabilityRegistry class |
| `src/router.js` | Modify — add registry, matchBestAgent, subscribe/unsubscribe/update methods |
| `src/server.js` | Modify — add 3 new MCP tools |
| `test/unit/capability-registry.test.js` | Create — registry methods |
| `test/unit/router-discovery.test.js` | Create — discovery delegation |
| `test/integration/capability-discovery.test.js` | Create — full flow |

---

## Task 1: CapabilityRegistry Core

**Files:**
- Create: `src/protocols/capability-registry.js`
- Test: `test/unit/capability-registry.test.js`

- [ ] **Step 1: Write the failing test — constructor and initial state**

```javascript
// test/unit/capability-registry.test.js
import { CapabilityRegistry } from '../../src/protocols/capability-registry.js';
import { A2ARouter } from '../../src/router.js';

describe('CapabilityRegistry', () => {
  let router;
  let registry;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
    registry = new CapabilityRegistry(router);
  });

  test('initializes with empty capabilityIndex', () => {
    expect(registry.capabilityIndex.size).toBe(0);
  });

  test('initializes with empty subscriptions', () => {
    expect(registry.subscriptions.size).toBe(0);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/capability-registry.test.js --no-coverage 2>&1 | head -30
```
Expected: FAIL — "Cannot find module"

- [ ] **Step 3: Write minimal CapabilityRegistry constructor**

```javascript
// src/protocols/capability-registry.js
export class CapabilityRegistry {
  constructor(router) {
    this.router = router;
    this.capabilityIndex = new Map(); // capability -> Set<agentId>
    this.subscriptions = new Map();    // capability -> Set<agentId>
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/capability-registry.test.js --no-coverage 2>&1 | tail -10
```
Expected: PASS

- [ ] **Step 5: Write failing test — register() adds to index**

```javascript
test('register() adds agent capabilities to index', () => {
  registry.register('agent-1', ['coding', 'review']);
  expect(registry.capabilityIndex.get('coding')).toContain('agent-1');
  expect(registry.capabilityIndex.get('review')).toContain('agent-1');
});
```

- [ ] **Step 6: Run test to verify it fails**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/capability-registry.test.js --no-coverage 2>&1 | tail -10
```
Expected: FAIL — "register is not a function"

- [ ] **Step 7: Write register() method**

```javascript
register(agentId, capabilities) {
  for (const cap of capabilities) {
    if (!this.capabilityIndex.has(cap)) {
      this.capabilityIndex.set(cap, new Set());
    }
    this.capabilityIndex.get(cap).add(agentId);
  }
}
```

- [ ] **Step 8: Run test to verify it passes**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/capability-registry.test.js --no-coverage 2>&1 | tail -10
```
Expected: PASS

- [ ] **Step 9: Write failing test — unregister() removes from index**

```javascript
test('unregister() removes agent from index', () => {
  registry.register('agent-1', ['coding']);
  registry.unregister('agent-1');
  const set = registry.capabilityIndex.get('coding');
  expect(set && set.has('agent-1')).toBe(false);
});
```

- [ ] **Step 10: Run test to verify it fails**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/capability-registry.test.js --no-coverage 2>&1 | tail -10
```
Expected: FAIL — "unregister is not a function"

- [ ] **Step 11: Write unregister() method**

```javascript
unregister(agentId) {
  // Remove from capabilityIndex
  for (const [, agents] of this.capabilityIndex) {
    agents.delete(agentId);
  }
  // Clean up subscriptions for this agent
  for (const [, subscribers] of this.subscriptions) {
    subscribers.delete(agentId);
  }
}
```

- [ ] **Step 12: Run test to verify it passes**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/capability-registry.test.js --no-coverage 2>&1 | tail -10
```
Expected: PASS

- [ ] **Step 13: Write failing test — match() returns scored results**

```javascript
test('match() returns scored results sorted by score', () => {
  registry.register('coder', ['coding']);
  registry.register('reviewer', ['code-review']);
  // Simulate agent load via router.agents
  router.agents.get('coder').load = 0.2;
  router.agents.get('reviewer').load = 0.8;

  const results = registry.match('code', { limit: 5 });
  expect(results[0].agentId).toBe('coder'); // exact match + low load
});
```

- [ ] **Step 14: Run test to verify it fails**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/capability-registry.test.js --no-coverage 2>&1 | tail -10
```
Expected: FAIL — "match is not a function"

- [ ] **Step 15: Write match() method**

```javascript
match(query, options = {}) {
  const { loadThreshold = 0.9, limit = 5 } = options;
  const scored = [];

  for (const [capability, agentIds] of this.capabilityIndex) {
    for (const agentId of agentIds) {
      const agent = this.router.agents.get(agentId);
      if (!agent) continue;
      if (agent.load > loadThreshold) continue; // hard filter

      let matchScore = 0;
      if (capability === query) matchScore = 10;
      else if (capability.startsWith(query)) matchScore = 5;
      else if (capability.includes(query)) matchScore = 3;
      else continue;

      const recencyBonus = (Date.now() - agent.lastHeartbeat) < 30000 ? 1 : 0;
      const score = matchScore + recencyBonus - (agent.load * 10);

      scored.push({
        agentId,
        score,
        capabilities: Array.from(agent.capabilities),
        status: agent.status,
        load: agent.load
      });
    }
  }

  return scored.sort((a, b) => b.score - a.score).slice(0, limit);
}
```

- [ ] **Step 16: Run test to verify it passes**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/capability-registry.test.js --no-coverage 2>&1 | tail -10
```
Expected: PASS

- [ ] **Step 17: Write failing test — subscribe() and notifySubscribers()**

```javascript
test('subscribe() adds subscriber and notifySubscribers() delivers message', () => {
  registry.register('provider', ['coding']);
  registry.subscribe('subscriber-1', ['coding']);

  let notified = null;
  router.on('message:deliver', (msg) => { notified = msg; });

  registry.notifySubscribers('coding', { type: 'capability:added', agentId: 'provider', capabilities: ['coding'] });

  expect(notified).not.toBeNull();
  expect(notified.to).toBe('subscriber-1');
});
```

- [ ] **Step 18: Run test to verify it fails**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/capability-registry.test.js --no-coverage 2>&1 | tail -10
```
Expected: FAIL — "subscribe is not a function"

- [ ] **Step 19: Write subscribe() and notifySubscribers() methods**

```javascript
subscribe(agentId, capabilities) {
  for (const cap of capabilities) {
    if (!this.subscriptions.has(cap)) {
      this.subscriptions.set(cap, new Set());
    }
    this.subscriptions.get(cap).add(agentId);
  }
}

notifySubscribers(capability, event) {
  const subscribers = this.subscriptions.get(capability);
  if (!subscribers) return;

  for (const subscriberId of subscribers) {
    const agent = this.router.agents.get(subscriberId);
    if (!agent || agent.status === 'offline') continue;

    const msg = {
      id: crypto.randomUUID(),
      type: 'EVENT',
      priority: 'NORMAL',
      from: 'router',
      to: subscriberId,
      timestamp: Date.now(),
      payload: { event: { capability, ...event } }
    };
    this.router.emit('message:deliver', msg, agent);
  }
}
```

- [ ] **Step 20: Run test to verify it passes**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/capability-registry.test.js --no-coverage 2>&1 | tail -10
```
Expected: PASS

- [ ] **Step 21: Commit**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
git add src/protocols/capability-registry.js test/unit/capability-registry.test.js
git commit -m "feat(capability-registry): add core CapabilityRegistry class

- register/unregister with capabilityIndex
- match() with weighted scoring (exact/prefix/contains + load + recency)
- subscribe/notifySubscribers for pub/sub notifications

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 2: Router Integration

**Files:**
- Modify: `src/router.js:40-95` (registerAgent, unregisterAgent, heartbeat)
- Modify: `src/router.js:221-261` (handleDiscovery)

- [ ] **Step 1: Write failing test — router.integrates CapabilityRegistry**

```javascript
// test/unit/router-discovery.test.js
import { A2ARouter } from '../../src/router.js';

describe('Router Capability Integration', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
  });

  test('registerAgent() updates capability registry', () => {
    router.registerAgent('test-agent', ['coding', 'review']);
    const matches = router.capabilityRegistry.match('code', { limit: 5 });
    expect(matches.length).toBeGreaterThan(0);
  });

  test('unregisterAgent() removes from capability registry', () => {
    router.registerAgent('test-agent', ['coding']);
    router.unregisterAgent('test-agent');
    const matches = router.capabilityRegistry.match('coding', { limit: 5 });
    expect(matches.some(m => m.agentId === 'test-agent')).toBe(false);
  });

  test('matchBestAgent() returns best scored agent', () => {
    router.registerAgent('idle-coder', ['coding']);
    router.registerAgent('busy-coder', ['coding']);
    router.heartbeat('idle-coder', 'healthy', 0.1, 0);
    router.heartbeat('busy-coder', 'healthy', 0.9, 10);

    const result = router.matchBestAgent('code', { limit: 1 });
    expect(result[0].agentId).toBe('idle-coder');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/router-discovery.test.js --no-coverage 2>&1 | tail -15
```
Expected: FAIL — "capabilityRegistry is undefined" / "matchBestAgent is not a function"

- [ ] **Step 3: Modify router.js — add CapabilityRegistry import and initialization**

```javascript
// At top of router.js, add:
import { CapabilityRegistry } from './protocols/capability-registry.js';

// In constructor, after this.queues initialization:
this.capabilityRegistry = new CapabilityRegistry(this);
```

- [ ] **Step 4: Modify router.js — wire registerAgent to registry**

```javascript
// In registerAgent(), after this.agents.set():
this.capabilityRegistry.register(agentId, capabilities);
```

- [ ] **Step 5: Modify router.js — wire unregisterAgent to registry**

```javascript
// In unregisterAgent(), after this.agents.delete():
this.capabilityRegistry.unregister(agentId);
```

- [ ] **Step 6: Write failing test — subscribe/unsubscribe capabilities**

```javascript
test('subscribeCapabilities() adds subscription', () => {
  router.registerAgent('subscriber', ['listening']);
  router.subscribeCapabilities('subscriber', ['coding']);
  const capSubs = router.capabilityRegistry.subscriptions.get('coding');
  expect(capSubs && capSubs.has('subscriber')).toBe(true);
});
```

- [ ] **Step 7: Run test to verify it fails**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/router-discovery.test.js --no-coverage 2>&1 | tail -10
```
Expected: FAIL — "subscribeCapabilities is not a function"

- [ ] **Step 8: Write subscribeCapabilities, unsubscribeCapabilities, updateAgentCapabilities methods**

```javascript
subscribeCapabilities(agentId, capabilities) {
  this.capabilityRegistry.subscribe(agentId, capabilities);
  return { success: true };
}

unsubscribeCapabilities(agentId, capabilities) {
  this.capabilityRegistry.unsubscribe(agentId, capabilities);
  return { success: true };
}

updateAgentCapabilities(agentId, capabilities) {
  this.capabilityRegistry.updateCapabilities(agentId, capabilities);
  return { success: true };
}

matchBestAgent(query, constraints) {
  return this.capabilityRegistry.match(query, constraints);
}
```

- [ ] **Step 9: Write failing test — handleDiscovery delegates to registry**

```javascript
test('handleDiscovery() returns scored matches', () => {
  router.registerAgent('coder', ['coding']);
  router.heartbeat('coder', 'healthy', 0.2, 0);

  const msg = {
    id: 'test-1', type: 'DISCOVER', from: 'client', to: 'router',
    timestamp: Date.now(), payload: { query: 'code' }
  };
  router.routeMessage(msg);
  // handleDiscovery sends response back to client
});
```

- [ ] **Step 10: Run tests to verify all pass**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/unit/router-discovery.test.js --no-coverage 2>&1 | tail -10
```
Expected: PASS

- [ ] **Step 11: Commit**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
git add src/router.js test/unit/router-discovery.test.js
git commit -m "feat(router): integrate CapabilityRegistry

- registerAgent/unregisterAgent sync to registry
- add matchBestAgent, subscribeCapabilities, unsubscribeCapabilities, updateAgentCapabilities
- handleDiscovery delegates to registry.match()

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 3: MCP Server Tools

**Files:**
- Modify: `src/server.js:44-302` (add 3 new tools to TOOLS array)
- Modify: `src/server.js:311-567` (add tool handlers)

- [ ] **Step 1: Write failing test — server has new tool definitions**

```javascript
// Note: MCP tools are defined in server.js TOOLS array
// Test via inspection or integration test
import { A2ARouter } from '../../src/router.js';
import { ACPGateway } from '../../src/protocols/acp-gateway.js';

const router = new A2ARouter({ heartbeatTimeout: 60000 });
const gateway = new ACPGateway(router, { enabled: true });
// Tools are defined in server.js TOOLS array
// We verify via server startup output
```

- [ ] **Step 2: Add tool definitions to TOOLS array (lines 44-302)**

Add to the TOOLS array in server.js:

```javascript
{
  name: 'a2a_subscribe_capabilities',
  description: 'Subscribe to capability change notifications',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string', description: 'Agent subscribing' },
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
      loadThreshold: { type: 'number', default: 0.9 },
      limit: { type: 'number', default: 5 }
    },
    required: ['query']
  }
},
{
  name: 'a2a_update_agent_capabilities',
  description: 'Update an agent capabilities after initial registration',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string' },
      capabilities: { type: 'array', items: { type: 'string' } }
    },
    required: ['agentId', 'capabilities']
  }
}
```

- [ ] **Step 3: Add tool handlers in server.js switch statement**

```javascript
case 'a2a_subscribe_capabilities': {
  const result = router.subscribeCapabilities(args.agentId, args.capabilities || []);
  return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
}

case 'a2a_match_agent': {
  const result = router.matchBestAgent(args.query, {
    loadThreshold: args.loadThreshold || 0.9,
    limit: args.limit || 5
  });
  return { content: [{ type: 'text', text: JSON.stringify({ success: true, matches: result }, null, 2) }] };
}

case 'a2a_update_agent_capabilities': {
  const result = router.updateAgentCapabilities(args.agentId, args.capabilities || []);
  return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
}
```

- [ ] **Step 4: Verify server starts with new tools**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
timeout 3 node src/server.js 2>&1 || true
```
Expected: Output shows 17 tools registered (14 existing + 3 new)

- [ ] **Step 5: Commit**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
git add src/server.js
git commit -m "feat(server): add 3 MCP tools for capability discovery

- a2a_subscribe_capabilities: subscribe to capability changes
- a2a_match_agent: smart matching with load scoring
- a2a_update_agent_capabilities: update agent capabilities

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 4: Integration Test

**Files:**
- Create: `test/integration/capability-discovery.test.js`

- [ ] **Step 1: Write integration test — full discovery flow**

```javascript
// test/integration/capability-discovery.test.js
import { A2ARouter } from '../../src/router.js';
import { ACPGateway } from '../../src/protocols/acp-gateway.js';

describe('Capability Discovery Integration', () => {
  let router;
  let gateway;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
    gateway = new ACPGateway(router, { enabled: true });
  });

  test('agent registration broadcasts to subscribers', () => {
    router.registerAgent('provider', ['coding']);
    router.subscribeCapabilities('subscriber', ['coding']);

    let notification = null;
    router.on('message:deliver', (msg) => {
      if (msg.to === 'subscriber') notification = msg;
    });

    router.registerAgent('new-agent', ['coding']);

    expect(notification).not.toBeNull();
    expect(notification.payload.event.capability).toBe('coding');
  });

  test('matchBestAgent returns highest scoring agent', () => {
    router.registerAgent('idle-coder', ['coding']);
    router.registerAgent('busy-reviewer', ['code-review']);
    router.heartbeat('idle-coder', 'healthy', 0.1, 0);
    router.heartbeat('busy-reviewer', 'healthy', 0.95, 10);

    const matches = router.matchBestAgent('code', { limit: 5 });
    expect(matches[0].agentId).toBe('idle-coder');
  });

  test('updateAgentCapabilities emits updated event', () => {
    router.registerAgent('agent-1', ['coding']);
    let updated = null;
    router.on('capability:updated', (data) => { updated = data; });

    router.updateAgentCapabilities('agent-1', ['coding', 'review']);

    expect(updated).not.toBeNull();
    expect(updated.newCapabilities).toContain('review');
  });
});
```

- [ ] **Step 2: Run integration test**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
node --experimental-vm-modules node_modules/.bin/jest test/integration/capability-discovery.test.js --no-coverage 2>&1 | tail -15
```
Expected: PASS

- [ ] **Step 3: Commit**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
git add test/integration/capability-discovery.test.js
git commit -m "test: add capability discovery integration tests

- agent registration broadcasts to subscribers
- matchBestAgent returns highest scoring agent
- updateAgentCapabilities emits capability:updated

Co-Authored-By: claude-flow <ruv@ruv.net>"
```

---

## Task 5: Verify Full Server Startup

- [ ] **Step 1: Start server and verify all tools**

```bash
cd "D:/OpenClaw/workspace/80-PROJECTS/a2a-router"
timeout 5 node src/server.js 2>&1 || true
```
Expected: Shows "Tools available: a2a_register_agent, a2a_unregister_agent, a2a_heartbeat, a2a_send_message, a2a_discover, a2a_get_agents, a2a_get_stats, ruflo_list_agents, ruflo_dispatch_task, ruflo_get_status, ruflo_query_intelligence, acp_send_message, acp_register_agent, acp_gateway_status, **a2a_subscribe_capabilities, a2a_match_agent, a2a_update_agent_capabilities**"

---

## Verification Checklist

- [ ] `npm test` runs all tests
- [ ] Server starts without errors
- [ ] All 17 MCP tools visible in startup output
- [ ] Manual test: `node -e "import('./src/server.js')"` completes without import errors
- [ ] Backward compatibility: existing `a2a_discover` still works
