#!/usr/bin/env node
/**
 * OMC Subagent Pipeline
 * Structured parallel RPC-based subagent execution.
 *
 * Inspired by Hermes Agent's Subagent Pipeline:
 *   - Tasks split into parallel sub-agent calls
 *   - RPC-style request/response with structured output
 *   - Result aggregation + error handling
 *   - Timeout + retry logic
 *   - Audit trail
 *
 * Usage:
 *   node subagent-pipeline.mjs --plan "task description"   # plan task breakdown
 *   node subagent-pipeline.mjs --run plan.json            # execute plan
 *   node subagent-pipeline.mjs --status                     # show pipeline status
 *
 * Architecture:
 *   - Plans stored in .omc/state/subagent-plans/
 *   - Results in .omc/state/subagent-results/
 *   - State in .omc/state/subagent-pipeline.json
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const PLANS_DIR = resolve(__dirname, '../state/subagent-plans');
const RESULTS_DIR = resolve(__dirname, '../state/subagent-results');
const STATE_FILE = resolve(__dirname, '../state/subagent-pipeline.json');
const MAX_PARALLEL = 3;
const DEFAULT_TIMEOUT = 120000; // 2 min

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

function readState() {
  if (!existsSync(STATE_FILE)) return { plans: [], active: null };
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return { plans: [], active: null }; }
}

function writeState(state) {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

function savePlan(plan) {
  if (!existsSync(PLANS_DIR)) mkdirSync(PLANS_DIR, { recursive: true });
  const id = plan.id || `plan-${Date.now()}`;
  const path = resolve(PLANS_DIR, `${id}.json`);
  writeFileSync(path, JSON.stringify(plan, null, 2), 'utf-8');
  return { id, path };
}

function loadPlan(id) {
  const path = resolve(PLANS_DIR, `${id}.json`);
  if (!existsSync(path)) {
    // Try as full path
    if (existsSync(id)) {
      return JSON.parse(readFileSync(id, 'utf-8'));
    }
    return null;
  }
  return JSON.parse(readFileSync(path, 'utf-8'));
}

function saveResult(planId, subagentId, result) {
  if (!existsSync(RESULTS_DIR)) mkdirSync(RESULTS_DIR, { recursive: true });
  const path = resolve(RESULTS_DIR, `${planId}-${subagentId}.json`);
  writeFileSync(path, JSON.stringify(result, null, 2), 'utf-8');
  return path;
}

// ── Task planner ─────────────────────────────────────────────────────────────
function planTask(task) {
  // Analyze task → split into subagent tasks
  const subtasks = [];

  // Pattern-based task decomposition
  if (task.match(/search|find|explore/i)) {
    subtasks.push({
      id: 'researcher',
      role: 'researcher',
      description: `Research and gather information: ${task}`,
      agentType: 'Explore',
      timeout: 60000,
      priority: 1,
    });
  }

  if (task.match(/code|implement|build|create/i)) {
    subtasks.push({
      id: 'coder',
      role: 'coder',
      description: `Implement code: ${task}`,
      agentType: 'general-purpose',
      timeout: DEFAULT_TIMEOUT,
      priority: 2,
    });
  }

  if (task.match(/test|verify|check/i)) {
    subtasks.push({
      id: 'tester',
      role: 'tester',
      description: `Test and verify: ${task}`,
      agentType: 'tester',
      timeout: 60000,
      priority: 3,
    });
  }

  if (task.match(/review|analyze|assess/i)) {
    subtasks.push({
      id: 'reviewer',
      role: 'reviewer',
      description: `Review and analyze: ${task}`,
      agentType: 'oh-my-claudecode:code-reviewer',
      timeout: 60000,
      priority: 4,
    });
  }

  // Default: single general-purpose task
  if (subtasks.length === 0) {
    subtasks.push({
      id: 'general',
      role: 'general',
      description: task,
      agentType: 'general-purpose',
      timeout: DEFAULT_TIMEOUT,
      priority: 1,
    });
  }

  return {
    id: `pipeline-${Date.now()}`,
    task,
    subtasks,
    status: 'planned',
    created: new Date().toISOString(),
    parallel: subtasks.length > 1 && !subtasks.some(s => s.depends_on),
    max_parallel: MAX_PARALLEL,
  };
}

// ── Execute plan ─────────────────────────────────────────────────────────────
async function executeSubagent(task) {
  // In practice, this would spawn an agent via the Agent tool
  // For now, simulate with a placeholder
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        id: task.id,
        status: 'complete',
        output: `[SIMULATED] Would execute: ${task.description}`,
        agentType: task.agentType,
        duration_ms: 0,
      });
    }, 100);
  });
}

async function runPlan(plan) {
  const state = readState();
  const results = [];
  const startTime = Date.now();

  // Mark as active
  plan.status = 'running';
  plan.started = new Date().toISOString();
  savePlan(plan);

  // Sequential for now (parallel execution needs actual agent spawning)
  for (const task of plan.subtasks) {
    try {
      console.log(`  Running: ${task.id} (${task.role})`);
      const result = await executeSubagent(task);
      result.started = new Date().toISOString();
      result.completed = new Date().toISOString();
      saveResult(plan.id, task.id, result);
      results.push(result);
    } catch (e) {
      console.error(`  Failed: ${task.id} — ${e.message}`);
      results.push({ id: task.id, status: 'failed', error: e.message });
    }
  }

  plan.status = 'complete';
  plan.completed = new Date().toISOString();
  plan.duration_ms = Date.now() - startTime;
  plan.results = results;
  savePlan(plan);

  return plan;
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.plan) {
    // Plan a task
    const plan = planTask(args.plan);
    const { id, path } = savePlan(plan);

    console.log(`\n📋 OMC Subagent Pipeline Plan`);
    console.log(`  Plan ID: ${id}`);
    console.log(`  Task: ${plan.task}`);
    console.log(`  Subtasks: ${plan.subtasks.length}`);
    console.log(`  Parallel: ${plan.parallel ? 'yes' : 'no'}`);
    for (const t of plan.subtasks) {
      console.log(`    [${t.id}] ${t.role} — ${t.description.slice(0, 60)}... (timeout: ${t.timeout}ms)`);
    }
    console.log(`\n  Run with: node subagent-pipeline.mjs --run ${id}`);
    console.log(`  Or: node subagent-pipeline.mjs --run "${path}"\n`);

    const state = readState();
    state.plans.push({ id, task: plan.task, created: plan.created });
    writeState(state);
    return;
  }

  if (args.run) {
    const plan = loadPlan(args.run);
    if (!plan) {
      console.error(`Plan not found: ${args.run}`);
      return;
    }

    console.log(`\n▶️  Running pipeline: ${plan.id}`);
    console.log(`  Task: ${plan.task}`);
    console.log(`  Subtasks: ${plan.subtasks.length}\n`);

    const result = await runPlan(plan);

    console.log(`\n  ✅ Pipeline complete (${result.duration_ms}ms)`);
    for (const r of result.results) {
      console.log(`    [${r.status}] ${r.id}: ${r.output?.slice(0, 60) || r.error || ''}...`);
    }
    console.log();
    return;
  }

  if (args.status) {
    const state = readState();
    const plans = existsSync(PLANS_DIR)
      ? readdirSync(PLANS_DIR).filter(f => f.endsWith('.json'))
      : [];

    console.log(`\n📊 OMC Subagent Pipeline Status`);
    console.log(`  Plans: ${plans.length}`);
    console.log(`  Active: ${state.active || 'none'}`);
    if (plans.length > 0) {
      console.log(`\n  Recent plans:`);
      for (const p of plans.slice(-5)) {
        const data = JSON.parse(readFileSync(resolve(PLANS_DIR, p), 'utf-8'));
        console.log(`    • ${data.id} [${data.status}] — ${data.task?.slice(0, 50)}...`);
      }
    }
    console.log();
    return;
  }

  // Default: help
  console.log(`OMC Subagent Pipeline`);
  console.log(`Usage:`);
  console.log(`  --plan "task"   Plan task breakdown`);
  console.log(`  --run plan-id   Execute a plan`);
  console.log(`  --status        Show pipeline status`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
