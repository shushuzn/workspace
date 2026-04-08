#!/usr/bin/env node
/**
 * OMC Agent Lifecycle Manager
 * Manages subagent spawning, lifecycle, cleanup, and resource tracking.
 *
 * Inspired by Hermes Agent's execution environments:
 *   - Spawn, monitor, and terminate subagents
 *   - Resource limits and timeout enforcement
 *   - Graceful shutdown and cleanup
 *   - Audit trail of all agent lifecycles
 *
 * Usage:
 *   node agent-lifecycle.mjs --spawn type [--name id] [--timeout N]    Spawn agent
 *   node agent-lifecycle.mjs --list                                      List agents
 *   node agent-lifecycle.mjs --status agent-id                            Agent status
 *   node agent-lifecycle.mjs --kill agent-id                              Kill agent
 *   node agent-lifecycle.mjs --cleanup                                   Cleanup dead
 *   node agent-lifecycle.mjs --audit                                     Audit trail
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, appendFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const STATE_FILE = resolve(STATE_DIR, 'agent-lifecycle.json');
const AUDIT_FILE = resolve(STATE_DIR, 'agent-lifecycle-audit.jsonl');
const MAX_AGENTS = 10;
const DEFAULT_TIMEOUT = 300000; // 5 min

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      if (key === 'name') { args.name = argv[++i]; continue; }
      if (key === 'timeout') { args.timeout = parseInt(argv[++i]) || DEFAULT_TIMEOUT; continue; }
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

function readState() {
  if (!existsSync(STATE_FILE)) return { agents: {}, spawned: 0 };
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return { agents: {}, spawned: 0 }; }
}

function writeState(state) {
  mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

function audit(event) {
  const entry = { ...event, ts: new Date().toISOString() };
  mkdirSync(STATE_DIR, { recursive: true });
  appendFileSync(AUDIT_FILE, JSON.stringify(entry) + '\n', 'utf-8');
}

// ── Agent types ─────────────────────────────────────────────────────────────
const AGENT_TYPES = {
  Explore: { description: 'Codebase search and exploration', defaultTimeout: 60000 },
  Architect: { description: 'Architecture design and planning', defaultTimeout: 180000 },
  Executor: { description: 'Code implementation', defaultTimeout: 300000 },
  Reviewer: { description: 'Code review and analysis', defaultTimeout: 120000 },
  Researcher: { description: 'Research and information gathering', defaultTimeout: 90000 },
  Writer: { description: 'Documentation writing', defaultTimeout: 120000 },
  QA: { description: 'Testing and quality assurance', defaultTimeout: 180000 },
  'general-purpose': { description: 'General purpose agent', defaultTimeout: 300000 },
};

function getAgentType(type) {
  return AGENT_TYPES[type] || AGENT_TYPES['general-purpose'];
}

// ── Spawn agent ─────────────────────────────────────────────────────────────
function spawnAgent(type, name, timeout) {
  const state = readState();
  const activeCount = Object.values(state.agents).filter(a => a.status === 'running').length;

  if (activeCount >= MAX_AGENTS) {
    return { error: `Max agents reached (${MAX_AGENTS})` };
  }

  const id = name || `${type}-${Date.now()}`;
  const config = getAgentType(type);
  const effectiveTimeout = timeout || config.defaultTimeout;

  if (state.agents[id]) {
    return { error: `Agent already exists: ${id}` };
  }

  state.agents[id] = {
    id,
    type,
    name,
    status: 'running',
    spawned: new Date().toISOString(),
    timeout: effectiveTimeout,
    expires: new Date(Date.now() + effectiveTimeout).toISOString(),
    result: null,
    error: null,
  };
  state.spawned++;
  writeState(state);

  audit({ event: 'spawn', agentId: id, type, timeout: effectiveTimeout });

  console.log(`\n✅ Spawned: ${id} (${type})`);
  console.log(`   Timeout: ${effectiveTimeout / 1000}s`);
  console.log(`   Expires: ${state.agents[id].expires}\n`);

  return state.agents[id];
}

// ── Update agent status ───────────────────────────────────────────────────
function updateAgent(id, updates) {
  const state = readState();
  if (!state.agents[id]) return { error: 'Agent not found' };

  state.agents[id] = { ...state.agents[id], ...updates };
  writeState(state);
  audit({ event: 'update', agentId: id, updates });

  return state.agents[id];
}

// ── Kill agent ─────────────────────────────────────────────────────────────
function killAgent(id, reason = 'manual') {
  const state = readState();
  if (!state.agents[id]) return { error: 'Agent not found' };

  const agent = state.agents[id];
  agent.status = 'killed';
  agent.ended = new Date().toISOString();
  agent.endReason = reason;

  if (reason === 'timeout') {
    agent.error = 'Killed due to timeout';
  }

  writeState(state);
  audit({ event: 'kill', agentId: id, reason });

  return { killed: id, reason };
}

// ── Check timeouts ────────────────────────────────────────────────────────
function checkTimeouts() {
  const state = readState();
  const now = Date.now();
  const killed = [];

  for (const [id, agent] of Object.entries(state.agents)) {
    if (agent.status === 'running') {
      const expires = new Date(agent.expires).getTime();
      if (now > expires) {
        killAgent(id, 'timeout');
        killed.push(id);
      }
    }
  }

  if (killed.length > 0) {
    console.log(`Killed ${killed.length} timed-out agents: ${killed.join(', ')}`);
  }

  return killed;
}

// ── Cleanup dead agents ───────────────────────────────────────────────────
function cleanup() {
  const state = readState();
  const before = Object.keys(state.agents).length;
  const dead = ['killed', 'completed', 'failed'];

  for (const [id, agent] of Object.entries(state.agents)) {
    if (dead.includes(agent.status)) {
      const age = Date.now() - new Date(agent.ended || agent.expires).getTime();
      if (age > 24 * 60 * 60 * 1000) { // > 24h old
        delete state.agents[id];
      }
    }
  }

  const after = Object.keys(state.agents).length;
  const cleaned = before - after;
  writeState(state);

  audit({ event: 'cleanup', before, after, cleaned });
  console.log(`Cleaned up ${cleaned} dead agents (${after} remaining)\n`);
}

// ── Audit trail ───────────────────────────────────────────────────────────
function showAudit(lines = 20) {
  if (!existsSync(AUDIT_FILE)) {
    console.log('No audit entries\n');
    return;
  }

  const content = readFileSync(AUDIT_FILE, 'utf-8');
  const entries = content.split('\n').filter(Boolean).slice(-lines);

  console.log(`\n📋 Agent Lifecycle Audit (last ${entries.length} entries)\n`);
  for (const entry of entries) {
    try {
      const e = JSON.parse(entry);
      const time = new Date(e.ts).toLocaleTimeString('zh-CN');
      if (e.event === 'spawn') {
        console.log(`  ${time} 🟢 SPAWN ${e.agentId} (${e.type})`);
      } else if (e.event === 'kill') {
        console.log(`  ${time} 🔴 KILL ${e.agentId} — ${e.reason}`);
      } else if (e.event === 'update') {
        console.log(`  ${time} 🔵 UPDATE ${e.agentId}: ${JSON.stringify(e.updates)}`);
      } else if (e.event === 'cleanup') {
        console.log(`  ${time} 🟡 CLEANUP: removed ${e.cleaned} agents`);
      } else {
        console.log(`  ${time} ${e.event} ${e.agentId || ''}`);
      }
    } catch { /* skip */ }
  }
  console.log();
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  // Check timeouts on every run
  checkTimeouts();

  if (args.spawn) {
    const result = spawnAgent(args.spawn, args.name, args.timeout);
    if (result.error) console.error(`Error: ${result.error}`);
    return;
  }

  if (args.list) {
    const state = readState();
    const agents = Object.values(state.agents);
    const running = agents.filter(a => a.status === 'running');
    const dead = agents.filter(a => ['killed', 'completed', 'failed'].includes(a.status));

    console.log(`\n🤖 OMC Agent Lifecycle`);
    console.log(`  Running: ${running.length}/${MAX_AGENTS}`);
    console.log(`  Total spawned: ${state.spawned}`);
    console.log(`  Dead (retained): ${dead.length}\n`);

    if (running.length > 0) {
      console.log(`  Running agents:`);
      for (const a of running) {
        const expires = new Date(a.expires).toLocaleTimeString('zh-CN');
        console.log(`    [${a.id}] ${a.type} — expires ${expires}`);
      }
    }
    if (dead.length > 0) {
      console.log(`\n  Dead agents:`);
      for (const a of dead) {
        console.log(`    [${a.id}] ${a.type} (${a.status}) — ${a.endReason || 'unknown'}`);
      }
    }
    console.log();
    return;
  }

  if (args.status) {
    const state = readState();
    const agent = state.agents[args.status];
    if (!agent) {
      console.error(`Agent not found: ${args.status}`);
      return;
    }
    console.log(`\nAgent: ${agent.id}`);
    console.log(`  Type: ${agent.type}`);
    console.log(`  Status: ${agent.status}`);
    console.log(`  Spawned: ${agent.spawned}`);
    if (agent.expires) console.log(`  Expires: ${agent.expires}`);
    if (agent.ended) console.log(`  Ended: ${agent.ended}`);
    if (agent.endReason) console.log(`  End reason: ${agent.endReason}`);
    if (agent.result) console.log(`  Result: ${JSON.stringify(agent.result)}`);
    if (agent.error) console.log(`  Error: ${agent.error}`);
    console.log();
    return;
  }

  if (args.kill) {
    const result = killAgent(args.kill, 'manual');
    if (result.error) console.error(`Error: ${result.error}`);
    else console.log(`Killed: ${result.killed} (${result.reason})\n`);
    return;
  }

  if (args.cleanup) {
    cleanup();
    return;
  }

  if (args.audit) {
    showAudit(parseInt(args.audit) || 20);
    return;
  }

  // Default: help + summary
  const state = readState();
  console.log(`\n🤖 OMC Agent Lifecycle Manager`);
  console.log(`  Agents: ${Object.keys(state.agents).length} total, ${state.spawned} spawned`);
  console.log(`  Running: ${Object.values(state.agents).filter(a => a.status === 'running').length}/${MAX_AGENTS}`);
  console.log(`\nUsage:`);
  console.log(`  --spawn type [--name id] [--timeout N]  Spawn an agent`);
  console.log(`  --list                                  List agents`);
  console.log(`  --status agent-id                       Agent details`);
  console.log(`  --kill agent-id                         Kill agent`);
  console.log(`  --cleanup                               Remove dead agents`);
  console.log(`  --audit [N]                             Show audit trail`);
  console.log(`\nAgent types: ${Object.keys(AGENT_TYPES).join(', ')}`);
  console.log();
}

main().catch(e => { console.error(e.message); process.exit(1); });
