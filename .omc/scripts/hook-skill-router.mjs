#!/usr/bin/env node
/**
 * OMC Skill Router — Dynamic trigger evaluation
 * Reads hook-skill-manifest.json → evaluates conditions → fires appropriate skills
 *
 * Replaces static hook triggers with dynamic condition evaluation.
 * Each skill has: trigger event, conditions, priority, blocking rules.
 */
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const MANIFEST = resolve(__dirname, 'hook-skill-manifest.json');
const STATE_DIR = resolve(__dirname, '../state');
const COUNTER_FILE = resolve(STATE_DIR, 'auto-seed-counter.json');
const ERROR_FREQ_FILE = resolve(STATE_DIR, 'error-frequency.json');
const RECURRENCE_FLAG = resolve(STATE_DIR, 'insight-recurrence-flag.md');
const EFF_FILE = resolve(STATE_DIR, 'insight-effectiveness.json');

function log(...a) { console.log('[skill-router]', ...a); }

// ── Condition evaluators ─────────────────────────────────────────────────────
function evalCondition(cond, ctx) {
  if (!cond || Object.keys(cond).length === 0) return true;

  for (const [key, val] of Object.entries(cond)) {
    switch (key) {
      case 'minToolCount':
        if ((ctx.toolCount || 0) < val) return false;
        break;
      case 'minBashRatio':
        if ((ctx.bashRatio || 0) < val) return false;
        break;
      case 'minToolVelocity':
        if ((ctx.velocity || 0) < val) return false;
        break;
      case 'minErrorFreq':
        if ((ctx.errorFreq || 0) < val) return false;
        break;
      case 'minRecurrence':
        if ((ctx.recurrence || 0) < val) return false;
        break;
      case 'noveltyRequired':
        if (val === true && !ctx.hasNovelty) return false;
        break;
      case 'excludePatterns': {
        const cmd = ctx.command || '';
        if (val.some(p => cmd.includes(p))) return false;
        break;
      }
      case 'dangerousRulesOnly':
        // Check if there are dangerous rules to apply
        if (val === true && !ctx.hasDangerousRules) return false;
        break;
    }
  }
  return true;
}

// ── Load context for condition evaluation ──────────────────────────────────────
function loadContext(event) {
  const ctx = {
    toolCount: 0,
    bashRatio: 0,
    velocity: 0,
    errorFreq: 0,
    recurrence: 0,
    hasNovelty: false,
    hasDangerousRules: false,
    command: '',
  };

  // Tool count from counter
  if (existsSync(COUNTER_FILE)) {
    try {
      const counter = JSON.parse(readFileSync(COUNTER_FILE, 'utf-8'));
      ctx.toolCount = counter.count || 0;
    } catch {}
  }

  // Error frequency
  if (existsSync(ERROR_FREQ_FILE)) {
    try {
      const freq = JSON.parse(readFileSync(ERROR_FREQ_FILE, 'utf-8'));
      // Sum total across all classes
      ctx.errorFreq = Object.values(freq.classes || {}).reduce((s, c) => s + (c.totalCount || 0), 0);
    } catch {}
  }

  // Recurrence for most frequent error class
  if (existsSync(ERROR_FREQ_FILE)) {
    try {
      const freq = JSON.parse(readFileSync(ERROR_FREQ_FILE, 'utf-8'));
      let maxCount = 0;
      for (const [cls, data] of Object.entries(freq.classes || {})) {
        if ((data.totalCount || 0) > maxCount) {
          maxCount = data.totalCount;
          ctx.recurrence = maxCount;
        }
      }
    } catch {}
  }

  // Bash ratio from event
  if (event?.tool_name === 'Bash' || event?.tool?.name === 'Bash') {
    ctx.bashRatio = 0.5; // Will be updated by caller
  }

  // Novelty from active-learn trigger
  const ACTIVE_LEARN = resolve(STATE_DIR, 'active-learn-trigger.json');
  if (existsSync(ACTIVE_LEARN)) {
    ctx.hasNovelty = true;
  }

  // Dangerous rules from self-improve state
  const SI_STATE = resolve(STATE_DIR, 'hook-self-improve-state.json');
  if (existsSync(SI_STATE)) {
    try {
      const si = JSON.parse(readFileSync(SI_STATE, 'utf-8'));
      ctx.hasDangerousRules = (si.dangerousCount || 0) > 0;
    } catch {}
  }

  // Command from Bash events
  if (event?.tool_input?.command) {
    ctx.command = event.tool_input.command;
  } else if (event?.tool?.input?.command) {
    ctx.command = event.tool.input.command;
  }

  return ctx;
}

