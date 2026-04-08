#!/usr/bin/env node
/**
 * OMC Introspection System
 * Observability into OMC hooks, scripts, memory, and agent activity.
 *
 * Inspired by Hermes Agent's observability:
 *   - Real-time hook execution monitoring
 *   - Script performance tracking
 *   - Memory usage and patterns
 *   - Agent activity dashboards
 *
 * Usage:
 *   node omc-introspect.mjs --hooks          Hook system status
 *   node omc-introspect.mjs --scripts        Script registry + stats
 *   node omc-introspect.mjs --memory         Memory system overview
 *   node omc-introspect.mjs --agents         Active agent status
 *   node omc-introspect.mjs --audit          Hook audit trail
 *   node omc-introspect.mjs --all            Full system overview
 *   node omc-introspect.mjs --heatmap        Activity heatmap
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync, statSync } from 'fs';
import { resolve, dirname } from 'path';

// Use hardcoded workspace root for Windows compatibility
const WORKSPACE = 'D:\\OpenClaw\\workspace';
const OMC_DIR = resolve(WORKSPACE, '.omc');
const SCRIPT_DIR = resolve(OMC_DIR, 'scripts');
const STATE_DIR = resolve(OMC_DIR, 'state');
const MEMORY_DIR = resolve(OMC_DIR, 'memory');
const HOOKS_DIR = resolve(WORKSPACE, '.claude');

// Minimal glob for ESM compatibility (no regex, simple string matching)
function globSync(pattern) {
  // Normalize pattern: extract dir and file filter
  const parts = pattern.replace(/\\/g, '/').split('/');
  const base = parts.slice(0, -1).join('/');
  const filter = parts[parts.length - 1].replace(/\*/g, 'SPLAT').replace(/\?/g, 'QMARK');
  const results = [];
  try {
    const files = readdirSync(base.replace(/\/$/, ''));
    for (const f of files) {
      const test = filter.replace(/SPLAT/g, '([^/]*)').replace(/QMARK/g, '[^/]');
      const re = new RegExp('^' + test + '$');
      if (re.test(f)) {
        results.push(resolve(base, f));
      }
    }
  } catch { /* ignore */ }
  return results;
}

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

function readJSON(path) {
  if (!existsSync(path)) return null;
  try { return JSON.parse(readFileSync(path, 'utf-8')); }
  catch { return null; }
}

function getFileAge(path) {
  try {
    const stat = statSync(path);
    const age = Date.now() - stat.mtime.getTime();
    const days = Math.floor(age / (24 * 60 * 60 * 1000));
    return days;
  } catch { return null; }
}

// ── Hook system ──────────────────────────────────────────────────────────────
function inspectHooks() {
  const hooks = [];
  const hookFiles = globSync(`${HOOKS_DIR}/hookify.*.local.md`);

  for (const file of hookFiles) {
    const content = readFileSync(file, 'utf-8');
    const metaMatch = content.match(/^---\n([\s\S]*?)\n---\n/);
    if (!metaMatch) continue;

    const meta = {};
    for (const line of metaMatch[1].split('\n')) {
      const idx = line.indexOf(':');
      if (idx < 0) continue;
      const key = line.slice(0, idx).trim();
      let val = line.slice(idx + 1).trim();
      if (val === 'true') val = true;
      if (val === 'false') val = false;
      meta[key] = val;
    }

    hooks.push({
      name: meta.name || file,
      enabled: meta.enabled !== false,
      event: meta.event || 'unknown',
      file,
    });
  }

  return hooks;
}

// ── Script registry ─────────────────────────────────────────────────────────
function inspectScripts() {
  const scripts = [];
  if (!existsSync(SCRIPT_DIR)) return scripts;

  const files = readdirSync(SCRIPT_DIR).filter(f => f.endsWith('.mjs'));
  for (const file of files) {
    const path = resolve(SCRIPT_DIR, file);
    const stat = statSync(path);
    const content = readFileSync(path, 'utf-8');

    // Extract docstring
    const docMatch = content.match(/\/\*\*([\s\S]*?)\*\//);
    const description = docMatch
      ? docMatch[1].split('\n').find(l => l.includes('—'))?.replace(/[*\s]/g, '').trim() || 'OMC script'
      : 'OMC script';

    // Check for state file
    const stateFile = file.replace('.mjs', '-state.json');
    const hasState = existsSync(resolve(STATE_DIR, stateFile));

    scripts.push({
      name: file,
      path,
      size: stat.size,
      description: description.replace(/—/, '').trim(),
      hasState,
      lastModified: stat.mtime.toISOString(),
    });
  }

  // Sort by size
  scripts.sort((a, b) => b.size - a.size);
  return scripts;
}

// ── Memory system ─────────────────────────────────────────────────────────────
function inspectMemory() {
  const memory = [];

  if (existsSync(MEMORY_DIR)) {
    const files = readdirSync(MEMORY_DIR).filter(f => f.endsWith('.md'));
    for (const file of files) {
      const path = resolve(MEMORY_DIR, file);
      const stat = statSync(path);
      const content = readFileSync(path, 'utf-8');
      memory.push({
        name: file,
        path,
        size: stat.size,
        lines: content.split('\n').length,
        lastModified: stat.mtime.toISOString(),
      });
    }
  }

  return memory;
}

// ── State files overview ───────────────────────────────────────────────────────
function inspectState() {
  const stateFiles = [];

  if (existsSync(STATE_DIR)) {
    const files = readdirSync(STATE_DIR).filter(f => f.endsWith('.json') || f.endsWith('.jsonl'));
    for (const file of files) {
      const path = resolve(STATE_DIR, file);
      const stat = statSync(path);
      stateFiles.push({
        name: file,
        path,
        size: stat.size,
        age: getFileAge(path),
        lastModified: stat.mtime.toISOString(),
      });
    }
  }

  stateFiles.sort((a, b) => b.size - a.size);
  return stateFiles;
}

// ── Hook audit analysis ─────────────────────────────────────────────────────
function analyzeHookAudit() {
  const auditPath = resolve(STATE_DIR, 'hook-audit.jsonl');
  if (!existsSync(auditPath)) return { total: 0, byTool: {}, byHour: {} };

  try {
    const content = readFileSync(auditPath, 'utf-8');
    const lines = content.split('\n').filter(Boolean).slice(-1000); // last 1000

    const entries = lines.map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);

    const byTool = {};
    const byHour = {};

    for (const e of entries) {
      const tool = e.tool || 'unknown';
      byTool[tool] = (byTool[tool] || 0) + 1;

      if (e.timestamp) {
        const hour = new Date(e.timestamp).getHours();
        byHour[hour] = (byHour[hour] || 0) + 1;
      }
    }

    // Top tools
    const topTools = Object.entries(byTool)
      .sort((a, b) => b[1] - a[1]).slice(0, 10);

    return { total: entries.length, byTool: topTools, byHour, hoursTotal: Object.keys(byHour).length };
  } catch {
    return { total: 0, byTool: {}, byHour: {} };
  }
}

