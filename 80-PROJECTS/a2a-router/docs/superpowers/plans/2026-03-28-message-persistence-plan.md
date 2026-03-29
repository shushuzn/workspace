# Message Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add SQLite-based message persistence to a2a-router so messages survive restarts and can be queried by agent/time.

**Architecture:** MessageStore wraps SQLite (node:sqlite), integrated into A2ARouter as `router.messageStore`. Messages are saved synchronously after validation but before delivery. Query methods allow retrieval by agentId and time range.

**Tech Stack:** Node.js built-in `node:sqlite` (Node 22+), Jest for testing

> **Node Version**: Requires Node.js 22+ (built-in `node:sqlite` module)

---

## Task 1: MessageStore Class

**Files:**
- Create: `src/protocols/persistence/message-store.js`
- Test: `test/unit/message-store.test.js`

### Steps

- [ ] **Step 1: Write failing test — MessageStore initializes database**

```javascript
// test/unit/message-store.test.js
import { MessageStore } from '../../src/protocols/persistence/message-store.js';

describe('MessageStore', () => {
  let store;

  test('initializes with messages table', () => {
    store = new MessageStore(':memory:');
    const result = store.getDatabase().prepare(
      "SELECT name FROM sqlite_master WHERE type='table' AND name='messages'"
    ).get();
    expect(result.name).toBe('messages');
  });
});
```

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/message-store.test.js`
Expected: FAIL — MessageStore not found

- [ ] **Step 2: Create MessageStore with table creation**

```javascript
// src/protocols/persistence/message-store.js
import { Database } from 'node:sqlite';

export class MessageStore {
  constructor(dbPath = './messages.db') {
    this.db = new Database(dbPath);
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        from_agent TEXT NOT NULL,
        to_agent TEXT NOT NULL,
        type TEXT NOT NULL,
        priority TEXT DEFAULT 'NORMAL',
        payload TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        delivered_at INTEGER
      )
    `);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_messages_from ON messages(from_agent)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_agent)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)`);
  }

  getDatabase() { return this.db; }
  close() { this.db.close(); }
}
```

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/message-store.test.js`
Expected: PASS

- [ ] **Step 3: Write failing test — save()**

```javascript
test('save() inserts message and returns id', () => {
  const msg = {
    id: 'msg-1',
    from: 'agent-a',
    to: 'agent-b',
    type: 'TASK',
    priority: 'NORMAL',
    payload: JSON.stringify({ data: 'hello' }),
    timestamp: Date.now()
  };
  const result = store.save(msg);
  expect(result.success).toBe(true);
  expect(result.id).toBe('msg-1');
});
```

Run: FAIL — save() not yet implemented

- [ ] **Step 4: Implement save() method**

```javascript
save(message) {
  try {
    const stmt = this.db.prepare(`
      INSERT INTO messages (id, from_agent, to_agent, type, priority, payload, timestamp, delivered_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);
    stmt.run(
      message.id,
      message.from,
      message.to,
      message.type,
      message.priority || 'NORMAL',
      JSON.stringify(message.payload),
      message.timestamp,
      message.delivered_at || null
    );
    return { success: true, id: message.id };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

- [ ] **Step 5: Write failing test — findByAgent()**

```javascript
test('findByAgent() returns messages for agent as sender', () => {
  store.save({ id: 'm1', from: 'a', to: 'b', type: 'TASK', payload: '{}', timestamp: Date.now() });
  store.save({ id: 'm2', from: 'b', to: 'a', type: 'RESPONSE', payload: '{}', timestamp: Date.now() });
  const results = store.findByAgent('a', { limit: 10 });
  expect(results.length).toBe(2); // both m1 (from) and m2 (to)
});
```

Run: FAIL — findByAgent not implemented

- [ ] **Step 6: Implement findByAgent()**

```javascript
findByAgent(agentId, options = {}) {
  const { limit = 100, since, until } = options;
  let sql = `SELECT * FROM messages WHERE (from_agent = ? OR to_agent = ?)`;
  const params = [agentId, agentId];
  if (since !== undefined) {
    sql += ` AND timestamp >= ?`;
    params.push(since);
  }
  if (until !== undefined) {
    sql += ` AND timestamp <= ?`;
    params.push(until);
  }
  sql += ` ORDER BY timestamp DESC LIMIT ?`;
  params.push(limit);
  const stmt = this.db.prepare(sql);
  return stmt.all(...params);
}
```

