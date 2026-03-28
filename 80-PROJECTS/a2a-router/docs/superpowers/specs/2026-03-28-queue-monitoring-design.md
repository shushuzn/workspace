# Queue Monitoring & Threshold Alerts — a2a-router

**Date**: 2026-03-28
**Feature**: Queue Backlog Monitoring with Threshold Alerts
**Status**: Approved

---

## 1. Overview

Add queue monitoring capabilities to a2a-router so operators can query backlog statistics and receive alerts when queues exceed configured thresholds. Implemented as MCP tools — no external dependencies.

---

## 2. Architecture

### Components

- **QueueMonitor** class (`src/protocols/monitoring/queue-monitor.js`) — collects queue statistics
- **ThresholdChecker** — evaluates thresholds, generates alerts
- **New MCP tools** in `server.js` — exposes monitoring via MCP

### File Structure

```
src/
├── protocols/
│   ├── capability-registry.js      # existing
│   ├── persistence/
│   │   └── message-store.js       # existing
│   └── monitoring/                 # NEW
│       └── queue-monitor.js       # NEW: QueueMonitor class
├── router.js                       # MODIFY: add queue monitor, check on route
└── server.js                      # MODIFY: add MCP tools
test/
└── unit/
    └── queue-monitor.test.js      # NEW
```

---

## 3. QueueMonitor Class

```javascript
class QueueMonitor {
  constructor(router, options = {}) {
    this.router = router;
    this.thresholds = options.thresholds || {
      CRITICAL: 10,
      HIGH: 50,
      NORMAL: 100,
      LOW: 200
    };
  }

  // Returns queue statistics for all priorities
  getQueueStats() {
    // Returns: { queues: { CRITICAL: {size, avgWaitTime, maxWaitTime}, ... }, alerts: [...] }
  }

  // Check all queues against thresholds, return alerts
  checkThresholds() {
    // Returns: [{ level, queue, message, triggeredAt }]
  }
}
```

---

## 4. Data Tracked

Each message in queue now carries `enqueuedAt` timestamp:

```javascript
{
  id: 'msg-123',
  type: 'TASK',
  priority: 'HIGH',
  from: 'alice',
  to: 'bob',
  payload: { ... },
  timestamp: 1743168000000,  // original message timestamp
  enqueuedAt: 1743168000500  // when it entered queue (NEW)
}
```

### Queue Statistics

| Metric | Description |
|--------|-------------|
| `size` | Number of messages in queue |
| `avgWaitTime` | Average time in queue (ms) |
| `maxWaitTime` | Longest time in queue (ms) |

---

## 5. MCP Tools

### a2a_get_queue_stats

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

Returns:
```javascript
{
  success: true,
  queues: {
    CRITICAL: { size: 3, avgWaitTime: 120, maxWaitTime: 450 },
    HIGH:     { size: 15, avgWaitTime: 800, maxWaitTime: 3200 },
    NORMAL:   { size: 67, avgWaitTime: 5400, maxWaitTime: 18000 },
    LOW:      { size: 12, avgWaitTime: 12000, maxWaitTime: 36000 }
  },
  alerts: [
    {
      level: 'HIGH',
      queue: 'HIGH',
      message: 'Queue HIGH backlog 15 exceeds threshold 50',
      triggeredAt: 1743168000000
    }
  ]
}
```

### a2a_configure_thresholds (optional)

```javascript
{
  name: 'a2a_configure_thresholds',
  description: 'Configure alert thresholds for queue monitoring',
  inputSchema: {
    type: 'object',
    properties: {
      CRITICAL: { type: 'number' },
      HIGH: { type: 'number' },
      NORMAL: { type: 'number' },
      LOW: { type: 'number' }
    }
  }
}
```

---

## 6. Alert Triggering

Alerts are generated when:
1. `a2a_get_queue_stats` is called — checks thresholds and returns any active alerts
2. `routeMessage()` adds a message to a queue that now exceeds threshold

Alert levels: `CRITICAL`, `HIGH`, `NORMAL`, `LOW`

---

## 7. Error Handling

| Scenario | Behavior |
|----------|----------|
| Queue empty | Returns `size: 0`, no avg/max times |
| All queues under threshold | Returns `alerts: []` |
| Invalid threshold value | Returns error, keeps existing thresholds |

---

## 8. Tech Notes

- **No external dependencies** — uses only built-in Node.js
- **Synchronous** — no async overhead for stat collection
- **Thread-safe** — JavaScript single-threaded, no locks needed
