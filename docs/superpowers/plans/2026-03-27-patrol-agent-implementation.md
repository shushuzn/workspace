# Patrol Agent — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a fully autonomous continuous patrol agent that runs as a standalone Node.js process, patrolling the workspace for plans, lint errors, test failures, and code optimization opportunities.

**Architecture:** Standalone ESM Node.js project at `.omc/patrol-agent/`. Reads/writes patrol state to `~/.omc/patrol-state.json`. Invokes Claude Code CLI via `claude` command for plan execution. No external API dependencies in Phase 1. Patrol loop is timer-free — driven by async/await with configurable sleep intervals.

**Tech Stack:** Node.js ESM, `dotenv`, `https-proxy-agent`, file system APIs, `child_process` for Claude CLI invocation.

**Workspace root:** `D:/OpenClaw/workspace`
**State file:** `~/.omc/patrol-state.json` (cross-platform homedir)
**Plans dir:** `D:/OpenClaw/workspace/docs/superpowers/plans/`

---

## File Structure

```
omc/patrol-agent/
├── package.json          # ESM project, minimal deps
├── src/
│   ├── index.js         # Entry point — main loop
│   ├── state.js         # State load/save (patrol-state.json)
│   ├── plans.js          # Plan discovery, sort, status update
│   ├── git.js           # Git conflict detection, file status
│   ├── lint.js          # Lint check (eslint or surface scan)
│   └── executor.js      # Execute plan via claude CLI
├── plans/                # (created by this agent)
└── .env.local           # (optional) MINIMAX_API_KEY if needed
```

---

## Phase 1 Tasks: Core Loop (Day 1)

### Task 1: Project scaffolding — `package.json`

- [ ] **Step 1: Create `.omc/patrol-agent/` directory**

```bash
mkdir -p .omc/patrol-agent/src
```

- [ ] **Step 2: Create `package.json`**

```json
{
  "name": "patrol-agent",
  "version": "1.0.0",
  "type": "module",
  "description": "Autonomous workspace patrol agent",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "patrol": "node src/index.js"
  },
  "dependencies": {
    "dotenv": "^16.0.0",
    "https-proxy-agent": "^8.0.0"
  }
}
```

- [ ] **Step 3: Create `.omc/patrol-agent/.gitignore`**

```
node_modules/
patrol-state.json
*.log
```

- [ ] **Step 4: Run `npm install` in `.omc/patrol-agent/`**

```bash
cd .omc/patrol-agent && npm install
```

- [ ] **Step 5: Commit**

```bash
git add .omc/patrol-agent/package.json .omc/patrol-agent/src
git commit -m "feat(patrol): scaffold patrol agent project"
```

---

### Task 2: State management — `state.js`

**File:** Create `.omc/patrol-agent/src/state.js`

- [ ] **Step 1: Write `state.js`**

```javascript
// ~/.omc/patrol-agent/src/state.js
// Loads and saves patrol-state.json with cross-platform homedir support

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import os from 'os';

// Resolve ~/.omc/patrol-state.json
function getStatePath() {
  const home = os.homedir();
  const omcDir = join(home, '.omc');
  return join(omcDir, 'patrol-state.json');
}

function ensureOmcDir() {
  const home = os.homedir();
  const omcDir = join(home, '.omc');
  if (!existsSync(omcDir)) {
    mkdirSync(omcDir, { recursive: true });
  }
  return omcDir;
}

export function loadState() {
  const statePath = getStatePath();
  try {
    if (existsSync(statePath)) {
      const raw = readFileSync(statePath, 'utf-8');
      return JSON.parse(raw);
    }
  } catch (err) {
    // Corrupt state — start fresh
  }
  // Default state
  return {
    last_patrol: null,
    loop_count: 0,
    completed_actions: [],
    skipped: [],
    research_topics: [],
    patrol_log: [],
    running: false,
  };
}

export function saveState(state) {
  const statePath = getStatePath();
  ensureOmcDir();
  try {
    writeFileSync(statePath, JSON.stringify(state, null, 2), 'utf-8');
  } catch (err) {
    console.error('[patrol] Failed to save state:', err.message);
  }
}

export function getStatePath() {
  return getStatePath();
}
```