// ── Main router logic ────────────────────────────────────────────────────────
async function route(event, trigger) {
  if (!existsSync(MANIFEST)) {
    log('no manifest found');
    return [];
  }

  let manifest;
  try {
    manifest = JSON.parse(readFileSync(MANIFEST, 'utf-8'));
  } catch {
    log('invalid manifest JSON');
    return [];
  }

  const skills = manifest.skills || {};
  const triggered = [];

  // Filter skills by trigger event
  const matchingSkills = Object.values(skills).filter(s => s.trigger === trigger);

  // Load evaluation context
  const ctx = loadContext(event);

  for (const skill of matchingSkills) {
    if (!evalCondition(skill.conditions || {}, ctx)) continue;

    // Check blocking — don't fire if higher-priority skill already triggered
    const blocked = triggered.some(fired => {
      const blocker = skills[fired];
      return blocker && blocker.blocks && blocker.blocks.includes(skill.name);
    });
    if (blocked) continue;

    triggered.push(skill.name);
  }

  return triggered;
}

// ── Fire skills ───────────────────────────────────────────────────────────────
function fireSkills(skillNames, event) {
  const SCRIPTS_DIR = __dirname;
  const scriptMap = {
    'auto-seed': { script: 'hook-auto-seed.mjs', args: ['--check'] },
    'active-learn': { script: 'hook-active-learn.mjs', args: [] },
    'self-improve': { script: 'hook-self-improve.mjs', args: ['--auto-apply'] },
    'meta-audit': { script: 'hook-session-end-drain.mjs', args: ['--step9-only'] },
  };

  const { spawn } = require('child_process');

  for (const name of skillNames) {
    const cfg = scriptMap[name];
    if (!cfg) { log(`no script for skill: ${name}`); continue; }

    const scriptPath = resolve(SCRIPTS_DIR, cfg.script);
    if (!existsSync(scriptPath)) { log(`script not found: ${scriptPath}`); continue; }

    log(`firing: ${name}`);
    const proc = spawn(process.execPath, [scriptPath, ...cfg.args], {
      stdio: 'ignore',
      detached: true,
      windowsHide: true,
    });
    proc.unref();
  }
}

// ── CLI / hook entry point ────────────────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);

  // Called from hook with event JSON on stdin
  if (args.includes('--stdin')) {
    let eventData = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', c => { eventData += c; });
    process.stdin.on('end', async () => {
      let event = {};
      try { event = JSON.parse(eventData); } catch {}
      const trigger = event.hook_event_name || 'PostToolUse';
      const skills = await route(event, trigger);
      if (skills.length > 0) {
        fireSkills(skills, event);
        console.log(`[skill-router] triggered: ${skills.join(', ')}`);
      }
    });
    return;
  }

  // Standalone: --evaluate <trigger>
  if (args.includes('--evaluate')) {
    const trigger = args[args.indexOf('--evaluate') + 1] || 'PostToolUse';
    const skills = await route({}, trigger);
    console.log(skills.join('\n'));
    return;
  }

  // List manifest skills
  if (args.includes('--list')) {
    if (!existsSync(MANIFEST)) { console.log('no manifest'); return; }
    const manifest = JSON.parse(readFileSync(MANIFEST, 'utf-8'));
    for (const [name, skill] of Object.entries(manifest.skills || {})) {
      console.log(`## ${name}`);
      console.log(`  trigger: ${skill.trigger}`);
      console.log(`  priority: ${skill.priority}`);
      console.log(`  blocks: ${(skill.blocks || []).join(', ') || '(none)'}`);
      console.log(`  after: ${(skill.after || []).join(', ') || '(none)'}`);
      console.log(`  conditions: ${JSON.stringify(skill.conditions)}`);
      console.log('');
    }
  }
}

main().catch(() => {});
