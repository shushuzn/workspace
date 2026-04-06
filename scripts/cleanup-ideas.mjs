#!/usr/bin/env node
/**
 * scripts/cleanup-ideas.mjs
 * Cleans up stale seeds from the idea pool:
 * - seed > 3 days old → mark as dormant
 * - active (seed/dormant/proposal/running) > 7 days old → kill
 * - Active entries > MAX_ACTIVE entries → kill lowest-score ones
 * Cap: MAX_ACTIVE = 100 (only active entries count; shipped/killed are exempt)
 */
import { readFileSync, writeFileSync } from 'fs';
import { join } from 'path';

const ideasPath = join(process.cwd(), '.omc', 'innovation', 'ideas.md');

function parseDate(str) {
  const y = parseInt(str.slice(0, 4));
  const m = parseInt(str.slice(4, 6)) - 1;
  const d = parseInt(str.slice(6, 8));
  return new Date(y, m, d);
}

function daysBetween(date1, date2) {
  return Math.floor(Math.abs(date2 - date1) / (1000 * 60 * 60 * 24));
}

function formatDate(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  return `${y}${m}${d}`;
}

const content = readFileSync(ideasPath, 'utf-8');
const lines = content.split('\n');
const now = new Date();
now.setHours(0, 0, 0, 0);
const HEADER_LINES = 8;

const header = lines.slice(0, HEADER_LINES);
let allEntries = lines.slice(HEADER_LINES).filter(l => l.trim());

const SCORE_RE = /\[score:(\d+)x(\d+)\]/;
const STAGE_RE = /^\- \[(\d{8})\] (\S+)/;
const F_RE = /\[f:(\d)\]/;

// Pass 1: age-based cleanup (seed>3d→dormant, >7d→kill; dormant/proposal/running >7d→kill)
// Returns { entries, stats }
function ageCleanup(entries) {
  const newEntries = [];
  let dormantAdded = 0, killedByAge = 0;
  const stats = { seed: 0, shipped: 0, killed: 0, dormant: 0, proposal: 0, running: 0, f1: 0, f2: 0, f3: 0, f4: 0, f5: 0 };

  for (const line of entries) {
    const stageMatch = line.match(STAGE_RE);
    const scoreMatch = line.match(SCORE_RE);
    const fMatch = line.match(F_RE);
    const stage = stageMatch ? stageMatch[2] : 'unknown';
    const days = stageMatch ? daysBetween(parseDate(stageMatch[1]), now) : -1;

    stats[stage] = (stats[stage] || 0) + 1;
    if (fMatch) {
      const fv = parseInt(fMatch[1]);
      if (fv === 1) stats.f1++;
      else if (fv === 2) stats.f2++;
      else if (fv === 3) stats.f3++;
      else if (fv === 4) stats.f4++;
      else if (fv === 5) stats.f5++;
    }

    const isActive = ['seed', 'dormant', 'proposal', 'running'].includes(stage);

    if (isActive) {
      if (days > 7) {
        // Kill: too old without transition
        const s = scoreMatch ? `${scoreMatch[1]}x${scoreMatch[2]}` : '1x1';
        const fv = fMatch ? fMatch[1] : '1';
        const newLine = line
          .replace(/^\- \[(\d{8})\] (\S+)/, `- [${stageMatch[1]}] killed`)
          .replace(/\]\s*([^\[]+)$/, (m, rest) => `] [score:${s}] [f:${fv}] ${rest} | killed:${formatDate(now)} auto-cleanup`);
        newEntries.push(newLine);
        killedByAge++;
        console.log(`  🗑  Kill(${days}d): ${line.substring(0, 70)}`);
      } else if (days > 3 && stage === 'seed') {
        // Dormant: seed too old
        const newLine = line.replace(/\] seed \[/, '] dormant [');
        newEntries.push(newLine);
        dormantAdded++;
        console.log(`  💤  Dormant(${days}d): ${line.substring(0, 70)}`);
      } else {
        newEntries.push(line);
      }
    } else {
      newEntries.push(line); // shipped/killed always kept
    }
  }

  return { entries: newEntries, stats, killedByAge, dormantAdded };
}

// Pass 2: cap non-seed entries (shipped/killed/dormant/proposal/running) to MAX_NON_SEED
// Seeds are NEVER removed by cap — they are always preserved
const MAX_NON_SEED = 100;

function applyCap(entries, stats) {
  const nonSeedEntries = entries.filter(l => {
    const m = l.match(STAGE_RE);
    return m && m[2] !== 'seed';
  });

  if (nonSeedEntries.length <= MAX_NON_SEED) {
    return { entries, removedByCap: 0 };
  }

  // Sort non-seed: lowest score first (to remove those), then older first
  nonSeedEntries.sort((a, b) => {
    const sa = a.match(SCORE_RE);
    const sb = b.match(SCORE_RE);
    const da = a.match(STAGE_RE);
    const db = b.match(STAGE_RE);
    const scoreA = sa ? parseInt(sa[1]) * parseInt(sa[2]) : 1;
    const scoreB = sb ? parseInt(sb[1]) * parseInt(sb[2]) : 1;
    const dateA = da ? parseDate(da[1]).getTime() : 0;
    const dateB = db ? parseDate(db[1]).getTime() : 0;
    if (scoreA !== scoreB) return scoreA - scoreB;
    return dateA - dateB;
  });

  const toRemove = nonSeedEntries.slice(0, nonSeedEntries.length - MAX_NON_SEED);
  const toRemoveSet = new Set(toRemove);
  let removedByCap = 0;
  const newEntries = entries.map(line => {
    if (toRemoveSet.has(line)) {
      const sm = line.match(SCORE_RE);
      const fm = line.match(F_RE);
      const stm = line.match(STAGE_RE);
      const s = sm ? `${sm[1]}x${sm[2]}` : '1x1';
      const fv = fm ? fm[1] : '1';
      const d = stm ? stm[1] : formatDate(now);
      const stageMatch = line.match(STAGE_RE);
      const stage = stageMatch ? stageMatch[2] : 'unknown';
      removedByCap++;
      console.log(`  🔪  Cap-remove(${stage},score${s}): ${line.substring(0, 60)}`);
      return line
        .replace(/^\- \[(\d{8})\] (\S+)/, `- [${d}] killed`)
        .replace(/\]\s*([^\[]+)$/, (m, rest) => `] [score:${s}] [f:${fv}] ${rest} | killed:${formatDate(now)} pool-cap`);
    }
    return line;
  });

  return { entries: newEntries, removedByCap };
}

// Run
const { entries: afterAge, stats, killedByAge, dormantAdded } = ageCleanup(allEntries);
const { entries: finalEntries, removedByCap } = applyCap(afterAge, stats);

const newContent = [...header, ...finalEntries].join('\n') + '\n';
writeFileSync(ideasPath, newContent, 'utf-8');

const total = stats.seed + stats.shipped + stats.killed + stats.dormant + stats.proposal + stats.running;
console.log('\n=== Pool Stats ===');
console.log(`total: ${total} | seed: ${stats.seed} | shipped: ${stats.shipped} | killed: ${stats.killed} | dormant: ${stats.dormant} | proposal: ${stats.proposal} | running: ${stats.running}`);
console.log(`f:1:${stats.f1} | f:2:${stats.f2} | f:3:${stats.f3} | f:4:${stats.f4} | f:5:${stats.f5}`);
console.log(`\nEntries: ${allEntries.length} → ${finalEntries.length} | age-killed: ${killedByAge} | cap-removed: ${removedByCap} | dormant: ${dormantAdded}`);