- [ ] **Step 2: Create test file `test/state.js`** (minimal smoke test)

```javascript
// test/state.test.js
import { loadState, saveState, getStatePath } from '../src/state.js';
import { existsSync, unlinkSync } from 'fs';
import { ok, equal } from 'assert';

const path = getStatePath();

// loadState returns object with expected fields
const state = loadState();
ok(typeof state.loop_count === 'number', 'loop_count is number');
ok(Array.isArray(state.completed_actions), 'completed_actions is array');
ok(Array.isArray(state.skipped), 'skipped is array');
ok(Array.isArray(state.patrol_log), 'patrol_log is array');

// saveState round-trips
const original = loadState();
const modified = { ...original, loop_count: original.loop_count + 1 };
saveState(modified);
const reloaded = loadState();
equal(reloaded.loop_count, modified.loop_count, 'state round-trips correctly');

// Restore original
saveState(original);
console.log('state.js: all tests passed');
```

- [ ] **Step 3: Run smoke test**

```bash
node --test test/state.test.js
# Expected: passed
```

- [ ] **Step 4: Commit**

```bash
git add .omc/patrol-agent/src/state.js .omc/patrol-agent/test/state.test.js
git commit -m "feat(patrol): add state management module"
```

---

### Task 3: Plan management — `plans.js`

**File:** Create `.omc/patrol-agent/src/plans.js`

- [ ] **Step 1: Write `plans.js`**

```javascript
// ~/.omc/patrol-agent/src/plans.js
// Discover, sort, and update plan files in docs/superpowers/plans/

import { readdirSync, readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const PLANS_DIR = 'D:/OpenClaw/workspace/docs/superpowers/plans';

export function getPendingPlans() {
  if (!existsSync(PLANS_DIR)) return [];

  const files = readdirSync(PLANS_DIR).filter(f => f.endsWith('.md'));

  /** @type {Array<{id: string, file: string, status: string, hash: string, updated_at: string, frontmatter: object}>} */
  const plans = [];

  for (const file of files) {
    const filePath = join(PLANS_DIR, file);
    let raw;
    try {
      raw = readFileSync(filePath, 'utf-8');
    } catch {
      continue;
    }

    // Parse frontmatter: lines between first `---` markers
    const fmMatch = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
    if (!fmMatch) continue;

    const frontmatter = {};
    for (const line of fmMatch[1].split('\n')) {
      const colonIdx = line.indexOf(':');
      if (colonIdx === -1) continue;
      const key = line.slice(0, colonIdx).trim();
      const val = line.slice(colonIdx + 1).trim();
      frontmatter[key] = val;
    }

    const status = frontmatter.status || 'pending';
    if (status !== 'pending' && status !== 'in_progress') continue;

    plans.push({
      id: frontmatter.id || file.replace('.md', ''),
      file: filePath,
      status,
      hash: frontmatter.hash || '',
      updated_at: frontmatter.updated_at || '',
      frontmatter,
    });
  }

  // Sort by updated_at ascending (oldest first)
  plans.sort((a, b) => {
    const ta = new Date(a.updated_at || 0).getTime();
    const tb = new Date(b.updated_at || 0).getTime();
    return ta - tb;
  });

  return plans;
}

export function markPlanDone(plan) {
  updatePlanStatus(plan, 'done');
}

export function markPlanSkipped(plan, reason) {
  // Append to skipped list in frontmatter
  updatePlanStatus(plan, 'skipped');
}

function updatePlanStatus(plan, status) {
  const filePath = plan.file;
  let raw;
  try {
    raw = readFileSync(filePath, 'utf-8');
  } catch {
    return;
  }

  // Replace status in frontmatter
  const updated = raw.replace(
    /^(---\r?\n)([\s\S]*?)(\r?\n---\r?\n)/,
    (_, open, fm, close) => {
      const lines = fm.split('\n').map(line => {
        if (line.startsWith('status:')) return `status: ${status}`;
        if (line.startsWith('updated_at:')) return `updated_at: ${new Date().toISOString()}`;
        return line;
      });
      return open + lines.join('\n') + close;
    }
  );

  try {
    writeFileSync(filePath, updated, 'utf-8');
  } catch {
    // Log but don't fail
  }
}
```

