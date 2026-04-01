# Global Memory System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development

**Goal:** Build a global memory system that automatically archives session outcomes to SQLite + FTS5, enables full-text search, and injects recent memory on session startup.

**Architecture:** No SessionEnd hook exists in Claude Code — SessionStart hook chains a memory processor that reads history.jsonl, finds the last unprocessed session, extracts memory, writes to SQLite + FTS5, and injects recent summaries into context.

**Tech Stack:** Node.js (shell-accessible), sqlite3 (or sql.js WASM for portability), bash hook chaining

---

## File Map

| File | Role |
|------|------|
| `~/.claude/hooks/hooks.json` | Modify — add SessionStart chain |
| `~/.claude/hooks/session-start-memory` | Create — bash wrapper, chains memory-processor.js |
| `~/.claude/hooks/memory-processor.js` | Create — core: parse history.jsonl, write SQLite |
| `~/.claude/memory/sessions.db` | Created at runtime via init step |
| `~/.claude/memory-query.js` | Create — CLI query tool |

**Note:** All `~/.claude/` paths are relative to the home directory. Hook scripts live in the superpowers plugin hooks directory (`~/.claude/plugins/cache/superpowers-dev/superpowers/5.0.5/hooks/`). Query tool lives in `~/.claude/` directly.

---

## Task 1: SQLite Init + Schema

**Files:**
- Create: `~/.claude/memory/` (directory)
- Create: `~/.claude/memory/init-db.js` — initializes schema

### Steps

- [ ] **Step 1: Create init-db.js**

```js
// ~/.claude/memory/init-db.js
import sqlite3 from 'sqlite3';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DB_PATH = path.join(__dirname, 'sessions.db');

const db = new sqlite3.Database(DB_PATH);

db.exec(`
CREATE TABLE IF NOT EXISTS sessions (
  session_id   TEXT PRIMARY KEY,
  timestamp    INTEGER,
  project      TEXT,
  summary      TEXT,
  operations   TEXT,
  files_modified TEXT TEXT,
  problems     TEXT,
  solutions    TEXT,
  tags         TEXT
);

CREATE TABLE IF NOT EXISTS processed_sessions (
  session_id   TEXT PRIMARY KEY,
  processed_at INTEGER
);

CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
  session_id UNINDEXED,
  summary,
  problems,
  solutions,
  content=sessions,
  content_rowid=rowid
);
`);

console.log('DB initialized at', DB_PATH);
db.close();
```

- [ ] **Step 2: Verify Node.js and sqlite3 are available in hook environment**

Run: `node --version && npm list -g sqlite3 2>/dev/null || echo "sqlite3 not global"`

If sqlite3 not available globally, switch to `sql.js` (WASM — zero native deps):
```js
// switch import to:
import initSqlJs from 'sql.js';
// then:
const SQL = await initSqlJs();
const db = new SQL.Database();
```

- [ ] **Step 3: Run init**

Run: `mkdir -p ~/.claude/memory && node ~/.claude/memory/init-db.js`
Expected: outputs DB path, no error

- [ ] **Step 4: Verify schema**

Run: `node -e "import('sqlite3').then(m=>new m.Database('${env:HOME}/.claude/memory/sessions.db', db=>{db.all(\"SELECT name FROM sqlite_master WHERE type='table'\",[],(e,r)=>{console.log(JSON.stringify(r));db.close()})}))"` (Windows: use %USERPROFILE% or expand ~ manually)

Expected: `sessions`, `processed_sessions`, and `sessions_fts` tables present

- [ ] **Step 5: Commit**

```bash
# No git commit — this is global config in ~/.claude/
```

---

## Task 2: memory-processor.js — Core Parser

**Files:**
- Create: `~/.claude/hooks/memory-processor.js`

### Steps

- [ ] **Step 1: Write the failing shell-execution test first (verify hook can run node)**

Create `memory-processor.js`:
```js
#!/usr/bin/env node
// ~/.claude/hooks/memory-processor.js
// Processes history.jsonl, extracts session memory, writes to SQLite

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HOME = process.env.HOME || process.env.USERPROFILE;
const HISTORY = path.join(HOME, '.claude', 'history.jsonl');
const DB_PATH = path.join(HOME, '.claude', 'memory', 'sessions.db');

function getLastSessionId() {
  // Returns the session_id from the most recent history.jsonl line
  const lines = fs.readFileSync(HISTORY, 'utf8').trim().split('\n').filter(l => l.trim());
  if (lines.length === 0) return null;
  const last = JSON.parse(lines[lines.length - 1]);
  return last.sessionId || null;
}

function getLastProcessedSessionId() {
  // Query processed_sessions table, return most recent processed session_id
  // Returns null if nothing processed yet
}

function main() {
  const lastSessionId = getLastSessionId();
  const lastProcessed = getLastProcessedSessionId();

  if (lastSessionId === lastProcessed) {
    console.log('Already processed, nothing to do');
    return;
  }

  // Extract all lines for sessionId from history.jsonl
  // Parse transcript, classify operations, detect problems/solutions
  // Insert into sessions table + FTS5
  // Insert into processed_sessions
  console.log(JSON.stringify({ lastSessionId, lastProcessed, action: 'processed' }));
}

main();
```

