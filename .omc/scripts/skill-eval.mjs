#!/usr/bin/env node
/**
 * OMC Skill Condition Evaluator
 * Called by existing hooks → checks conditions → decides whether to proceed
 * Returns exit code 0 = fire, 1 = skip
 */
import { existsSync, readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const MANIFEST = resolve(__dirname, 'hook-skill-manifest.json');
const COUNTER_FILE = resolve(STATE_DIR, 'auto-seed-counter.json');
const ERROR_FREQ_FILE = resolve(__dirname, '../state/error-frequency.json');
const ACTIVE_LEARN_FILE = resolve(STATE_DIR, 'active-learn-trigger.json');

const SELF_SCRIPTS = ['hook-stats.mjs', 'hook-auto-seed.mjs', 'hook-session-start-inject.mjs'];

function log(...a) { console.error('[skill-eval]', ...a); }

// ── Load context ─────────────────────────────────────────────────────────────
function loadContext(event) {
  const ctx = { toolCount: 0, errorFreq: 0, recurrence: 0, hasNovelty: false };

  if (existsSync(COUNTER_FILE)) {
    try { ctx.toolCount = JSON.parse(readFileSync(COUNTER_FILE, 'utf-8')).count || 0; } catch {}
  }
  if (existsSync(ERROR_FREQ_FILE)) {
    try {
      const freq = JSON.parse(readFileSync(ERROR_FREQ_FILE, 'utf-8'));
      ctx.errorFreq = Object.values(freq.classes || {}).reduce((s, c) => s + (c.totalCount || 0), 0);
      let max = 0;
      for (const d of Object.values(freq.classes || {})) {
        if ((d.totalCount || 0) > max) max = d.totalCount;
      }
      ctx.recurrence = max;
    } catch {}
  }
  if (existsSync(ACTIVE_LEARN_FILE)) ctx.hasNovelty = true;

  if (event?.tool_name === 'Bash' || event?.tool?.name === 'Bash') {
    const cmd = event.tool_input?.command || event.tool?.input?.command || '';
    ctx.command = cmd;
    if (SELF_SCRIPTS.some(s => cmd.includes(s))) ctx.isSelfScript = true;
    if (cmd.match(/^(ls|cat|echo|cd|pwd|rm |mkdir )\s/)) ctx.isReadOnly = true;
  }

  return ctx;
}

// ── Condition check ─────────────────────────────────────────────────────────
function shouldFire(skill, ctx) {
  const cond = skill.conditions || {};
  if (!cond || Object.keys(cond).length === 0) return true;

  if (cond.minToolCount && ctx.toolCount < cond.minToolCount) return false;
  if (cond.minErrorFreq && ctx.errorFreq < cond.minErrorFreq) return false;
  if (cond.minRecurrence && ctx.recurrence < cond.minRecurrence) return false;
  if (cond.noveltyRequired && !ctx.hasNovelty) return false;
  if (cond.excludePatterns) {
    const cmd = ctx.command || '';
    if (cond.excludePatterns.some(p => cmd.includes(p))) return false;
  }
  return true;
}

// ── Main ───────────────────────────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) { log('usage: skill-eval <skill-name>'); process.exit(1); }

  const skillName = args[0];
  if (!existsSync(MANIFEST)) { log('no manifest'); process.exit(1); }

  let manifest;
  try { manifest = JSON.parse(readFileSync(MANIFEST, 'utf-8')); }
  catch { log('invalid manifest'); process.exit(1); }

  const skill = manifest.skills?.[skillName];
  if (!skill) { log(`skill not found: ${skillName}`); process.exit(1); }

  // Read event from stdin
  let eventData = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', c => { eventData += c; });
  process.stdin.on('end', () => {
    let event = {};
    try { event = JSON.parse(eventData); } catch {}
    const ctx = loadContext(event);
    const fire = shouldFire(skill, ctx);
    log(`${skillName}: toolCount=${ctx.toolCount} errorFreq=${ctx.errorFreq} recurrence=${ctx.recurrence} novelty=${ctx.hasNovelty} → ${fire ? 'FIRE' : 'SKIP'}`);
    process.exit(fire ? 0 : 1);
  });
}

main();