- [ ] **Step 2: Write minimal test `test/plans.test.js`**

```javascript
// test/plans.test.js
import { getPendingPlans } from '../src/plans.js';
import { ok, greaterOrEqual } from 'assert';

const plans = getPendingPlans();
// Returns array (possibly empty)
ok(Array.isArray(plans), 'returns array');
if (plans.length > 0) {
  const p = plans[0];
  ok(typeof p.id === 'string', 'plan has id');
  ok(typeof p.file === 'string', 'plan has file');
  ok(p.updated_at !== undefined, 'plan has updated_at');
}
console.log(`plans.js: found ${plans.length} pending plans`);
```

- [ ] **Step 3: Run test**

```bash
node --test test/plans.test.js
```

- [ ] **Step 4: Commit**

```bash
git add .omc/patrol-agent/src/plans.js .omc/patrol-agent/test/plans.test.js
git commit -m "feat(patrol): add plan discovery module"
```

---

### Task 4: Git integration — `git.js`

**File:** Create `.omc/patrol-agent/src/git.js`

- [ ] **Step 1: Write `git.js`**

```javascript
// ~/.omc/patrol-agent/src/git.js
// Git conflict detection: check if files have uncommitted local changes

import { execSync } from 'child_process';
import { existsSync } from 'fs';

const WORKSPACE_ROOT = 'D:/OpenClaw/workspace';

function git(args, cwd = WORKSPACE_ROOT) {
  try {
    return execSync(`git ${args}`, { cwd, encoding: 'utf-8', timeout: 15000 });
  } catch (err) {
    return err.stdout || '';
  }
}

/**
 * Check if any of the given files have uncommitted working-tree changes.
 * Returns true if conflict detected (files modified locally).
 * @param {string[]} files
 * @returns {boolean}
 */
export function hasWorkingTreeChanges(files) {
  if (!files || files.length === 0) return false;

  const status = git('status --porcelain', WORKSPACE_ROOT);
  const modifiedFiles = status
    .split('\n')
    .filter(line => line.startsWith(' M ') || line.startsWith(' M'))
    .map(line => line.slice(3).trim());

  for (const file of files) {
    // Normalize to workspace-relative path
    const relPath = file.replace(/^[A-Z]:[\/\\]/i, '').replace(/\\/g, '/');
    if (modifiedFiles.some(f => f === relPath || f.endsWith(relPath))) {
      return true;
    }
  }
  return false;
}

/**
 * Get list of all changed files (vs HEAD) in workspace.
 * @returns {string[]}
 */
export function getChangedFiles() {
  const status = git('status --porcelain', WORKSPACE_ROOT);
  return status
    .split('\n')
    .filter(line => line.length > 3)
    .map(line => line.slice(3).trim());
}

/**
 * Create a new branch for patrol changes.
 * @param {string} branchName
 * @returns {string} branch name
 */
export function createBranch(branchName) {
  git(`checkout -b ${branchName}`, WORKSPACE_ROOT);
  return branchName;
}

/**
 * Get current branch name.
 * @returns {string}
 */
export function getCurrentBranch() {
  return git('rev-parse --abbrev-ref HEAD', WORKSPACE_ROOT).trim();
}
```

- [ ] **Step 2: Write test `test/git.test.js`**

