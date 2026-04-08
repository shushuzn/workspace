#!/usr/bin/env node
/**
 * OMC Insight Generator
 * Analyzes trajectory → generates rule-based insights → writes to session-insights.md
 *
 * Called by hook-session-end-drain.mjs step6 on each session end.
 * No LLM needed — rule-based detection on trajectory metadata.
 */
import { existsSync, readFileSync, writeFileSync, readdirSync, statSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const TRAJ_DIR = resolve(__dirname, '../trajectories');
const INSIGHTS_FILE = resolve(__dirname, '../state/session-insights.md');

function log(...a) { console.log('[insight-gen]', ...a); }

function generateInsights(traj) {
  const lines = traj.split('\n');
  const insights = [];
  const today = new Date().toISOString().split('T')[0];

  // Extract metrics
  const topToolsLine = lines.find(l => l.includes('Top tools:'));
  const summaryLine = lines.find(l => l.includes('Summary:'));
  const patternsLine = lines.find(l => l.includes('Patterns detected:'));

  // Insight: Heavy bash usage (lower threshold)
  if (topToolsLine) {
    const m = topToolsLine.match(/Bash\((\d+)\)/);
    if (m && parseInt(m[1]) > 10) {
      insights.push({
        title: 'Heavy bash usage detected',
        obs: `Bash calls (${m[1]}) in session — review if commands can be consolidated`,
      });
    }
  }

  // Insight: No seeds
  if (summaryLine && summaryLine.includes('0 seeds')) {
    insights.push({
      title: 'No seeds generated',
      obs: 'Session produced no new ideas despite active tool usage',
    });
  }

  // Insight: Debugging mode
  if (patternsLine && patternsLine.includes('debugging mode')) {
    insights.push({
      title: 'Debugging mode session',
      obs: 'High tool-call session with no seeds = fixing, not creating',
    });
  }

  // Insight: Very high tool count
  const summary = summaryLine || '';
  const toolCallMatch = summary.match(/(\d+) tool calls/);
  if (toolCallMatch && parseInt(toolCallMatch[1]) > 100) {
    insights.push({
      title: 'Very high tool-call session',
      obs: `${toolCallMatch[1]} tool calls in single session — check for loop/deadlock patterns`,
    });
  }

  if (insights.length === 0) return '';

  // Count existing insights to get next number
  let counter = 1;
  if (existsSync(INSIGHTS_FILE)) {
    const existing = readFileSync(INSIGHTS_FILE, 'utf-8');
    const matches = existing.match(/### (\d+)\./g);
    if (matches) {
      const nums = matches.map(m => parseInt(m.match(/\d+/)[0]));
      counter = Math.max(...nums) + 1;
    }
  }

  let md = '';
  for (const ins of insights) {
    md += `### ${counter}. ${ins.title} [auto-generated]\n`;
    md += `**Observation**: ${ins.obs}\n`;
    md += `**Rule**: Track this pattern in future sessions\n\n`;
    counter++;
  }

  return md;
}

// Find latest trajectory
function findLatestTraj() {
  if (!existsSync(TRAJ_DIR)) return null;
  let latest = null;
  let latestMtime = 0;
  const files = readdirSync(TRAJ_DIR).filter(f => f.endsWith('.md'));
  for (const f of files) {
    const p = resolve(TRAJ_DIR, f);
    const s = statSync(p);
    if (s.mtimeMs > latestMtime) { latestMtime = s.mtimeMs; latest = p; }
  }
  return latest;
}

const traj = findLatestTraj();
if (!traj) { log('no trajectory found'); process.exit(0); }

const content = readFileSync(traj, 'utf-8');
const out = generateInsights(content);
if (!out) { log('no insight generated'); process.exit(0); }

const existing = existsSync(INSIGHTS_FILE) ? readFileSync(INSIGHTS_FILE, 'utf-8') : '';
writeFileSync(INSIGHTS_FILE, existing + out, 'utf-8');
log('generated insight from', traj.split('/').pop());
