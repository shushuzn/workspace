#!/usr/bin/env node
/**
 * scripts/ci-pattern-feedback.mjs
 * Records engineer feedback on CI pattern matches to build confidence scores.
 *
 * Usage:
 *   node scripts/ci-pattern-feedback.mjs confirm <pattern_name> [--notes=<text>]
 *   node scripts/ci-pattern-feedback.mjs reject <pattern_name> [--notes=<text>]
 *   node scripts/ci-pattern-feedback.mjs list [--sort=confidence|occurrences]
 *   node scripts/ci-pattern-feedback.mjs report
 *
 * Pattern confidence = confirmations / (confirmations + rejections)
 * High confidence (>0.8) → auto-suggest fix without human review
 * Low confidence (<0.3) → deprioritize in ci-diagnose.mjs
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PATTERN_FILE   = join(__dirname, '..', 'scripts', 'ci-failure-patterns.jsonl');
const FEEDBACK_FILE  = join(__dirname, '..', 'ci-pattern-feedback.jsonl');

const MODE = process.argv[2];
const args = process.argv.slice(3);

function parseArgs(args) {
  const result = {};
  for (const arg of args) {
    if (arg.startsWith('--')) {
      const [k, ...vParts] = arg.slice(2).split('=');
      if (k) result[k] = vParts.join('=') || true;
    }
  }
  return result;
}

function loadPatterns() {
  if (!existsSync(PATTERN_FILE)) return [];
  const content = readFileSync(PATTERN_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function savePatterns(patterns) {
  writeFileSync(PATTERN_FILE, patterns.map(p => JSON.stringify(p)).join('\n') + '\n');
}

function loadFeedback() {
  if (!existsSync(FEEDBACK_FILE)) return [];
  const content = readFileSync(FEEDBACK_FILE, 'utf8');
  return content.trim().split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

function appendFeedback(entry) {
  const line = JSON.stringify(entry) + '\n';
  writeFileSync(FEEDBACK_FILE, line, { flag: 'a' });
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  if (MODE === 'confirm' || MODE === 'reject') {
    const patternName = args[0];
    const opts = parseArgs(args);
    if (!patternName) {
      console.error('Usage: ci-pattern-feedback.mjs confirm|reject <pattern_name> [--notes=<text>]');
      process.exit(1);
    }

    const patterns = loadPatterns();
    const pattern = patterns.find(p => p.name === patternName);
    if (!pattern) {
      console.error(`Pattern not found: ${patternName}`);
      console.error('Run: ci-pattern-feedback.mjs list');
      process.exit(1);
    }

    const feedback = {
      type: MODE,
      pattern: patternName,
      date: new Date().toISOString().split('T')[0],
      notes: opts.notes || null
    };

    appendFeedback(feedback);

    // Update pattern confidence in place
    const allFeedback = loadFeedback();
    const conf = allFeedback.filter(f => f.pattern === patternName);
    const confirmations = conf.filter(f => f.type === 'confirm').length;
    const rejections = conf.filter(f => f.type === 'reject').length;
    const confidence = (confirmations + rejections) > 0
      ? confirmations / (confirmations + rejections)
      : null;

    pattern.confirmations = confirmations;
    pattern.rejections = rejections;
    pattern.confidence = confidence !== null ? parseFloat(confidence.toFixed(3)) : null;

    savePatterns(patterns);

    const icon = MODE === 'confirm' ? '✅' : '❌';
    console.log(`${icon} Feedback recorded for "${patternName}"`);
    console.log(`  Confirmations: ${confirmations} | Rejections: ${rejections}`);
    if (confidence !== null) console.log(`  Confidence: ${(confidence * 100).toFixed(0)}%`);
    if (opts.notes) console.log(`  Notes: ${opts.notes}`);
    return;
  }

  if (MODE === 'list') {
    const patterns = loadPatterns();
    const sortBy = args.find(a => a.startsWith('--sort='))?.split('=')[1] || 'confidence';

    const sorted = [...patterns].sort((a, b) => {
      if (sortBy === 'confidence') {
        const ca = a.confidence ?? 0.5;
        const cb = b.confidence ?? 0.5;
        return cb - ca;
      }
      if (sortBy === 'occurrences') {
        return (b.occurrences || 0) - (a.occurrences || 0);
      }
      return 0;
    });

    console.log(`\n=== CI Failure Patterns (${patterns.length}) ===\n`);
    for (const p of sorted) {
      const conf = p.confidence !== null && p.confidence !== undefined
        ? `${(p.confidence * 100).toFixed(0)}%`
        : 'N/A';
      const confIcon = p.confidence === null || p.confidence === undefined ? '❓'
        : p.confidence >= 0.8 ? '🟢'
        : p.confidence >= 0.5 ? '🟡'
        : '🔴';
      console.log(`${confIcon} ${p.name} (${p.severity})`);
      console.log(`   Pattern: ${p.pattern}`);
      console.log(`   Confidence: ${conf} | Occurrences: ${p.occurrences} | Confirm: ${p.confirmations} | Reject: ${p.rejections}`);
      console.log(`   Hint: ${p.hint}`);
      console.log(`   Last seen: ${p.lastSeen || 'never'}`);
      console.log();
    }
    return;
  }

  if (MODE === 'report') {
    const patterns = loadPatterns();
    const highConf = patterns.filter(p => p.confidence !== null && p.confidence >= 0.8);
    const lowConf = patterns.filter(p => p.confidence !== null && p.confidence <= 0.3);
    const unknown = patterns.filter(p => p.confidence === null || p.confidence === undefined);

    console.log(`\n=== Pattern Confidence Report ===\n`);
    console.log(`Total patterns: ${patterns.length}`);
    console.log(`High confidence (≥80%): ${highConf.length}`);
    console.log(`Low confidence (≤30%): ${lowConf.length}`);
    console.log(`Unknown: ${unknown.length}\n`);

    if (highConf.length > 0) {
      console.log('🟢 High confidence (auto-fix OK):');
      for (const p of highConf) {
        console.log(`   ${p.name}: ${(p.confidence * 100).toFixed(0)}% — ${p.fix}`);
      }
      console.log();
    }

    if (lowConf.length > 0) {
      console.log('🔴 Low confidence (needs review):');
      for (const p of lowConf) {
        console.log(`   ${p.name}: ${(p.confidence * 100).toFixed(0)}% — verify pattern is correct`);
      }
      console.log();
    }

    if (unknown.length > 0) {
      console.log('❓ Unknown (no feedback yet):');
      for (const p of unknown) {
        console.log(`   ${p.name} (${p.occurrences} occurrences)`);
      }
      console.log();
    }

    console.log('Usage:');
    console.log('  ci-pattern-feedback.mjs confirm <name> [--notes=<text>]');
    console.log('  ci-pattern-feedback.mjs reject <name> [--notes=<text>]');
    console.log();
    return;
  }

  // Default help
  console.log('Usage:');
  console.log('  ci-pattern-feedback.mjs confirm <pattern_name> [--notes=<text>]');
  console.log('  ci-pattern-feedback.mjs reject <pattern_name> [--notes=<text>]');
  console.log('  ci-pattern-feedback.mjs list [--sort=confidence|occurrences]');
  console.log('  ci-pattern-feedback.mjs report');
}

main().catch(e => { console.error(e); process.exit(1); });