```javascript
// test/git.test.js
import { hasWorkingTreeChanges, getChangedFiles, getCurrentBranch } from '../src/git.js';
import { ok, equal } from 'assert';

const branch = getCurrentBranch();
ok(typeof branch === 'string' && branch.length > 0, 'getCurrentBranch returns non-empty string');

const changed = getChangedFiles();
ok(Array.isArray(changed), 'getChangedFiles returns array');

// hasWorkingTreeChanges with empty array returns false
equal(hasWorkingTreeChanges([]), false, 'empty files = no conflict');

console.log(`git.js: branch=${branch}, changed=${changed.length} files`);
```

- [ ] **Step 3: Run test**

```bash
node --test test/git.test.js
```

- [ ] **Step 4: Commit**

```bash
git add .omc/patrol-agent/src/git.js .omc/patrol-agent/test/git.test.js
git commit -m "feat(patrol): add git conflict detection module"
```

---

### Task 5: Lint checker — `lint.js`

**File:** Create `.omc/patrol-agent/src/lint.js`

- [ ] **Step 1: Write `lint.js`**

```javascript
// ~/.omc/patrol-agent/src/lint.js
// Check for lint errors in workspace projects
// Uses eslint if project has eslint.config.js or .eslintrc, else surface scan

import { execSync } from 'child_process';
import { existsSync, readdirSync } from 'fs';
import { join } from 'path';

const WORKSPACE_ROOT = 'D:/OpenClaw/workspace';

function findEslintConfig(dir) {
  const candidates = [
    'eslint.config.js', 'eslint.config.mjs', 'eslint.config.cjs',
    '.eslintrc', '.eslintrc.js', '.eslintrc.json', '.eslintrc.yaml',
  ];
  for (const c of candidates) {
    if (existsSync(join(dir, c))) return join(dir, c);
  }
  return null;
}

function getJsFiles(dir, patterns = ['src/', ''], maxDepth = 3) {
  const files = [];
  function scan(subdir, depth) {
    if (depth > maxDepth) return;
    try {
      const entries = readdirSync(subdir, { withFileTypes: true });
      for (const entry of entries) {
        if (entry.isDirectory() && !entry.name.startsWith('.') && !entry.name.startsWith('node_modules')) {
          scan(join(subdir, entry.name), depth + 1);
        } else if (entry.isFile() && (entry.name.endsWith('.js') || entry.name.endsWith('.jsx') || entry.name.endsWith('.ts') || entry.name.endsWith('.tsx'))) {
          files.push(join(subdir, entry.name));
        }
      }
    } catch { /* skip inaccessible dirs */ }
  }
  scan(dir, 0);
  return files;
}

const PROJECT_DIRS = [
  'D:/OpenClaw/workspace/80-PROJECTS/agent-arena',
  'D:/OpenClaw/workspace/80-PROJECTS/ai-roundtable',
  'D:/OpenClaw/workspace/80-PROJECTS/star-forge-web',
];

export function checkLint() {
  /** @type {Array<{project: string, errors: number, output: string}>} */
  const results = [];

  for (const projectDir of PROJECT_DIRS) {
    if (!existsSync(projectDir)) continue;

    const eslintConfig = findEslintConfig(projectDir);
    if (eslintConfig) {
      try {
        const output = execSync(
          `npx eslint . --max-warnings 0 --format json`,
          { cwd: projectDir, encoding: 'utf-8', timeout: 60000, stdio: ['pipe', 'pipe', 'pipe'] }
        );
        let parsed;
        try {
          parsed = JSON.parse(output);
        } catch {
          parsed = [];
        }
        const totalErrors = parsed.reduce((sum, f) => sum + (f.errorCount || 0), 0);
        results.push({ project: projectDir.split('/').pop(), errors: totalErrors, output: '' });
      } catch (err) {
        // eslint failed or found errors (exit code != 0)
        const output = err.stdout || '';
        let parsed;
        try {
          parsed = JSON.parse(output);
        } catch {
          parsed = [];
        }
        const totalErrors = parsed.reduce((sum, f) => sum + (f.errorCount || 0), 0);
        results.push({ project: projectDir.split('/').pop(), errors: totalErrors, output });
      }
    } else {
      // No eslint config — skip for now (surface scan in Phase 3)
      results.push({ project: projectDir.split('/').pop(), errors: 0, output: 'no-eslint-config' });
    }
  }

  return results;
}

export function hasLintErrors() {
  const results = checkLint();
  return results.some(r => r.errors > 0);
}
```

