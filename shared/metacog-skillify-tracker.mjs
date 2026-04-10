#!/usr/bin/env node
/**
 * metacog-skillify-tracker.mjs — track skillify trigger frequency
 * Reads brainstorm-metacognition.jsonl and outputs skillify trigger stats
 * Usage: node shared/metacog-skillify-tracker.mjs --init
 */
import { readFileSync, existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const META_FILE = join(__DIR, '..', '.omc', 'innovation', 'brainstorm-metacognition.jsonl');
const SKILLS_DIR = join(__DIR, '..', '.claude', 'skills');

function loadMetacog() {
  if (!existsSync(META_FILE)) return [];
  return readFileSync(META_FILE, 'utf8').trim().split('\n')
    .filter(Boolean).map(l => { try { return JSON.parse(l); } catch { return null; } })
    .filter(Boolean);
}

function main() {
  const mode = process.argv.includes('--init') ? 'init' : 'track';
  const entries = loadMetacog();

  if (entries.length === 0) {
    console.log('[SKILLIFY-TRACKER] No metacognition entries found');
    return;
  }

  // Count skillify triggers per entry
  const skillifyEntries = entries.filter(e =>
    e.seed_critiques && e.seed_critiques.some(s => s.skillified === true)
  );

  // Extract skillify-related data
  const skillifyCount = skillifyEntries.length;
  const totalSeeds = entries.reduce((sum, e) => sum + (e.batch_seed_count || 0), 0);
  const avgScore = entries.reduce((sum, e) => sum + (e.batch_avg_score || 0), 0) / entries.length;

  // Count existing skills
  const skillsCount = existsSync(SKILLS_DIR) ?
    readdirSync(SKILLS_DIR).filter(f => f.endsWith('.md') && f.includes('SKILL')).length
    : 0;

  console.log(`\n=== Skillify Tracker ===`);
  console.log(`  Total batches: ${entries.length}`);
  console.log(`  Total seeds shipped: ${totalSeeds}`);
  console.log(`  Skillify triggers: ${skillifyCount}`);
  console.log(`  Trigger rate: ${totalSeeds > 0 ? ((skillifyCount / totalSeeds) * 100).toFixed(1) : 0}%`);
  console.log(`  Skills created: ${skillsCount}`);
  console.log(`  Avg batch score: ${avgScore.toFixed(1)}`);

  if (mode === 'init') {
    console.log('\n[SKILLIFY-TRACKER] Initialized');
  }
}

main();
