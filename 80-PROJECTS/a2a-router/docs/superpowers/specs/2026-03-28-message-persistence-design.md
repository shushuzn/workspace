# Message Persistence Design — a2a-router

**Date**: 2026-03-28
**Feature**: SQLite-based Message Persistence
**Status**: Approved

---

## 1. Overview

Add persistent message storage to a2a-router using SQLite. Messages are written to disk for durability and can be queried by agent ID or time range.

---

## 2. Architecture

### File Structure

```
src/
├── protocols/
│   ├── capability-registry.js    # existing
│   └── persistence/
│       └── message-store.js       # NEW: SQLite message store
├── router.js                      # MODIFY: integrate MessageStore
└── server.js                     # MODIFY: add query tools
test/
└── unit/
    └── message-store.test.js      # NEW: unit tests
```

### Component: MessageStore

- **Location**: `src/protocols/persistence/message-store.js`
- **Database**: `messages.db` (SQLite, WAL mode)
- **Table**: `messages`

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PRIMARY KEY | Message UUID |
| from | TEXT | Source agent ID |
| to | TEXT | Target agent ID (or 'broadcast') |
| type | TEXT | Message type |
| priority | TEXT | CRITICAL/HIGH/NORMAL/LOW |
| payload | TEXT | JSON payload |
| timestamp | INTEGER | Unix ms |
| delivered_at | INTEGER | Delivery timestamp (null if queued) |

**Indexes**:
- `idx_messages_from` on `from`
- `idx_messages_to` on `to`
- `idx_messages_timestamp` on `timestamp`

---

## 3. Data Flow

```
routeMessage()
  → validateMessage()
  → save to MessageStore.save()
  → emit 'message:deliver'
  → return { success, messageId }
```

Query path:
```
a2a_query_messages tool
  → MessageStore.findByAgent(agentId, { limit, since, until })
  → returns array of messages
```

---

## 4. API

### MessageStore Class

```javascript
class MessageStore {
  constructor(dbPath = './messages.db')

  // Save a message to disk
  // Returns: { success: true, id }
  save(message)

  // Find messages by agent (as sender or receiver)
  // Options: { limit = 100, since, until }
  // Returns: Message[]
  findByAgent(agentId, options = {})

  // Find single message by id
  // Returns: Message | null
  findById(id)

  // Delete messages older than timestamp
  // Returns: count deleted
  archive(olderThan)

  // Close database connection
  close()
}
```

### Router Integration

- `router.messageStore` — MessageStore instance
- `router.persistMessage(message)` — save message before routing
- `router.queryMessages(agentId, options)` — query history

---

## 5. MCP Tools

### a2a_query_messages

```javascript
{
  name: 'a2a_query_messages',
  description: 'Query message history for an agent',
  inputSchema: {
    type: 'object',
    properties: {
      agentId: { type: 'string' },
      limit: { type: 'number', default: 100 },
      since: { type: 'number' },  // Unix timestamp ms
      until: { type: 'number' }   // Unix timestamp ms
    },
    required: ['agentId']
  }
}
```

### a2a_archive_messages

```javascript
{
  name: 'a2a_archive_messages',
  description: 'Delete messages older than timestamp',
  inputSchema: {
    type: 'object',
    properties: {
      olderThan: { type: 'number' }  // Unix timestamp ms
    },
    required: ['olderThan']
  }
}
```

---

## 6. Error Handling

| Scenario | Behavior |
|----------|----------|
| SQLite write fails | Log error, return `{ success: false, error }`, do NOT block routing |
| Database locked | SQLite WAL handles concurrent reads/writes |
| Invalid query params | Return `{ success: false, error: 'INVALID_PARAMS' }` |

---

## 7. Implementation Steps

1. Create `src/protocols/persistence/message-store.js`
2. Add unit tests in `test/unit/message-store.test.js`
3. Integrate MessageStore into `router.js`
4. Add MCP tools to `server.js`
5. Verify all tests pass

---

## 8. Tech Notes

- **SQLite WAL mode**: enables concurrent reads during writes
- **Synchronous**: NORMAL (default SQLite safe mode)
- **Journal mode**: WAL (better concurrency)
- **No external dependencies**: use built-in `node:sqlite` or `better-sqlite3`