- [ ] **Step 7: Write failing test — findById() and archive()**

```javascript
test('findById() returns single message', () => {
  store.save({ id: 'unique-1', from: 'a', to: 'b', type: 'TASK', payload: '{}', timestamp: Date.now() });
  const msg = store.findById('unique-1');
  expect(msg.id).toBe('unique-1');
});

test('archive() deletes old messages', () => {
  const oldTs = Date.now() - 100000;
  store.save({ id: 'old-1', from: 'a', to: 'b', type: 'TASK', payload: '{}', timestamp: oldTs });
  const deleted = store.archive(oldTs);
  expect(deleted).toBe(1);
  expect(store.findById('old-1')).toBeUndefined();
});
```

- [ ] **Step 8: Implement findById() and archive()**

```javascript
findById(id) {
  const stmt = this.db.prepare('SELECT * FROM messages WHERE id = ?');
  return stmt.get(id);
}

archive(olderThan) {
  const stmt = this.db.prepare('DELETE FROM messages WHERE timestamp < ?');
  const result = stmt.run(olderThan);
  return result.changes;
}
```

Run all tests: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/message-store.test.js`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
git add src/protocols/persistence/message-store.js test/unit/message-store.test.js
git commit -m "feat(persistence): add MessageStore with SQLite backend

- MessageStore wraps node:sqlite (Node 22+)
- save(), findByAgent(), findById(), archive() methods
- Indexed on from_agent, to_agent, timestamp"
```

---

## Task 2: Router Integration

**Files:**
- Modify: `src/router.js` (add MessageStore integration)

### Steps

- [ ] **Step 1: Write failing test — router has messageStore**

```javascript
// test/unit/router-persistence.test.js (new file)
test('router initializes with messageStore', () => {
  const router = new A2ARouter({ heartbeatTimeout: 60000 });
  expect(router.messageStore).toBeDefined();
  expect(router.messageStore.getDatabase).toBeDefined();
});
```

Run: FAIL — messageStore not defined on router

- [ ] **Step 2: Modify router.js — add MessageStore import and init**

```javascript
import { CapabilityRegistry } from './protocols/capability-registry.js';
import { MessageStore } from './protocols/persistence/message-store.js';

export class A2ARouter extends EventEmitter {
  constructor(options = {}) {
    // ... existing init ...
    this.capabilityRegistry = new CapabilityRegistry(this);
    this.messageStore = new MessageStore(options.dbPath || './messages.db');
    this.startMaintenance();
  }
}
```

Run: PASS

- [ ] **Step 3: Write failing test — routeMessage saves to store**

```javascript
test('routeMessage() saves message to store before delivery', () => {
  const router = new A2ARouter({ heartbeatTimeout: 60000 });
  router.registerAgent('sender', ['coding']);
  router.registerAgent('receiver', ['coding']);
  const msg = {
    id: 'persisted-1',
    type: 'TASK',
    priority: 'NORMAL',
    from: 'sender',
    to: 'receiver',
    timestamp: Date.now(),
    payload: { data: 'test' }
  };
  const result = router.routeMessage(msg);
  expect(result.success).toBe(true);
  const stored = router.messageStore.findById('persisted-1');
  expect(stored.id).toBe('persisted-1');
});
```

Run: FAIL — routeMessage doesn't call save yet

- [ ] **Step 4: Modify router.js — call messageStore.save() in routeMessage()**

In `routeMessage()`, after validation succeeds:

```javascript
routeMessage(message) {
  const validation = this.validateMessage(message);
  if (!validation.valid) {
    return { success: false, error: validation.error };
  }

  // Persist message
  const persistResult = this.messageStore.save(message);
  if (!persistResult.success) {
    console.error('[Router] Failed to persist message:', persistResult.error);
    // Continue routing even if persist fails — don't block delivery
  }

  // ... rest of routing logic
}
```

Run: PASS

- [ ] **Step 5: Add queryMessages method to router**

```javascript
queryMessages(agentId, options = {}) {
  return this.messageStore.findByAgent(agentId, options);
}
```

- [ ] **Step 6: Add archiveMessages method to router**

