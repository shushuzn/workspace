#!/usr/bin/env node
/**
 * OMC Semantic-style Insight Retrieval
 * Uses keyword expansion + multi-field scoring instead of embeddings.
 * Mimics semantic search without requiring embedding model.
 *
 * Usage:
 *   node insight-semantic-retrieve.mjs --context ".omc/scripts/hook"
 *   node insight-semantic-retrieve.mjs --keywords "hook,bash"
 */
import { existsSync, readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const INSIGHTS_FILE = resolve(__dirname, '../state/session-insights.md');

// Synonym expansions for domain terms
const SYNONYMS = {
  hook: ['trigger', 'mcp', 'event', 'pretool', 'posttool'],
  bash: ['shell', 'command', 'cli', 'terminal', 'exec'],
  insight: ['learn', 'pattern', 'observation', 'knowledge'],
  debug: ['bug', 'fix', 'error', 'issue', 'problem'],
  write: ['file', 'create', 'generate', 'output'],
  edit: ['modify', 'change', 'update', 'string', 'escape'],
  session: ['trajectory', 'drain', 'context', 'session-start'],
  task: ['track', 'taskcreate', 'taskupdate', 'todo'],
  jsonl: ['json', 'parse', 'log', 'transcript', 'events'],
  workflow: ['loop', 'pipeline', 'sequence', 'inspect'],
  memory: ['store', 'recall', 'retrieve', 'context'],
  filter: ['reject', 'skip', 'quality', 'gate'],
  verify: ['verify', 'expected', 'actual', 'validate', 'check'],
  commit: ['git', 'branch', 'stash'],
  regex: ['pattern', 'match', 'escape', 'test'],
  quality: ['insight', 'observation', 'rule', 'meaningful'],
  auto: ['auto-seed', 'auto-insight', 'trigger', 'automatic'],
  session_change: ['session change', 'session mismatch', 'reset', 'new session'],
  stale: ['stale', 'old', 'prior', 'yesterday', 'leftover'],
};

function expandKeywords(kw) {
  const expanded = [kw];
  const lower = kw.toLowerCase();
  for (const [key, syns] of Object.entries(SYNONYMS)) {
    if (lower.includes(key) || syns.some(s => lower.includes(s))) {
      expanded.push(key, ...syns);
    }
  }
  return [...new Set(expanded.flat())];
}

function extractKeywordsFromPath(filePath) {
  if (!filePath) return [];
  const parts = filePath.split(/[\/\\_\-\.\:]/).filter(Boolean);
  const kw = [];
  for (const p of parts) {
    kw.push(p);
    kw.push(...(SYNONYMS[p.toLowerCase()] || []));
  }
  return [...new Set(kw)];
}

function scoreInsight(insight, keywords, contextKw) {
  const allKw = new Set([...keywords, ...contextKw]);
  let score = 0;

  // Score each field
  for (const kw of allKw) {
    const lkw = kw.toLowerCase();
    // Title match (highest weight)
    if (insight.title.toLowerCase().includes(lkw)) score += 10;
    // Observation match
    if (insight.observation.toLowerCase().includes(lkw)) score += 5;
    // Fix match
    if (insight.fix.toLowerCase().includes(lkw)) score += 3;
    // Rule match
    if (insight.rule.toLowerCase().includes(lkw)) score += 2;
    // Block text match
    if (insight.block.toLowerCase().includes(lkw)) score += 1;
  }

  // Executed insights get small bonus (prefer proven fixes)
  if (insight.executed) score += 0.5;

  // Auto-generated without keywords get small penalty
  if (insight.title.includes('[auto-generated]') && score < 10) score *= 0.5;

  return score;
}

function parseInsights(content) {
  const lines = content.split('\n');
  const insights = [];
  let current = null;

  for (const line of lines) {
    const tm = line.match(/^### (\d+)\.\s+\[(.+?)\]/);
    if (tm) {
      if (current) insights.push(current);
      current = {
        num: parseInt(tm[1]),
        title: tm[2],
        executed: line.includes('✅ EXECUTED'),
        block: line,
        observation: '',
        fix: '',
        rule: '',
      };
    } else if (current) {
      current.block += ' ' + line;
      if (line.includes('**Observation**')) current.observation += ' ' + line.replace(/\*\*/g, '');
      if (line.includes('**Fix**')) current.fix += ' ' + line.replace(/\*\*/g, '');
      if (line.includes('**Rule**')) current.rule += ' ' + line.replace(/\*\*/g, '');
    }
  }
  if (current) insights.push(current);
  return insights;
}

function retrieve(contextKw, keywords) {
  if (!existsSync(INSIGHTS_FILE)) return [];
  const content = readFileSync(INSIGHTS_FILE, 'utf-8');
  const insights = parseInsights(content);

  const ctxKw = extractKeywordsFromPath(contextKw);
  const kw = [...new Set([...keywords.map(k => k.trim()), ...ctxKw])];
  const expanded = new Set(kw.flatMap(k => expandKeywords(k)));

  const scored = insights
    .map(i => ({ ...i, score: scoreInsight(i, [...expanded], ctxKw) }))
    .filter(i => i.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  return scored;
}

function formatInsight(i) {
  const status = i.executed ? ' ✅' : ' ⚠️';
  const fix = (i.fix.match(/Fix:\s*(.+?)(?:\n|$)/i)?.[1] || 'N/A').trim().slice(0, 120);
  return `### ${i.num}. ${i.title}${status}
> ${fix}${fix.length >= 120 ? '...' : ''}`;
}

// ── CLI ─────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const ctxIdx = args.indexOf('--context');
const kwIdx = args.indexOf('--keywords');

const context = ctxIdx >= 0 && args[ctxIdx + 1] && !args[ctxIdx + 1].startsWith('--') ? args[ctxIdx + 1] : '';
const keywords = kwIdx >= 0 ? args[kwIdx + 1].split(',').map(k => k.trim()) : [];

if (args.includes('--help')) {
  console.log('Usage: insight-semantic-retrieve.mjs --context ".omc/scripts/hook" --keywords "hook,session"');
  process.exit(0);
}

const results = retrieve(context, keywords);
if (results.length === 0) {
  console.log('No relevant insights found.');
} else {
  console.log(`\n## Relevant Insights (${results.length})\n`);
  for (const r of results) {
    console.log(formatInsight(r));
    console.log();
  }
}

export { retrieve };