- [ ] **Step 2: Test with real history.jsonl**

Run: `node ~/.claude/hooks/memory-processor.js`
Expected: outputs `{ lastSessionId, lastProcessed, action: 'processed' }` or "Already processed"

- [ ] **Step 3: Verify session extraction logic**

Test with a known session ID — print all history lines for that session, verify project/timestamp/display extraction is correct.

- [ ] **Step 4: Implement full extraction logic**

The processor needs to:
1. Read all history.jsonl lines for the target session_id
2. Extract: `project`, `timestamp` (first line), all `display` values (concatenated transcript)
3. Classify operation types from transcript keywords:
   - `bug`/`fix`/`修复` → bugfix
   - `feat`/`新增`/`新功能` → feature
   - `refactor`/`重构` → refactor
   - `brainstorm`/`讨论` → discussion
   - `research`/`研究` → research
   - else → other
4. Extract file paths from tool calls (Read/Edit/Write paths, Bash file arguments)
5. Detect problems: lines containing `Error`, `failed`, `错误`, `bug`
6. Detect solutions: subsequent lines with successful fixes
7. Build summary from first user prompt + final outcome
8. Generate tags from project name + operation types

```js
// Key extraction function signatures:
function extractSessionEntries(historyLines) {
  // historyLines: all history.jsonl lines for one session_id
  // Returns: { sessionId, timestamp, project, transcript, toolCalls }
}

function classifyOperations(transcript) {
  // Returns: string[] e.g. ['bugfix', 'feature']
}

function extractFilesModified(toolCalls) {
  // Returns: string[] of file paths
}

function extractProblemsAndSolutions(transcript) {
  // Returns: { problems: string, solutions: string }
}

function generateSummary(firstPrompt, outcome) {
  // Returns: string ≤ 200 chars
}
```

- [ ] **Step 5: Write to SQLite with FTS5**

```js
import sqlite3 from 'sqlite3';
const db = new sqlite3.Database(DB_PATH);

function insertSession(entry) {
  return new Promise((resolve, reject) => {
    db.run(`
      INSERT OR REPLACE INTO sessions
        (session_id, timestamp, project, summary, operations, files_modified, problems, solutions, tags)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      entry.session_id,
      entry.timestamp,
      entry.project,
      entry.summary,
      JSON.stringify(entry.operations),
      JSON.stringify(entry.files_modified),
      entry.problems,
      entry.solutions,
      JSON.stringify(entry.tags)
    ], function(err) {
      if (err) return reject(err);
      // FTS index
      db.run(`INSERT INTO sessions_fts(session_id, summary, problems, solutions)
               SELECT session_id, summary, problems, solutions FROM sessions
               WHERE session_id = ?`, [entry.session_id],
        (err2) => err2 ? reject(err2) : resolve()
      );
    });
  });
}
```

- [ ] **Step 6: Mark as processed**

```js
db.run(`INSERT OR REPLACE INTO processed_sessions (session_id, processed_at) VALUES (?, ?)`,
  [sessionId, Date.now()]);
```

- [ ] **Step 7: Test full write pipeline**

Run: `node ~/.claude/hooks/memory-processor.js`
Expected: No error, DB has new row in sessions + processed_sessions

---

## Task 3: memory-query.js — CLI Query Tool

**Files:**
- Create: `~/.claude/memory-query.js`

### Steps

- [ ] **Step 1: Write query tool skeleton**

```js
#!/usr/bin/env node
// ~/.claude/memory-query.js
// Usage: node memory-query.js recent 5
//        node memory-query.js project ai-roundtable
//        node memory-query.js search "NaN bug"
//        node memory-query.js tag bugfix

import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DB_PATH = path.join(process.env.HOME || process.env.USERPROFILE, '.claude', 'memory', 'sessions.db');

const [,, cmd, ...args] = process.argv;

const sqljs = (await import('sql.js')).default;
const SQL = await sqljs();
const db = new SQL.Database();
const buf = await fs.promises.readFile(DB_PATH).catch(() => null);
if (buf) db.importBuffer(buf);

async function queryRecent(n) { /* returns last n sessions */ }
async function queryByProject(p) { /* returns sessions for project */ }
async function searchFTS(q) { /* full-text search */ }
async function queryByTag(t) { /* filter by tag */ }
async function stats() { /* session count, project breakdown */ }

