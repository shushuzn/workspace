# Queue Monitoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add queue backlog monitoring to a2a-router with threshold alerts via MCP tools.

**Architecture:** QueueMonitor class wraps queue statistics collection and threshold checking (ThresholdChecker is embedded in QueueMonitor — simplified from spec). Router initializes it and calls checkThresholds() after each enqueue to detect threshold breaches. MCP tools expose stats and alerts via server.js.

**Tech Stack:** Node.js (no external deps), Jest for testing

---

## Task 1: QueueMonitor Class

**Files:**
- Create: `src/protocols/monitoring/queue-monitor.js`
- Test: `test/unit/queue-monitor.test.js`

### Steps

- [ ] **Step 1: Write failing test — QueueMonitor initializes**

```javascript
// test/unit/queue-monitor.test.js
import { QueueMonitor } from '../../src/protocols/monitoring/queue-monitor.js';

describe('QueueMonitor', () => {
  let router;
  let monitor;

  beforeEach(() => {
    router = {
      queues: new Map([
        ['CRITICAL', []],
        ['HIGH', []],
        ['NORMAL', []],
        ['LOW', []]
      ])
    };
    monitor = new QueueMonitor(router);
  });

  test('initializes with default thresholds', () => {
    expect(monitor.thresholds.CRITICAL).toBe(10);
    expect(monitor.thresholds.HIGH).toBe(50);
    expect(monitor.thresholds.NORMAL).toBe(100);
    expect(monitor.thresholds.LOW).toBe(200);
  });

  test('initializes with custom thresholds', () => {
    const custom = new QueueMonitor(router, {
      thresholds: { CRITICAL: 5, HIGH: 20, NORMAL: 50, LOW: 100 }
    });
    expect(custom.thresholds.CRITICAL).toBe(5);
  });
});
```

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/queue-monitor.test.js`
Expected: FAIL — QueueMonitor not found

- [ ] **Step 2: Create QueueMonitor class**

```javascript
// src/protocols/monitoring/queue-monitor.js
export class QueueMonitor {
  constructor(router, options = {}) {
    this.router = router;
    this.thresholds = options.thresholds || {
      CRITICAL: 10,
      HIGH: 50,
      NORMAL: 100,
      LOW: 200
    };
  }

  getQueueStats() {
    const queues = {};
    const alerts = [];

    for (const [priority, queue] of this.router.queues) {
      const size = queue.length;
      let avgWaitTime = 0;
      let maxWaitTime = 0;

      if (size > 0) {
        const now = Date.now();
        const waitTimes = queue.map(msg => now - (msg.enqueuedAt || now));
        avgWaitTime = Math.round(waitTimes.reduce((a, b) => a + b, 0) / size);
        maxWaitTime = Math.max(...waitTimes);
      }

      queues[priority] = { size, avgWaitTime, maxWaitTime };

      // Check threshold
      const threshold = this.thresholds[priority];
      if (size > threshold) {
        alerts.push({
          level: priority,
          queue: priority,
          message: `Queue ${priority} backlog ${size} exceeds threshold ${threshold}`,
          triggeredAt: Date.now()
        });
      }
    }

    return { queues, alerts };
  }

  checkThresholds() {
    return this.getQueueStats().alerts;
  }
}
```

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/queue-monitor.test.js`
Expected: PASS

- [ ] **Step 3: Write failing test — empty queue stats**

```javascript
test('getQueueStats() returns zeros for empty queue', () => {
  const stats = monitor.getQueueStats();
  expect(stats.queues.CRITICAL.size).toBe(0);
  expect(stats.queues.CRITICAL.avgWaitTime).toBe(0);
  expect(stats.queues.CRITICAL.maxWaitTime).toBe(0);
  expect(stats.alerts).toEqual([]);
});
```

Run: FAIL — implementation returns 0 but test expects exact match

- [ ] **Step 4: Write failing test — queue with messages**

```javascript
test('getQueueStats() calculates wait times', () => {
  const msg1 = { id: 'm1', enqueuedAt: Date.now() - 1000 };
  const msg2 = { id: 'm2', enqueuedAt: Date.now() - 500 };
  router.queues.get('HIGH').push(msg1, msg2);

  const stats = monitor.getQueueStats();
  expect(stats.queues.HIGH.size).toBe(2);
  expect(stats.queues.HIGH.maxWaitTime).toBeGreaterThanOrEqual(1000);
});
```

Run: FAIL — wait times need verification

- [ ] **Step 5: Write failing test — threshold alert**

```javascript
test('checkThresholds() returns alert when over threshold', () => {
  // Add 15 messages to HIGH queue (threshold is 50)
  for (let i = 0; i < 15; i++) {
    router.queues.get('HIGH').push({ id: `m${i}`, enqueuedAt: Date.now() });
  }

  const alerts = monitor.checkThresholds();
  expect(alerts.length).toBe(1);
  expect(alerts[0].level).toBe('HIGH');
  expect(alerts[0].queue).toBe('HIGH');
  expect(alerts[0].message).toContain('15');
});
```

Run: FAIL — alerts not generated

- [ ] **Step 6: Implement checkThresholds and verify all tests pass**

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/queue-monitor.test.js`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/protocols/monitoring/queue-monitor.js test/unit/queue-monitor.test.js
git commit -m "feat(monitoring): add QueueMonitor class for queue stats

- QueueMonitor wraps router queues and threshold config
- getQueueStats() returns size, avgWaitTime, maxWaitTime per priority
- checkThresholds() returns alerts when queue exceeds threshold"
```