- [ ] **Step 2: Write test `test/lint.test.js`**

```javascript
// test/lint.test.js
import { checkLint, hasLintErrors } from '../src/lint.js';
import { ok, equal } from 'assert';

const results = checkLint();
ok(Array.isArray(results), 'checkLint returns array');

for (const r of results) {
  ok(typeof r.project === 'string', `project name: ${r.project}`);
  ok(typeof r.errors === 'number', `errors is number for ${r.project}`);
  if (r.errors === 0) {
    console.log(`  ${r.project}: ${r.errors} errors`);
  } else {
    console.log(`  ${r.project}: ${r.errors} ERRORS`);
  }
}

const hasErrors = hasLintErrors();
equal(typeof hasErrors, 'boolean', 'hasLintErrors returns boolean');

console.log('lint.js: checked', results.length, 'projects');
```

- [ ] **Step 3: Run test**

```bash
node --test test/lint.test.js
```

- [ ] **Step 4: Commit**

```bash
git add .omc/patrol-agent/src/lint.js .omc/patrol-agent/test/lint.test.js
git commit -m "feat(patrol): add lint checker module"
```

---

### Task 6: Plan executor — `executor.js`

**File:** Create `.omc/patrol-agent/src/executor.js`

- [ ] **Step 1: Write `executor.js`**

```javascript
// ~/.omc/patrol-agent/src/executor.js
// Execute a plan by invoking claude CLI with instructions
// Reads plan content and feeds it as context to claude

import { readFileSync } from 'fs';
import { execSync } from 'child_process';
import { join } from 'path';

const WORKSPACE_ROOT = 'D:/OpenClaw/workspace';

/**
 * Execute a plan file using claude CLI.
 * The plan content is read and passed as context.
 * @param {{ id: string, file: string, frontmatter: object }} plan
 * @returns {{ success: boolean, output: string }}
 */
export function executePlan(plan) {
  let planContent;
  try {
    planContent = readFileSync(plan.file, 'utf-8');
  } catch (err) {
    return { success: false, output: `Failed to read plan: ${err.message}` };
  }

  // Extract markdown body (skip frontmatter)
  const bodyMatch = planContent.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n([\s\S]*)$/);
  const body = bodyMatch ? bodyMatch[1].trim() : planContent;

  // Build the claude command instruction
  const instruction = `Execute the following plan:\n\n# Plan: ${plan.id}\n\n${body}`;

  try {
    // Use claude --print with the instruction
    // The claude CLI will execute the task autonomously
    const output = execSync(
      `claude --print "${instruction.replace(/"/g, '\\"')}"`,
      {
        cwd: WORKSPACE_ROOT,
        encoding: 'utf-8',
        timeout: 300000, // 5 min per plan
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, CLAUDE_NO_CHECK_UPDATE: '1' },
      }
    );
    return { success: true, output: output.trim() };
  } catch (err) {
    return { success: false, output: err.stdout || err.message };
  }
}

/**
 * Fix lint errors in a project by running eslint --fix.
 * @param {string} projectDir
 * @returns {{ success: boolean, output: string }}
 */
export function fixLintErrors(projectDir) {
  try {
    const output = execSync(
      `npx eslint . --fix --max-warnings 0`,
      { cwd: projectDir, encoding: 'utf-8', timeout: 120000, stdio: ['pipe', 'pipe', 'pipe'] }
    );
    return { success: true, output: output || 'lint fixed' };
  } catch (err) {
    return { success: false, output: err.stdout || err.message };
  }
}
```

- [ ] **Step 2: Commit executor module (no test — requires claude CLI)**

```bash
git add .omc/patrol-agent/src/executor.js
git commit -m "feat(patrol): add plan executor module"
```

---

### Task 7: Main patrol loop — `index.js`

**File:** Create `.omc/patrol-agent/src/index.js`

- [ ] **Step 1: Write `index.js`**

```javascript
// ~/.omc/patrol-agent/src/index.js
// Main patrol loop — the heart of the patrol agent