const commands = { recent, project: queryByProject, search: searchFTS, tag: queryByTag, stats };
if (!commands[cmd]) { console.error('Usage: node memory-query.js <recent|project|search|tag|stats>'); process.exit(1); }
const result = await commands[cmd](...args);
console.log(JSON.stringify(result, null, 2));
```

- [ ] **Step 2: Implement each query function using sql.js FTS5 MATCH**

```js
async function searchFTS(q) {
  const stmt = db.prepare(`
    SELECT s.*, bm25(sessions_fts) as rank
    FROM sessions_fts
    JOIN sessions s ON sessions_fts.rowid = s.rowid
    WHERE sessions_fts MATCH ?
    ORDER BY rank
    LIMIT 20
  `);
  stmt.bind([q + '*']);
  const rows = [];
  while (stmt.step()) rows.push(stmt.getAsObject());
  return rows;
}
```

- [ ] **Step 3: Test each command**

```bash
node ~/.claude/memory-query.js recent 3
node ~/.claude/memory-query.js project ai-roundtable
node ~/.claude/memory-query.js search "bugfix"
node ~/.claude/memory-query.js tag quality-scorer
node ~/.claude/memory-query.js stats
```

- [ ] **Step 4: Format output as plain text**

Replace JSON output with human-readable terminal format:
```
=== Recent Sessions ===
[2026-04-01] ai-roundtable | Cognitive Annealing quality scorer implemented
  tags: [ai-roundtable, quality-scorer] | files: shared/qualityScorer.js
```

- [ ] **Step 5: Commit**

No git commit — global tool in `~/.claude/`.

---

## Task 4: Startup Hook Integration

**Files:**
- Modify: `~/.claude/plugins/cache/superpowers-dev/superpowers/5.0.5/hooks/session-start-memory`
- Modify: `~/.claude/plugins/cache/superpowers-dev/superpowers/5.0.5/hooks/hooks.json`

### Steps

- [ ] **Step 1: Create session-start-memory bash script**

```bash
#!/usr/bin/env bash
# ~/.claude/plugins/cache/superpowers-dev/superpowers/5.0.5/hooks/session-start-memory
# Chains from session-start; runs after main session-start hook

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MEMORY_PROC="${HOOK_DIR}/hooks/memory-processor.js"

# Run memory processor (it checks internally if there's work to do)
node "$MEMORY_PROC" 2>/dev/null || true

# Load recent memory for context injection
MEMORY_QUERY="${HOME}/.claude/memory-query.js"
if [ -f "$MEMORY_QUERY" ]; then
  RECENT=$(node "$MEMORY_QUERY" recent 3 2>/dev/null || echo "")
  if [ -n "$RECENT" ]; then
    echo "Recent memory:" >&2
    echo "$RECENT" >&2
  fi
fi
```

- [ ] **Step 2: Modify hooks.json to chain session-start-memory**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          },
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start-memory",
            "async": true
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 3: Test startup chain**

Close and reopen Claude Code, or trigger SessionStart manually to verify memory processor runs.

---

## Task 5: MEMORY.md Compatibility + End-to-End

### Steps

- [ ] **Step 1: Add MEMORY.md append to memory-processor.js**

After writing to SQLite, also append to project-level MEMORY.md:

```js
function appendToMemoryMd(entry) {
  const MEMORY_DIR = path.join(HOME, '.claude', 'projects');
  const memPath = path.join(MEMORY_DIR, entry.project, 'MEMORY.md');
  const line = `| ${new Date(entry.timestamp).toISOString().slice(0,10)} | ${entry.session_id} | ${entry.summary} |`;
  // Append to Session History table in MEMORY.md
  // Find the table, insert line before the closing |
}
```

- [ ] **Step 2: Create ~/.claude/projects/ directory if missing**

```js
if (!fs.existsSync(path.join(HOME, '.claude', 'projects'))) {
  fs.mkdirSync(path.join(HOME, '.claude', 'projects'), { recursive: true });
}
```

- [ ] **Step 3: End-to-end test**

1. Run `node ~/.claude/hooks/memory-processor.js`
2. Verify sessions.db has new row: `node -e "const SQL=require('sql.js');..."`
3. Verify `node ~/.claude/memory-query.js recent 3` shows it
4. Verify project-level MEMORY.md was updated (if project dir exists)
5. Close/reopen Claude Code, verify SessionStart runs without error

---

## Verification

Run all query commands, verify:
1. `recent 3` returns last 3 sessions with correct project/summary
2. `project ai-roundtable` filters correctly
3. `search "bugfix"` returns relevant results via FTS5
4. `stats` shows session count and project breakdown
5. No crashes on empty DB, missing project dirs, or malformed history.jsonl
