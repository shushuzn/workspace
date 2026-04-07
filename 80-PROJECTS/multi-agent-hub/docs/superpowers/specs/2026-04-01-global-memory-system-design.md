# Global Memory System — Design Spec

> **For agentic workers:** Implementation via superpowers:writing-plans → superpowers:subagent-driven-development

**Goal:** Build a global (workspace-wide) memory system that automatically archives session outcomes and enables semantic search across all sessions.

**Core principle:** Write simple, query smart. SessionEnd hook writes to both SQLite (primary store) and MEMORY.md (human-readable backup). Query layer uses SQLite FTS5 for full-text search.

---

## Architecture

> **Key constraint:** Claude Code has no `SessionEnd` hook. Available events: `SessionStart`, `UserPromptSubmit`, `AssistantMessage`, `Stop`. Solution: SessionStart hook processes the **previous** session's history on each startup.

```
Every SessionStart
    ↓
hook reads history.jsonl
    ↓
finds last session_id not yet processed (via processed_sessions tracking)
    ↓
extracts memory from that session's history lines
    ↓
writes to ~/.claude/memory/sessions.db (SQLite + FTS5)
    ↓
marks session as processed (prevents double-run)
    ↓
also appends to ~/.claude/projects/{project}/MEMORY.md
    ↓
injects recent memory summary into context for current session
```

---

## Data Model

### SQLite Schema

```sql
CREATE TABLE sessions (
  session_id   TEXT PRIMARY KEY,
  timestamp   INTEGER,
  project     TEXT,
  summary     TEXT,
  operations  TEXT,    -- JSON array: ["bugfix", "feature", "research"]
  files_modified TEXT, -- JSON array of file paths
  problems   TEXT,    -- What went wrong
  solutions  TEXT,    -- How it was solved
  tags       TEXT     -- JSON array: ["ai-roundtable", "bugfix", "performance"]
);

CREATE VIRTUAL TABLE sessions_fts USING fts5(
  summary, problems, solutions,
  content=sessions,
  content_rowid=rowid
);
```

### Memory Entry Example

```json
{
  "session_id": "76053268-d243-4153-be08-af2be297a190",
  "timestamp": 1775012000000,
  "project": "ai-roundtable",
  "summary": "Cognitive Annealing quality scorer implemented with subagent-driven workflow",
  "operations": ["feature", "testing", "integration"],
  "files_modified": [
    "shared/qualityScorer.js",
    "index.js",
    "tests/qualityScorer.test.js"
  ],
  "problems": "NaN in balance formula when contributions=[], quality score null on round 1",
  "solutions": "Added contributions.length guard, moved scorer call outside persona loop",
  "tags": [
    "ai-roundtable",
    "quality-scorer",
    "subagent-dev",
    "cognitive-annealing"
  ]
}
```

---

## Component Specifications

### 1. `session-end-hook.js`

**Location:** `~/.claude/hooks/session-end-hook.js`

**Trigger:** `SessionEnd` hook (configured in hooks.json)

**Input:** `history.jsonl` lines for current session, identified by `sessionId`

**Process:**

1. Read all `history.jsonl` lines with matching `sessionId`
2. Extract all `display` field values (user prompts/responses) and `pastedContents`
3. Parse the transcript — identify operations (tool calls: Read/Edit/Write/Bash), errors, outcomes
4. Extract `project` field from history lines
5. Classify operation type: `feature|bugfix|refactor|research|planning|discussion|other`
6. Detect `problems` and `solutions` from transcript content (error messages → solutions via edits)
7. Extract `files_modified` from tool call paths
8. Generate summary (first user prompt + key outcome, ≤200 chars)
9. Write to SQLite sessions table
10. Upsert to FTS5 index
11. Append entry to `~/.claude/projects/{project}/MEMORY.md` in Session History table format

**Dependencies:** `sqlite3` (via require or动态加载)

**Error handling:** On failure, log to stderr but do NOT block session end.

---

### 2. `memory-query.js`

**Location:** `~/.claude/hooks/memory-query.js`

**Interface:** CLI via `node memory-query.js <command> [args]`

**Commands:**