import { loadState, saveState } from './state.js';
import { getPendingPlans, markPlanDone, markPlanSkipped } from './plans.js';
import { hasWorkingTreeChanges, createBranch, getCurrentBranch } from './git.js';
import { checkLint, hasLintErrors } from './lint.js';
import { executePlan, fixLintErrors } from './executor.js';
import { setTimeout as sleep } from 'timers/promises';

const WORKSPACE_ROOT = 'D:/OpenClaw/workspace';
const LOOP_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
const MAX_RETRIES = 2;

let running = true;
let loopCount = 0;

// Handle shutdown signals gracefully
for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, () => {
    console.log(`\n[patrol] Received ${sig}, shutting down after current loop...`);
    running = false;
  });
}

function log(msg) {
  const ts = new Date().toISOString().replace('T', ' ').slice(0, 19);
  console.log(`[${ts}] ${msg}`);
}

function patrolLog(state, entry) {
  state.patrol_log = [entry, ...state.patrol_log].slice(0, 50); // Keep last 50
  saveState(state);
}

async function runLoop() {
  loopCount++;
  const state = loadState();
  state.loop_count = loopCount;
  state.last_patrol = new Date().toISOString();
  state.running = true;
  saveState(state);

  const actions = [];
  let didWork = false;

  // ─── 1. Execute pending plans ───────────────────────────────────────────
  const pendingPlans = getPendingPlans();
  if (pendingPlans.length > 0) {
    const plan = pendingPlans[0];
    log(`📋 Plan: ${plan.id} (${plan.file})`);

    const actionHash = `${plan.id}:${plan.hash || Date.now()}`;
    const alreadyDone = state.completed_actions.some(a => a.type === 'plan' && a.id === plan.id && a.hash === plan.hash);
    if (alreadyDone) {
      log(`  ⏭ Already executed, skipping.`);
    } else {
      let retryCount = 0;
      let success = false;
      while (retryCount <= MAX_RETRIES && !success) {
        const result = executePlan(plan);
        if (result.success) {
          success = true;
          markPlanDone(plan);
          state.completed_actions.push({
            type: 'plan',
            id: plan.id,
            hash: plan.hash || '',
            executed_at: new Date().toISOString(),
          });
          actions.push(`✓ Executed: ${plan.id}`);
          log(`  ✓ Done.`);
          didWork = true;
        } else {
          retryCount++;
          if (retryCount <= MAX_RETRIES) {
            log(`  ⚠ Retry #${retryCount} for: ${plan.id}: ${result.output.slice(0, 100)}`);
            await sleep(5000); // 5s backoff
          } else {
            log(`  ⚠ Skipped permanently: ${plan.id} | Error: ${result.output.slice(0, 200)}`);
            state.skipped.push({
              type: 'plan',
              id: plan.id,
              reason: result.output.slice(0, 200),
              at: new Date().toISOString(),
            });
            markPlanSkipped(plan, result.output);
            actions.push(`⚠ Skipped: ${plan.id}`);
            success = true; // Mark done to avoid re-trying
            didWork = true;
          }
        }
      }
    }
  }

  // ─── 2. Check and fix lint errors ───────────────────────────────────────
  if (!didWork || loopCount % 1 === 0) { // Always check if no plan was run
    const lintResults = checkLint();
    const projectsWithErrors = lintResults.filter(r => r.errors > 0);

    if (projectsWithErrors.length > 0) {
      for (const lr of projectsWithErrors) {
        if (lr.output === 'no-eslint-config') continue;
        log(`🔧 Lint errors in ${lr.project}: ${lr.errors} errors`);
        // Phase 1: just report, fix in Phase 3
        actions.push(`⚠ ${lr.errors} lint errors in ${lr.project} (fix in Phase 3)`);
        didWork = true;
      }
    }
  }

  // ─── 3. Optimization scan (every 10 loops) ─────────────────────────────
  if (loopCount % 10 === 0) {
    // Phase 3 feature — placeholder for now
    log(`[patrol] Optimization scan #${loopCount} (deferred to Phase 3)`);
  }

  // ─── 4. Research (every 50 loops) ─────────────────────────────────────
  if (loopCount % 50 === 0) {
    log(`[patrol] Research scan #${loopCount} (deferred to Phase 2)`);
  }

  // ─── 5. Patrol log ───────────────────────────────────────────────────
  const entry = {
    loop: loopCount,
    timestamp: new Date().toISOString(),
    actions,
    didWork,
  };
  patrolLog(state, entry);

  if (actions.length > 0) {
    log(`Loop #${loopCount} summary: ${actions.join(' | ')}`);
  } else {
    log(`Loop #${loopCount} — nothing to do.`);
  }

  log(`Next: Loop #${loopCount + 1} in ~${LOOP_INTERVAL_MS / 60000}min | Pending plans: ${pendingPlans.length}`);

  state.running = false;
  saveState(state);
}

