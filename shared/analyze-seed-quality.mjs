#!/usr/bin/env node
/**
 * analyze-seed-quality.mjs
 * Analyze seed pool quality and identify issues
 * Usage: node analyze-seed-quality.mjs [--auto-kill DAYS]
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_FILE = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');

function loadSeeds() {
  if (!existsSync(IDEAS_FILE)) return [];
  const content = readFileSync(IDEAS_FILE, 'utf8');
  const lines = content.split('\n');
  const seeds = [];
  for (const line of lines) {
    if (!line.includes('seed [brainstorm]')) continue;
    const shipMatch = line.match(/shipped:(\d{8})/);
    const killedMatch = line.match(/killed:(\d{8})\s+(\w+)/);
    const scoreMatch = line.match(/score:(\d+)x(\d+)/);
    const fMatch = line.match(/\[f:(\d+)\]/);
    const dateMatch = line.match(/^\- \[(\d{8})\]/);

    seeds.push({
      date: dateMatch ? dateMatch[1] : null,
      shipped: shipMatch ? shipMatch[1] : null,
      killed: killedMatch ? { date: killedMatch[1], reason: killedMatch[2] } : null,
      score: scoreMatch ? parseInt(scoreMatch[1]) * parseInt(scoreMatch[2]) : 0,
      f: fMatch ? parseInt(fMatch[1]) : null,
      raw: line
    });
  }
  return seeds;
}

function analyzeQuality(seeds) {
  const stats = {
    total: seeds.length,
    shipped: seeds.filter(s => s.shipped).length,
    killed: seeds.filter(s => s.killed).length,
    active: seeds.filter(s => !s.shipped && !s.killed).length,
    avgScore: 0,
    byF: {}
  };

  // Calculate avg score for shipped seeds
  const shippedSeeds = seeds.filter(s => s.shipped);
  if (shippedSeeds.length > 0) {
    stats.avgScore = shippedSeeds.reduce((sum, s) => sum + s.score, 0) / shippedSeeds.length;
  }

  // Group by f score
  for (const s of seeds) {
    if (s.f) {
      if (!stats.byF[s.f]) stats.byF[s.f] = { total: 0, shipped: 0 };
      stats.byF[s.f].total++;
      if (s.shipped) stats.byF[s.f].shipped++;
    }
  }

  return stats;
}

function findStaleKilled(seeds, days = 7) {
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);
  const cutoffStr = cutoff.toISOString().slice(0, 8).replace(/-/g, '');

  return seeds.filter(s => {
    if (!s.killed) return false;
    return s.killed.date < cutoffStr;
  });
}

const args = process.argv.slice(2);
const autoKill = args.includes('--auto-kill');

console.log('=== Seed Quality Analysis ===\n');

const seeds = loadSeeds();
const stats = analyzeQuality(seeds);

console.log(`Total seeds: ${stats.total}`);
console.log(`Shipped: ${stats.shipped} (${((stats.shipped/stats.total)*100).toFixed(1)}%)`);
console.log(`Killed: ${stats.killed} (${((stats.killed/stats.total)*100).toFixed(1)}%)`);
console.log(`Active: ${stats.active}`);
console.log(`Avg score (shipped): ${stats.avgScore.toFixed(1)}`);

console.log('\n【By f:score】');
for (const f of Object.keys(stats.byF).sort((a, b) => a - b)) {
  const g = stats.byF[f];
  const rate = ((g.shipped / g.total) * 100).toFixed(0);
  console.log(`  f:${f}: ${g.total} seeds, ${g.shipped} shipped (${rate}%)`);
}

if (autoKill) {
  const stale = findStaleKilled(seeds, 7);
  console.log(`\n【Stale killed (>7 days, to remove)】: ${stale.length}`);
  if (stale.length > 0) {
    for (const s of stale.slice(0, 5)) {
      console.log(`  ${s.raw.slice(0, 80)}...`);
    }
  }
}