```javascript
archiveMessages(olderThan) {
  return this.messageStore.archive(olderThan);
}
```

- [ ] **Step 7: Add graceful shutdown to close database**

```javascript
// In A2ARouter, add close() method
close() {
  if (this.messageStore) {
    this.messageStore.close();
  }
}
```

Also update `server.js` to call `router.close()` on SIGTERM/SIGINT:

```javascript
process.on('SIGTERM', () => {
  acpGateway.stop();
  router.close();
  process.exit(0);
});
process.on('SIGINT', () => {
  acpGateway.stop();
  router.close();
  process.exit(0);
});
```

Run all tests: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/unit/`
Expected: PASS (all 19 + new tests)

- [ ] **Step 8: Commit**

```bash
git add src/router.js test/unit/router-persistence.test.js
git commit -m "feat(router): integrate MessageStore for message persistence

- router.messageStore accessible for queries
- routeMessage() saves to SQLite before delivery
- queryMessages() and archiveMessages() wrapper methods"
```

---

## Task 3: MCP Tools

**Files:**
- Modify: `src/server.js` (add 2 new tools)

### Steps

- [ ] **Step 1: Write tool definitions for a2a_query_messages and a2a_archive_messages**

Add to TOOLS array:

```javascript
{
  name: 'a2a_query_messages',
  description: 'Query message history for an agent',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string', description: 'Agent ID to query' },
      limit: { type: 'number', default: 100 },
      since: { type: 'number', description: 'Start timestamp (ms)' },
      until: { type: 'number', description: 'End timestamp (ms)' }
    },
    required: ['agentId']
  }
},
{
  name: 'a2a_archive_messages',
  description: 'Delete messages older than timestamp',
  inputSchema: {
    type: 'object',
    properties: {
      olderThan: { type: 'number', description: 'Delete messages before this timestamp (ms)' }
    },
    required: ['olderThan']
  }
}
```

- [ ] **Step 2: Add handlers in switch statement**

```javascript
case 'a2a_query_messages': {
  const { agentId, limit, since, until } = args;
  const results = router.queryMessages(agentId, { limit: limit || 100, since, until });
  return {
    content: [{ type: 'text', text: JSON.stringify({ success: true, messages: results }, null, 2) }]
  };
}

case 'a2a_archive_messages': {
  const { olderThan } = args;
  const deleted = router.archiveMessages(olderThan);
  return {
    content: [{ type: 'text', text: JSON.stringify({ success: true, deleted }, null, 2) }]
  };
}
```

- [ ] **Step 3: Verify server starts with all 19 tools**

```bash
node --experimental-vm-modules src/server.js &
sleep 2
echo "Server started with new tools"
```

- [ ] **Step 4: Commit**

```bash
git add src/server.js
git commit -m "feat(server): add a2a_query_messages and a2a_archive_messages tools"
```

---

## Task 4: Integration Test

**Files:**
- Create: `test/integration/persistence.test.js`

### Steps

- [ ] **Step 1: Full integration test — register, send, query**

```javascript
test('end-to-end: register agents, send message, query history', () => {
  const router = new A2ARouter({ heartbeatTimeout: 60000 });
  router.registerAgent('alice', ['coding']);
  router.registerAgent('bob', ['review']);

  router.routeMessage({
    id: 'e2e-1',
    type: 'TASK',
    priority: 'HIGH',
    from: 'alice',
    to: 'bob',
    timestamp: Date.now(),
    payload: { task: 'review PR' }
  });

  const history = router.queryMessages('alice', { limit: 10 });
  expect(history.some(m => m.id === 'e2e-1')).toBe(true);
});
```

Run: `node --experimental-vm-modules ./node_modules/jest/bin/jest.js test/integration/persistence.test.js`
Expected: PASS

- [ ] **Step 2: Commit**

```bash
git add test/integration/persistence.test.js
git commit -m "test(integration): add message persistence end-to-end test"
```

---

## Final Verification

Run all tests:
```bash
node --experimental-vm-modules ./node_modules/jest/bin/jest.js --testPathPattern="test/"
```

Expected: All tests pass (19 existing + 7 new = 26 total)

Verify server starts:
```bash
timeout 5 node --experimental-vm-modules src/server.js 2>&1 | head -20
```

Expected: "A2A Router MCP Server started" + "21 tools available"