| Command          | Example                                      | Description                      |
| ---------------- | -------------------------------------------- | -------------------------------- |
| `recent <n>`     | `node memory-query.js recent 5`              | Last N sessions                  |
| `project <name>` | `node memory-query.js project ai-roundtable` | All sessions for project         |
| `search <query>` | `node memory-query.js search "NaN bug"`      | FTS5 full-text search            |
| `tag <tag>`      | `node memory-query.js tag bugfix`            | Filter by tag                    |
| `stats`          | `node memory-query.js stats`                 | Session count, project breakdown |

**Output:** Plain text, human-readable, suitable for terminal

**Dependencies:** `sql.js` (WASM SQLite, zero native deps) — or `sqlite3` if available

**Usage as module:** Export `queryRecent(n)`, `queryByProject(p)`, `search(q)` for use by other components

---

### 3. Startup Integration

**Location:** Existing `SessionStart` hook or new startup script

**Behavior:** On session start, call `memory-query.js recent 3` and inject summary into session context as a `memory-context` note.

Implementation options (pick one):

- Modify existing `session-start` hook to chain `node memory-query.js recent 3` output
- Add to CLAUDE.md as a directive: `On session start, check memory-query.js recent 3 for context`
- Integrate into skill system via `@hook` directive in prompts

**Recommended:** Option 1 (modify startup hook), then document in CLAUDE.md as fallback.

---

### 4. FTS5 Indexing Strategy

- Synchronous index update on every session write (SQLite transaction)
- FTS5 ` MATCH` query with `ORDER BY rank` for relevance
- `tokenize=porter` for Chinese/English stemming

---

### 5. MEMORY.md Compatibility Layer

SessionEnd hook appends to project-level MEMORY.md in the existing format:

```markdown
| {date} | {session_id} | {summary} |
```

Session ID links to full DB entry for drill-down.

DB is the **authoritative store**; MEMORY.md is a human-readable mirror.

---

## SessionEnd Hook Registration

**Note:** There is no `SessionEnd` hook in Claude Code. Instead, the existing `SessionStart` hook is extended to:

1. Process the previous session's memory on every startup
2. Inject recent memory context

The `session-start` script is modified (or a new `session-start-memory` script added) to chain the memory processing step.

---

## Technology Choices

| Item             | Choice                   | Rationale                                        |
| ---------------- | ------------------------ | ------------------------------------------------ |
| Primary store    | SQLite3                  | Zero-config, embedded, transactional             |
| Full-text search | FTS5                     | Built into SQLite, fast, adequate for this scale |
| Query library    | sql.js (WASM)            | Zero native dependencies, portable               |
| Write library    | sqlite3 (native or wasm) | Used only in hook context                        |
| Language         | Node.js                  | Already available in Claude Code environment     |
| Config           | hooks.json               | Standard Claude Code hooks mechanism             |

---

## Out of Scope (Phase 1)

- Vector embeddings / semantic similarity search
- Per-session deletion or editing
- Multi-user / cloud sync
- Automatic tag extraction via LLM
- Query result caching

---

## Processed Sessions Tracking

To avoid re-processing the same session on multiple startups, maintain a `processed_sessions` table:

```sql
CREATE TABLE processed_sessions (
  session_id TEXT PRIMARY KEY,
  processed_at INTEGER
);
```

On each SessionStart:

1. Query `processed_sessions` for the most recent unprocessed session_id in history.jsonl
2. If found: process it → insert into sessions + FTS → insert into processed_sessions
3. If not found: nothing to do (already caught up)

The session being processed is the one that wrote to `history.jsonl` before the current session started.

---

## Rollout Sequence

1. **Startup hook extension** — Modify session-start script to chain memory processor
2. **SQLite + FTS5 init** — Create DB schema, verify sqlite3 works in hook context
3. **memory-processor.js** — Implement history.jsonl parser + session extractor + DB writer
4. **Processed tracking** — Verify duplicate prevention works
5. **memory-query.js** — Implement all query commands
6. **MEMORY.md compatibility** — Dual-write confirmed working
7. **Context injection** — Inject recent memory on session start
8. **Verification** — Run real sessions, verify history appears in queries
