#!/usr/bin/env node
/**
 * OMC Workflow Detector
 * Scans hook-audit.jsonl for repeated tool-call sequences → suggests reusable workflows.
 *
 * Usage:
 *   node hook-workflow-detector.mjs [--min-count 3] [--ngram 3]
 *   node hook-workflow-detector.mjs --emit    Write workflow-patterns.md
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const LOG_PATH = resolve(__dirname, '../state/hook-audit.jsonl');
const OUT_PATH = resolve(__dirname, '../innovation/workflow-patterns.md');

const MIN_COUNT = parseInt(process.argv.find(a => a.startsWith('--min-count='))?.split('=')[1] ?? '3');
const NGRAM_SIZE = parseInt(process.argv.find(a => a.startsWith('--ngram='))?.split('=')[1] ?? '3');

// ── Parse args ────────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

// ── Read audit log ────────────────────────────────────────────────────────────
function readEntries() {
  if (!existsSync(LOG_PATH)) return [];
  const raw = readFileSync(LOG_PATH, 'utf-8');
  return raw.split('\n').filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

// ── Extract tool sequence ─────────────────────────────────────────────────────
function extractToolSequence(entries) {
  const seq = [];
  for (const e of entries) {
    if (e.tool && e.tool !== 'unknown') {
      seq.push(e.tool);
    }
  }
  return seq;
}

// ── N-gram extraction ────────────────────────────────────────────────────────
function extractNgrams(seq, n) {
  if (seq.length < n) return [];
  const grams = [];
  for (let i = 0; i <= seq.length - n; i++) {
    grams.push(seq.slice(i, i + n).join(' → '));
  }
  return grams;
}

// ── Cluster n-grams ───────────────────────────────────────────────────────────
function clusterNgrams(entries) {
  const seq = extractToolSequence(entries);
  const allNgrams = [];

  for (let n = 2; n <= NGRAM_SIZE; n++) {
    allNgrams.push(...extractNgrams(seq, n).map(g => ({ n, gram: g })));
  }

  const counts = {};
  for (const { gram } of allNgrams) {
    counts[gram] = (counts[gram] || 0) + 1;
  }

  return Object.entries(counts)
    .filter(([, count]) => count >= MIN_COUNT)
    .sort((a, b) => b[1] - a[1]);
}

// ── Pattern meaning ─────────────────────────────────────────────────────────
function interpretPattern(gram) {
  const tools = gram.split(' → ');

  // Detect common workflow patterns
  if (tools.includes('Read') && tools.includes('Grep') && tools.includes('Edit')) {
    return '🔍 **Read-Search-Edit workflow**: Investigate code → find patterns → make targeted changes. Common in bug fixing and refactoring.';
  }
  if (tools.includes('Read') && tools.includes('Grep') && tools.includes('Bash')) {
    return '🔍 **Read-Search-Run workflow**: Investigate code → find patterns → run verification commands. Common in testing and debugging.';
  }
  if (tools.includes('Write') && tools.includes('Bash')) {
    return '📝 **Write-Execute workflow**: Create files then run commands. Common in scaffolding and setup.';
  }
  if (tools.includes('Bash') && tools.includes('Bash')) {
    return '⚙️ **Multi-command pipeline**: Multiple shell commands in sequence. Could be consolidated into a single script.';
  }
  if (tools.includes('Edit') && tools.includes('Edit')) {
    return '✏️ **Multi-edit session**: Multiple file edits. Consider batching or creating a shared utility.';
  }
  if (tools.includes('Read') && tools.includes('Write')) {
    return '📋 **Read-Modify-Write pattern**: Load file → modify → save. Common in code generation and transformation.';
  }
  if (tools.includes('Glob') && tools.includes('Read') && tools.includes('Edit')) {
    return '📁 **Find-Read-Edit workflow**: Discover files → read content → make changes. Common in refactoring across multiple files.';
  }
  if (tools.includes('Glob') && tools.includes('Grep')) {
    return '🔎 **File discovery + search**: Find files matching criteria → search within them. Common in cross-file analysis.';
  }

  return `Generic pattern: ${gram}`;
}

// ── Build workflow suggestions ───────────────────────────────────────────────
function buildSuggestions(clusters) {
  const suggestions = [];

  for (const [gram, count] of clusters) {
    const tools = gram.split(' → ');
    const interpretation = interpretPattern(gram);

    suggestions.push({
      id: `wf-${Date.now()}-${Math.random().toString(36).slice(2, 5)}`,
      pattern: gram,
      count,
      tools,
      interpretation,
      suggestion: `Consider consolidating this ${tools.length}-step sequence into a reusable skill or adapter.`,
    });
  }

  return suggestions;
}

// ── Emit workflow-patterns.md ─────────────────────────────────────────────────
function emitMarkdown(suggestions) {
  const today = new Date().toISOString().split('T')[0];
  let md = `# Workflow Patterns\n\n`;
  md += `*Auto-generated by hook-workflow-detector.mjs — ${today}*\n\n`;
  md += `Detected repeated tool-call sequences from \`hook-audit.jsonl\`.\n\n`;

  if (suggestions.length === 0) {
    md += `No recurring patterns found yet (need ≥${MIN_COUNT} occurrences).\n`;
    return md;
  }

  for (const s of suggestions) {
    md += `## ${s.interpretation.split('**')[1] || s.pattern}\n\n`;
    md += `**Pattern**: \`${s.pattern}\`\n`;
    md += `**Occurrences**: ${s.count}×\n\n`;
    md += `${s.interpretation}\n\n`;
    md += `**Suggestion**: ${s.suggestion}\n\n`;
    md += `---\n\n`;
  }

  return md;
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  console.log(`\n🔍 Workflow Detector`);
  console.log(`  Log: ${LOG_PATH}`);
  console.log(`  N-gram size: ${NGRAM_SIZE}`);
  console.log(`  Min count: ${MIN_COUNT}\n`);

  const entries = readEntries();
  console.log(`  Total audit entries: ${entries.length}`);

  if (entries.length === 0) {
    console.log('  No entries. Ensure hook audit logging is active.\n');
    return;
  }

  const clusters = clusterNgrams(entries);
  console.log(`  Recurring sequences: ${clusters.length}\n`);

  const suggestions = buildSuggestions(clusters);

  if (suggestions.length > 0) {
    for (const s of suggestions.slice(0, 10)) {
      console.log(`  📌 [${s.count}×] ${s.pattern}`);
    }
  } else {
    console.log('  No recurring patterns found.\n');
  }

  if (args.emit) {
    const md = emitMarkdown(suggestions);
    const dir = dirname(OUT_PATH);
    if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
    writeFileSync(OUT_PATH, md, 'utf-8');
    console.log(`\n  Written to ${OUT_PATH}`);
  }

  console.log();
}

main().catch(e => { console.error(e); process.exit(1); });