async function main() {
  const state = loadState();

  if (state.running) {
    log('Patrol already running (check ~/.omc/patrol-state.json). Exiting.');
    process.exit(1);
  }

  log(`🚀 Patrol agent starting — loop_count resumes from ${state.loop_count}`);
  log(`   Workspace: ${WORKSPACE_ROOT}`);
  log(`   Plans dir: D:/OpenClaw/workspace/docs/superpowers/plans/`);
  log(`   Press Ctrl+C to stop.`);
  log('─'.repeat(60));

  while (running) {
    await runLoop();
    if (running) {
      try {
        await sleep(LOOP_INTERVAL_MS);
      } catch {
        // Interrupted
        break;
      }
    }
  }

  log('[patrol] Patrol loop stopped.');
}

main().catch(err => {
  console.error('[patrol] Fatal error:', err);
  process.exit(1);
});
```

- [ ] **Step 2: Create `.env.example`**

```bash
# .omc/patrol-agent/.env.example
# Optional: if patrol agent needs MiniMax API for research (Phase 2)
# MINIMAX_API_KEY=your_key_here
```

- [ ] **Step 3: Run smoke test (dry-run import check)**

```bash
cd .omc/patrol-agent && node --check src/index.js
# Expected: no syntax errors
```

- [ ] **Step 4: Commit**

```bash
git add .omc/patrol-agent/src/index.js .omc/patrol-agent/.env.example
git commit -m "feat(patrol): add main patrol loop"
```

---

## Phase 2 Tasks: Research Integration (Day 2)

### Task 8: Web research module — `research.js`

**New file:** `.omc/patrol-agent/src/research.js`

Research integration using GitHub API (public, no auth needed for search) and arXiv public API.

- [ ] **Implement `research.js`** with:
  - `searchGitHub(query)` — GitHub REST API search (public endpoint)
  - `searchArxiv(query)` — arXiv Atom feed search
  - `deepResearch(topic)` — combined search, returns ranked ideas
  - Each idea: `{ title, url, summary, confidence: 0.0-1.0, source }`

**Output format for ideas:**
```javascript
{
  title: "LLM Memory System for Agents",
  url: "https://github.com/...",
  summary: "Persistent memory architecture for LLM agents...",
  confidence: 0.85,
  source: "github",
  generated_at: new Date().toISOString(),
}
```

- [ ] **Write test `test/research.test.js`** (can use recorded responses or mock)
- [ ] **Commit**

### Task 9: Research-driven plan writer — `planWriter.js`

**New file:** `.omc/patrol-agent/src/planWriter.js`

- [ ] **Implement `writePlanFromResearch(idea)`** that creates a new plan file in `docs/superpowers/plans/` with:
  - Frontmatter: `status: pending`, `hash: sha256(idea.title + idea.url)`, `generated_from: research`, `source_url`, `confidence`, `generated_at`
  - Markdown body: `# Plan: ${idea.title}`, research source, summary, why it fits, suggested implementation

