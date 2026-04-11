#!/usr/bin/env node
/**
 * scripts/ci-pattern-health-decay.mjs
 * Applies time-based confidence decay for patterns not seen in 30+ days.
 * Decay formula: effective_conf = raw_conf * decay_factor
 *   days < 30  → decay_factor = 1.0 (no decay)
 *   days 30-120 → decay_factor linearly from 1.0 → 0.5
 *   days > 120 → decay_factor = 0.5 (floor)
 *
 * Usage:
 *   node scripts/ci-pattern-health-decay.mjs              # show decay report
 *   node scripts/ci-pattern-health-decay.mjs --apply      # apply decay to patterns
 *   node scripts/ci-pattern-health-decay.mjs --stale       # list only stale patterns
 */
import { existsSync, readFileSync, writeFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_FILE = join(__dirname, '..', 'ci-state.json');
const PATTERNS_FILE = join(__dirname, 'ci-failure-patterns.jsonl');
const APPLY = process.argv.includes('--apply');
const STALE_ONLY = process.argv.includes('--stale');

const DECAY_START_DAYS = 30;
const DECAY_END_DAYS = 120;
const DECAY_FLOOR = 0.5;

function loadState() {
  if (!existsSync(STATE_FILE)) return {};
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf8')); } catch { return {}; }
}

function loadPatterns() {
  if (!existsSync(PATTERNS_FILE)) return [];
  try {
    const content = readFileSync(PATTERNS_FILE, 'utf8');
    return content.trim().split('\n').filter(Boolean).map(l => {
      try { return JSON.parse(l); } catch { return null; }
    }).filter(Boolean);
  } catch { return []; }
}

function calcDecayFactor(daysSince) {
  if (daysSince < DECAY_START_DAYS) return 1.0;
  if (daysSince > DECAY_END_DAYS) return DECAY_FLOOR;
  const t = (daysSince - DECAY_START_DAYS) / (DECAY_END_DAYS - DECAY_START_DAYS);
  return 1.0 - t * (1.0 - DECAY_FLOOR);
}

function daysSince(timestamp) {
  if (!timestamp) return Infinity;
  const then = new Date(timestamp);
  const now = new Date();
  return (now - then) / (1000 * 60 * 60 * 24);
}

function effectiveConfidence(pattern, lastEventTime) {
  if (pattern.confirmations == null || pattern.rejections == null) return null;
  const total = pattern.confirmations + pattern.rejections;
  if (total === 0) return null;
  const raw = pattern.confirmations / total;
  if (!lastEventTime) return raw;
  const decay = calcDecayFactor(Math.floor(daysSince(lastEventTime)));
  return raw * decay;
}

function run() {
  const state = loadState();
  const patterns = loadPatterns();
  const fixHistory = state?.patterns?.fixHistory || {};
  const lastFixAttempt = state?.patterns?.lastFixAttempt || {};

  const now = new Date();
  const rows = [];

  for (const p of patterns) {
    const events = fixHistory[p.name] || [];
    const lastFix = lastFixAttempt[p.name];
    const lastEventTime = lastFix?.timestamp || events[events.length - 1]?.timestamp || null;
    const rawConf = (p.confirmations != null && (p.confirmations + p.rejections) > 0)
      ? p.confirmations / (p.confirmations + p.rejections)
      : null;
    const effConf = effectiveConfidence(p, lastEventTime);
    const decay = lastEventTime ? calcDecayFactor(Math.floor(daysSince(lastEventTime))) : 1.0;
    const days = lastEventTime ? Math.floor(daysSince(lastEventTime)) : null;
    const isStale = days !== null && days >= DECAY_START_DAYS;

    if (STALE_ONLY && !isStale) continue;

    rows.push({
      name: p.name,
      severity: p.severity,
      rawConf,
      effConf,
      decay,
      days,
      lastEventTime,
      lastFix,
      isStale,
      confirms: p.confirmations || 0,
      rejects: p.rejections || 0,
      eventCount: events.length,
    });
  }

  if (STALE_ONLY) {
    // Just list stale patterns
    const stale = rows.filter(r => r.isStale);
    if (stale.length === 0) {
      console.log('No stale patterns (30+ days since last event).');
      return;
    }
    console.log(`\n=== Stale Patterns (${stale.length}) ===\n`);
    for (const r of stale.sort((a, b) => (a.days || 0) - (b.days || 0))) {
      const confStr = r.effConf !== null ? `${(r.effConf * 100).toFixed(0)}%` : 'N/A';
      const rawStr = r.rawConf !== null ? `${(r.rawConf * 100).toFixed(0)}%` : 'N/A';
      console.log(`  ${r.severity}  ${r.days}d  ${confStr} (was ${rawStr})  ${r.name}`);
    }
    console.log();
    return;
  }

  // Full report
  const staleCount = rows.filter(r => r.isStale).length;
  console.log(`\n=== Pattern Health Decay Report ===  (${now.toLocaleDateString()})\n`);
  console.log(`Decay: 0 days=no decay, ${DECAY_START_DAYS}+ days=linear decay to ${(DECAY_FLOOR * 100).toFixed(0)}%, ${DECAY_END_DAYS}+ days=floor\n`);
  console.log(
    `${'Pattern'.padEnd(42)} ${'Raw'.padEnd(7)} ${'Effective'.padEnd(9)} ${'Decay'.padEnd(6)} ${'Days'.padEnd(5)} ${'Sev'}  Last Event`
  );
  console.log('─'.repeat(95));

  for (const r of rows.sort((a, b) => (b.effConf ?? -1) - (a.effConf ?? -1))) {
    const rawStr = r.rawConf !== null ? `${(r.rawConf * 100).toFixed(0)}%`.padEnd(7) : '  N/A  ';
    const effStr = r.effConf !== null ? `${(r.effConf * 100).toFixed(0)}%`.padEnd(9) : 'N/A      ';
    const decayStr = r.days !== null ? `${(r.decay * 100).toFixed(0)}%`.padEnd(6) : '—     ';
    const daysStr = r.days !== null ? `${r.days}d`.padEnd(5) : '—    ';
    const staleMark = r.isStale ? ' ◀' : '';
    const name42 = r.name.length > 40 ? r.name.substring(0, 39) + '…' : r.name;
    const lastStr = r.lastEventTime
      ? new Date(r.lastEventTime).toLocaleDateString()
      : 'never';
    console.log(
      `${name42.padEnd(42)} ${rawStr} ${effStr} ${decayStr} ${daysStr}  ${r.severity.padEnd(3)} ${lastStr}${staleMark}`
    );
  }

  console.log();
  console.log(`Summary: ${rows.length} patterns, ${staleCount} stale (30+ days), ${rows.length - staleCount} healthy`);

  if (APPLY) {
    // Update patterns with decayed confidence (write decayed value to a "decayed_conf" field)
    // Actually --apply should write decay metadata back to ci-state.json for use by other tools
    const state2 = loadState();
    if (!state2.patterns) state2.patterns = {};
    if (!state2.patterns.decayReport) state2.patterns.decayReport = {};
    state2.patterns.decayReport.generatedAt = new Date().toISOString();
    state2.patterns.decayReport.patterns = rows.map(r => ({
      name: r.name,
      rawConf: r.rawConf,
      effConf: r.effConf,
      decayFactor: r.decay,
      daysSinceEvent: r.days,
      lastEventTime: r.lastEventTime,
      isStale: r.isStale,
    }));
    writeFileSync(STATE_FILE, JSON.stringify(state2, null, 2));
    console.log('\nDecay report written to ci-state.json (patterns.decayReport).');
  }
  console.log();
}

run();
