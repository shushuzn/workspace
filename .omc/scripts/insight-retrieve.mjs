#!/usr/bin/env node
/**
 * OMC Insight Tag Retrieval
 * Given a context (file path, keywords), retrieve relevant past insights.
 *
 * Usage:
 *   node insight-retrieve.mjs --context ".omc/scripts/hook"
 *   node insight-retrieve.mjs --keywords "bash hook session"
 *   node insight-retrieve.mjs --context ".omc/scripts/hook" --keywords "session change"
 */
import { existsSync, readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const INSIGHTS_FILE = resolve(__dirname, '../state/session-insights.md');

function log(...a) { console.log('[insight-retrieve]', ...a); }

const TAG_VOCAB = ['hook', 'bash', 'insight', 'debug', 'write', 'edit', 'session', 'task', 'jsonl', 'workflow', 'memory', 'filter', 'quality', 'verify', 'commit', 'regex'];

function extractTags(line) {
  const tagMatches = line.match(/#(\w+)/g) || [];
  const tags = tagMatches.map(t => t.slice(1));
  // Also infer from keyword matching
  const lowerLine = line.toLowerCase();
  const inferred = TAG_VOCAB.filter(tag => {
    if (tags.includes(tag)) return false;
    const patterns = {
      hook: ['hook', 'trigger', 'mcp'],
      bash: ['bash', 'shell', 'command', 'cli'],
      insight: ['insight', 'learn', 'pattern'],
      debug: ['debug', 'bug', 'fix'],
      write: ['write', 'file', 'edit'],
      edit: ['edit', 'string', 'escape'],
      session: ['session', 'trajectory', 'drain'],
      task: ['task', 'track', 'create', 'update'],
      jsonl: ['jsonl', 'json', 'parse', 'log'],
      workflow: ['workflow', 'loop', 'inspect'],
      memory: ['memory', 'store', 'recall'],
      filter: ['filter', 'reject', 'quality'],
      quality: ['quality', 'insight', 'observation'],
      verify: ['verify', 'expected', 'actual'],
      commit: ['commit', 'git', 'branch'],
      regex: ['regex', 'pattern', 'match', 'escape'],
    };
    return patterns[tag]?.some(p => lowerLine.includes(p)) || false;
  });
  return [...new Set([...tags, ...inferred])];
}

function parseInsights(content) {
  const lines = content.split('\n');
  const insights = [];
  let current = null;

  for (const line of lines) {
    const titleMatch = line.match(/^### (\d+)\.\s+\[(.+?)\]/);
    if (titleMatch) {
      if (current) insights.push(current);
      current = {
        num: parseInt(titleMatch[1]),
        title: titleMatch[2],
        tags: extractTags(line),
        lines: [line],
        executed: line.includes('✅ EXECUTED'),
        observation: '',
        fix: '',
        rule: '',
      };
    } else if (current) {
      current.lines.push(line);
      if (line.includes('**Observation**')) current.observation += ' ' + line;
      if (line.includes('**Fix**')) current.fix += ' ' + line;
      if (line.includes('**Rule**')) current.rule += ' ' + line;
      const lineTags = extractTags(line);
      current.tags = [...new Set([...current.tags, ...lineTags])];
    }
  }
  if (current) insights.push(current);
  return insights;
}

function scoreInsight(insight, contextKw, filePath) {
  let score = 0;
  const ctx = contextKw.map(k => k.toLowerCase());
  const fp = (filePath || '').toLowerCase();

  // Tag overlap
  for (const tag of insight.tags) {
    if (ctx.some(k => k === tag || k.includes(tag))) score += 3;
    if (fp.includes(tag)) score += 2;
  }

  // Keyword in title
  for (const k of ctx) {
    if (insight.title.toLowerCase().includes(k)) score += 5;
    if (insight.observation.toLowerCase().includes(k)) score += 2;
    if (insight.fix.toLowerCase().includes(k)) score += 1;
    if (insight.rule.toLowerCase().includes(k)) score += 1;
  }

  // Executed insights slightly deprioritized (want fresh + executed)
  if (insight.executed) score -= 1;

  return score;
}

function retrieve(context, keywords, maxResults = 5) {
  if (!existsSync(INSIGHTS_FILE)) {
    log('no insights file found');
    return [];
  }
  const content = readFileSync(INSIGHTS_FILE, 'utf-8');
  const insights = parseInsights(content);

  const allKw = [
    ...keywords,
    ...(context ? context.split(/[\/\\_\-\.]/).filter(Boolean).map(p => p.toLowerCase()) : []),
  ];

  const scored = insights
    .filter(i => !i.title.includes('[auto-generated]') || i.tags.length > 0)
    .map(i => ({ ...i, score: scoreInsight(i, allKw, context) }))
    .filter(i => i.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxResults);

  return scored;
}

function formatInsight(i) {
  const tags = i.tags.length > 0 ? ' #' + i.tags.join(' #') : '';
  const status = i.executed ? ' ✅' : '';
  const fix = i.fix.match(/\*\*Fix\*\*:\s*(.+)/)?.[1]?.trim() || 'N/A';
  return `### ${i.num}. ${i.title}${status}${tags}
> ${fix.slice(0, 120)}${fix.length > 120 ? '...' : ''}`;
}

// ── CLI ─────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const ctxIdx = args.indexOf('--context');
const kwIdx = args.indexOf('--keywords');
const ctx = ctxIdx >= 0 && args[ctxIdx + 1] && !args[ctxIdx + 1].startsWith('--') ? args[ctxIdx + 1] : '';
const keywords = kwIdx >= 0 ? args[kwIdx + 1]?.split(',').map(k => k.trim()) || [] : [];

if (args.includes('--help') || args.includes('-h')) {
  console.log(`Usage: insight-retrieve.mjs --context ".omc/scripts/hook" --keywords "session,bash"`);
  console.log(`Usage: insight-retrieve.mjs --context ".omc/scripts/hook"`);
  console.log(`Usage: insight-retrieve.mjs --keywords "hook,bash"`);
  process.exit(0);
}

const results = retrieve(ctx, keywords);
if (results.length === 0) {
  console.log('No relevant insights found.');
} else {
  console.log(`\n## Relevant Past Insights (${results.length})\n`);
  for (const r of results) {
    console.log(formatInsight(r));
    console.log();
  }
}

export { retrieve };