---

## Task 2: Router Integration

**Files:**
- Modify: `src/router.js` — add QueueMonitor, track enqueuedAt

### Steps

- [ ] **Step 1: Write failing test — router initializes QueueMonitor**

```javascript
// test/unit/router-monitoring.test.js (new file)
import { A2ARouter } from '../../src/router.js';

describe('Router Queue Monitoring', () => {
  let router;

  beforeEach(() => {
    router = new A2ARouter({ heartbeatTimeout: 60000 });
  });

  test('router has queueMonitor', () => {
    expect(router.queueMonitor).toBeDefined();
  });

  test('routeMessage sets enqueuedAt on queued messages', () => {
    router.registerAgent('alice', ['coding']);
    router.registerAgent('bob', ['review']);

    router.routeMessage({
      id: 'enqueue-test',
      type: 'TASK',
      priority: 'HIGH',
      from: 'alice',
      to: 'bob',
      timestamp: Date.now(),
      payload: {}
    });

    const queue = router.queues.get('HIGH');
    expect(queue[0].enqueuedAt).toBeDefined();
  });
});
```

Run: FAIL — queueMonitor not defined

- [ ] **Step 2: Modify router.js — import and init QueueMonitor**

In `constructor`, after messageStore init:

```javascript
import { QueueMonitor } from './protocols/monitoring/queue-monitor.js';

// In constructor:
this.queueMonitor = new QueueMonitor(this, {
  thresholds: options.queueThresholds || undefined
});
```

Run: PASS

- [ ] **Step 3: Modify router to set enqueuedAt on enqueue AND check thresholds**

Find where messages are added to queue. Add:

```javascript
message.enqueuedAt = Date.now();

// Check thresholds after enqueue
const alerts = this.queueMonitor.checkThresholds();
if (alerts.length > 0) {
  // Log alerts or emit event
  console.warn('[Router] Queue threshold alerts:', alerts);
}
```

In the code that pushes to queue. Run test to verify.

- [ ] **Step 4: Add query method to router**

```javascript
getQueueStats() {
  return this.queueMonitor.getQueueStats();
}
```

- [ ] **Step 5: Commit**

```bash
git add src/router.js test/unit/router-monitoring.test.js
git commit -m "feat(router): integrate QueueMonitor for backlog monitoring

- router.queueMonitor accessible for queries
- routeMessage() records enqueuedAt timestamp
- getQueueStats() wrapper method"
```

---

## Task 3: MCP Tools

**Files:**
- Modify: `src/server.js` — add a2a_get_queue_stats tool

### Steps

- [ ] **Step 1: Write failing test — server returns queue stats**

Add to existing server test or create new integration test:

```javascript
test('a2a_get_queue_stats returns queue information', async () => {
  // Setup router with queued messages
  const result = await callTool('a2a_get_queue_stats', {});
  const parsed = JSON.parse(result.content[0].text);
  expect(parsed.success).toBe(true);
  expect(parsed.queues).toBeDefined();
});
```

Run: FAIL — tool not defined

- [ ] **Step 2: Add tool definition to TOOLS array**

```javascript
{
  name: 'a2a_get_queue_stats',
  description: 'Get queue backlog statistics and threshold alerts',
  inputSchema: {
    type: 'object',
    properties: {}
  }
}
```

- [ ] **Step 3: Add handler in switch statement**

```javascript
case 'a2a_get_queue_stats': {
  const stats = router.getQueueStats();
  return {
    content: [{ type: 'text', text: JSON.stringify({ success: true, ...stats }, null, 2) }]
  };
}
```

- [ ] **Step 4: Verify server starts with all tools**

```bash
timeout 5 node --experimental-vm-modules src/server.js 2>&1 | head -20
```

Expected: "Tools available:" includes "a2a_get_queue_stats"

- [ ] **Step 5: Commit**

```bash
git add src/server.js
git commit -m "feat(server): add a2a_get_queue_stats MCP tool"
```

---

## Task 4: Integration Test

**Files:**
- Create: `test/integration/monitoring.test.js`

### Steps

- [ ] **Step 1: Full integration test — queue stats with alerts**

```javascript
test('end-to-end: queue stats with threshold alert', () => {
  const router = new A2ARouter({ heartbeatTimeout: 60000 });
  router.registerAgent('alice', ['coding']);
  router.registerAgent('bob', ['review']);

  // Fill HIGH queue over threshold (15 > 50 threshold)
  for (let i = 0; i < 15; i++) {
    router.routeMessage({
      id: `msg-${i}`,
      type: 'TASK',
      priority: 'HIGH',
      from: 'alice',
      to: 'bob',
      timestamp: Date.now(),
      payload: {}
    });
  }

  const stats = router.getQueueStats();
  expect(stats.queues.HIGH.size).toBe(15);
  expect(stats.alerts.length).toBeGreaterThan(0);
  expect(stats.alerts[0].level).toBe('HIGH');
});
```

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/integration/monitoring.test.js`
Expected: PASS

- [ ] **Step 2: Commit**

```bash
git add test/integration/monitoring.test.js
git commit -m "test(integration): add queue monitoring end-to-end test"
```

---

## Final Verification

Run all tests:
```bash
node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/ --silent
```

Expected: All tests pass (36+ total)

Verify server:
```bash
timeout 5 node --experimental-vm-modules src/server.js 2>&1 | head -20
```

Expected: "A2A Router MCP Server started" + "Tools available: a2a_get_queue_stats"