- [ ] **Write test**
- [ ] **Commit**

### Task 10: Integrate research into main loop

Modify `index.js` to call `deepResearch()` every 50 loops, filter by confidence > 0.7, write plans.

- [ ] **Update `index.js`** with research integration
- [ ] **Commit**

---

## Phase 3 Tasks: Error Recovery + Hash Deduplication (Day 3)

### Task 11: Retry + skip logic (already in index.js loop, but verify)

The `executePlan` function in `executor.js` already handles retries. Verify the loop correctly tracks `retryCount` and calls `markPlanSkipped` on permanent failure.

- [ ] **Review and confirm** `executor.js` retry logic matches spec
- [ ] **Commit** (likely no changes)

### Task 12: Hash deduplication for files

Enhance `git.js` to compute SHA256 of file contents before modification, compare with git HEAD hash. Skip if identical.

- [ ] **Add `fileHash(path)`** to `git.js` — `git hash-object <file>`
- [ ] **Update `index.js`** — before modifying a file, check `fileHash(target) === gitHash(target)`. If same, skip.
- [ ] **Commit**

### Task 13: Git conflict auto-branch

Enhance `git.js` with `autoBranchForConflict(files)` — if `hasWorkingTreeChanges(files)`, create `patrol/auto-{timestamp}` branch.

- [ ] **Update `index.js`** to call `autoBranchForConflict` when about to modify conflicting files
- [ ] **Commit**

---

## Phase 4 Tasks: Integration + Polish (Day 4)

### Task 14: CLI entry point script

Create a convenient launcher at `D:/OpenClaw/workspace/patrol.sh` (or `.bat` for Windows).

**Windows batch file** `D:/OpenClaw/workspace/patrol.bat`:
```batch
@echo off
cd /d "%~dp0"
echo Starting patrol agent...
nohup node .omc/patrol-agent/src/index.js > .omc/patrol.log 2>&1 &
echo Patrol agent started in background. See .omc/patrol.log for output.
pause
```

- [ ] **Create `patrol.bat`**
- [ ] **Commit**

### Task 15: README

Create `D:/OpenClaw/workspace/.omc/patrol-agent/README.md` with:
- How to start/stop
- How to add plans
- How to view patrol state
- How to check logs

- [ ] **Commit**

---

## Task Summary Table

| Phase | Task | File | Description |
|-------|------|------|-------------|
| 1 | 1 | `package.json` | Scaffold project |
| 1 | 2 | `src/state.js` | State load/save |
| 1 | 3 | `src/plans.js` | Plan discovery + sort |
| 1 | 4 | `src/git.js` | Git conflict detection |
| 1 | 5 | `src/lint.js` | Lint checker |
| 1 | 6 | `src/executor.js` | Plan executor via claude CLI |
| 1 | 7 | `src/index.js` | Main patrol loop |
| 2 | 8 | `src/research.js` | GitHub + arXiv research |
| 2 | 9 | `src/planWriter.js` | Write plans from research |
| 2 | 10 | `src/index.js` | Integrate research into loop |
| 3 | 11 | `src/executor.js` | Verify retry logic |
| 3 | 12 | `src/git.js` | Hash deduplication |
| 3 | 13 | `src/git.js` | Auto-branch for conflicts |
| 4 | 14 | `patrol.bat` | CLI launcher |
| 4 | 15 | `README.md` | Documentation |

---

## Verification

After Phase 1 (Task 7), verify:
1. `node --check .omc/patrol-agent/src/index.js` — no syntax errors
2. `node .omc/patrol-agent/src/index.js` — runs for 1 loop and exits cleanly (set `LOOP_INTERVAL_MS = 1000` for test)
3. `~/.omc/patrol-state.json` is created with correct structure
4. Plans in `docs/superpowers/plans/` are discovered and sorted by `updated_at`
