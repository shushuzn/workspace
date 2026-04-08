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

  // Extract individual tool counts
  const toolCounts = {};
  const toolLines = lines.filter(l => l.trim().startsWith('- '));
  for (const tl of toolLines) {
    const m = tl.match(/^- ([^(]+)\((\d+)\)$/);
    if (m) toolCounts[m[1].trim()] = parseInt(m[2]);
  }

  // Insight: Edit + Write + 0 seeds = modifying without creating
  if ((toolCounts['Edit'] || 0) >= 3 && (toolCounts['Write'] || 0) >= 3 && summary.includes('0 seeds')) {
    insights.push({
      title: 'Modifying without creating',
      obs: `Edit(${toolCounts['Edit']}) + Write(${toolCounts['Write']}) but 0 seeds — working on existing code, not generating new ideas`,
    });
  }

  // Insight: Read-dominant workflow
  const readCount = toolCounts['Read'] || 0;
  const editCount = toolCounts['Edit'] || 0;
  if (readCount > editCount * 3 && readCount > 10) {
    insights.push({
      title: 'Read-heavy workflow',
      obs: `Read(${readCount}) vs Edit(${editCount}) — reading far more than editing, possible research or review mode`,
    });
  }

  // Insight: Shell-only session (high Bash, minimal code tools)
  const bashCount = toolCounts['Bash'] || 0;
  const codeTools = (toolCounts['Edit'] || 0) + (toolCounts['Write'] || 0) + (toolCounts['Grep'] || 0);
  if (bashCount > 20 && codeTools < 5) {
    insights.push({
      title: 'Shell-only session',
      obs: `Bash(${bashCount}) with minimal code tools — check if work could be scripted instead of manual commands`,
    });
  }

  // Insight: Many tools but 0 seeds = no idea generation
  const totalTools = Object.values(toolCounts).reduce((s, v) => s + v, 0);
  const promptMatch = summary.match(/(\d+) user prompts/);
  const prompts = promptMatch ? parseInt(promptMatch[1]) : 0;
  if (totalTools > 30 && prompts > 0 && summary.includes('0 seeds')) {
    insights.push({
      title: 'Productive session but no seeds',
      obs: `${totalTools} tool calls, ${prompts} prompts, 0 seeds — ideas未被记录，应检查是否需要 brainstorm`,
    });
  }

  // Insight: High Write = creating new files
  if ((toolCounts['Write'] || 0) >= 10) {
    insights.push({
      title: 'High file creation activity',
      obs: `Write(${toolCounts['Write']}) — many new files created, good candidate for seed if project-scoped`,
    });
  }

  if (insights.length === 0) return '';

  // Read existing insights for deduplication and counter
  let existing = '';
  if (existsSync(INSIGHTS_FILE)) {
    existing = readFileSync(INSIGHTS_FILE, 'utf-8');
  }

  // Deduplicate: skip if title AND observation both already exist
  const newInsights = [];
  for (const ins of insights) {
    if (!existing.includes(ins.title) || !existing.includes(ins.obs)) {
      newInsights.push(ins);
    }
  }
  if (newInsights.length === 0) return '';

  // Count existing insights to get next number
  let counter = 1;
  const matches = existing.match(/### (\d+)\./g);
  if (matches) {
    const nums = matches.map(m => parseInt(m.match(/\d+/)[0]));
    counter = Math.max(...nums) + 1;
  }

  let md = '';
  for (const ins of newInsights) {
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