// ── Heatmap ──────────────────────────────────────────────────────────────────
function generateHeatmap() {
  const data = analyzeHookAudit();
  if (data.total === 0) return 'No hook data';

  const hours = Array.from({ length: 24 }, (_, i) => {
    const count = data.byHour[i] || 0;
    const max = Math.max(...Object.values(data.byHour));
    const density = max > 0 ? count / max : 0;
    const bar = '█'.repeat(Math.round(density * 10));
    return `${String(i).padStart(2, '0')}h ${bar || '·'} ${count}`;
  });

  return hours.join('\n');
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (!args.hooks && !args.scripts && !args.memory && !args.agents && !args.audit && !args.all && !args.heatmap) {
    args.all = true;
  }

  if (args.all || args.hooks) {
    const hooks = inspectHooks();
    console.log(`\n🪝 OMC Hooks (${hooks.length} rules)`);
    console.log(`  Enabled: ${hooks.filter(h => h.enabled).length}`);
    console.log(`  Disabled: ${hooks.filter(h => !h.enabled).length}\n`);
    for (const h of hooks) {
      const status = h.enabled ? '🟢' : '⚪️';
      console.log(`  ${status} ${h.name} [${h.event}]`);
    }
    console.log();
  }

  if (args.all || args.scripts) {
    const scripts = inspectScripts();
    const totalSize = scripts.reduce((s, c) => s + c.size, 0);
    console.log(`\n📜 OMC Scripts (${scripts.length} scripts, ${Math.round(totalSize / 1024)}KB total)`);
    for (const s of scripts.slice(0, 15)) {
      const state = s.hasState ? '📊' : '  ';
      console.log(`  ${state} ${s.name} (${Math.round(s.size / 1024)}KB) — ${s.description}`);
    }
    console.log();
  }

  if (args.all || args.memory) {
    const memory = inspectMemory();
    const totalSize = memory.reduce((s, m) => s + m.size, 0);
    console.log(`\n🧠 OMC Memory (${memory.length} files, ${Math.round(totalSize / 1024)}KB)`);
    for (const m of memory.slice(0, 10)) {
      console.log(`  ${m.name} (${Math.round(m.size / 1024)}KB, ${m.lines}L)`);
    }
    console.log();
  }

  if (args.all || args.state) {
    const stateFiles = inspectState();
    console.log(`\n💾 OMC State (${stateFiles.length} files)`);
    for (const s of stateFiles.slice(0, 15)) {
      console.log(`  ${s.name} (${Math.round(s.size / 1024)}KB, ${s.age ?? '?'}d old)`);
    }
    console.log();
  }

  if (args.all || args.agents) {
    const lifecyclePath = resolve(STATE_DIR, 'agent-lifecycle.json');
    const lifecycle = readJSON(lifecyclePath);
    if (lifecycle) {
      const running = Object.values(lifecycle.agents || {}).filter(a => a.status === 'running');
      console.log(`\n🤖 OMC Agents`);
      console.log(`  Total spawned: ${lifecycle.spawned}`);
      console.log(`  Running: ${running.length}`);
      for (const a of running) {
        console.log(`  🟢 ${a.id} (${a.type}) — expires ${a.expires}`);
      }
    } else {
      console.log(`\n🤖 OMC Agents: no lifecycle data\n`);
    }
  }

  if (args.all || args.audit) {
    const audit = analyzeHookAudit();
    console.log(`\n📊 Hook Activity (last 1000 entries)`);
    console.log(`  Total events: ${audit.total}`);
    if (audit.byTool.length > 0) {
      console.log(`  Top tools:`);
      for (const [tool, count] of audit.byTool.slice(0, 5)) {
        console.log(`    ${tool}: ${count}`);
      }
    }
    console.log();
  }

  if (args.heatmap) {
    console.log(`\n🗓️ Activity Heatmap (hourly)\n`);
    console.log(generateHeatmap());
    console.log();
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
