#!/usr/bin/env node
/**
 * Agent Workflow CLI
 * Parses AGENT-WORKFLOWS.md YAML templates and executes via state machine.
 * Supports --dry-run preview and --execute for real runs.
 */
import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ── CLI ──────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const dryRun = args.includes('--dry-run');
const execute = args.includes('--execute');
const listWorkflows = args.includes('--list');
const positional = args.filter(a => !a.startsWith('--'));
const [action, ...rest] = positional;

// ── YAML parser ─────────────────────────────────────────────────────────────
function parseYaml(raw) {
  const docs = [];
  let inCodeBlock = false, buf = [];
  for (const line of raw.split('\n')) {
    if (line.trim() === '```yaml' || line.trim() === '```') {
      inCodeBlock = !inCodeBlock && line.trim() === '```yaml';
      if (!inCodeBlock && buf.length) { docs.push(buf.join('\n')); buf = []; }
    } else if (inCodeBlock) buf.push(line);
  }
  if (buf.length) docs.push(buf.join('\n'));
  return docs.map(d => parseDoc(d));
}

function parseValue(v) {
  if (v.startsWith('[') && v.endsWith(']')) return v.slice(1,-1).split(',').map(s=>s.trim());
  if (!isNaN(v) && v !== '') return Number(v);
  if (v === 'true') return true;
  if (v === 'false') return false;
  return v.replace(/^["']|["']$/g, '');
}

function parseDoc(src) {
  const result = {};
  const rawLines = src.split('\n').filter(l => {
    const t = l.trim();
    return t !== '' && !t.startsWith('#');
  });

  // Split into sections by top-level keys (indent=0, no leading dash)
  const sections = [];
  let current = null;
  for (const raw of rawLines) {
    const indent = raw.search(/\S/);
    const trimmed = raw.trim();
    if (indent === 0 && !trimmed.startsWith('-') && trimmed.includes(':')) {
      current = { key: trimmed.split(':')[0].trim(), lines: [] };
      sections.push(current);
    } else if (current !== null) {
      current.lines.push({ indent, raw: trimmed });
    }
  }

  for (const section of sections) {
    // Find the value of the top-level key in original source
    const topRaw = rawLines.find(l => {
      const t = l.trim();
      return t.startsWith(section.key + ':');
    });
    const colonIdx = topRaw.trim().indexOf(':');
    const topVal = topRaw.trim().slice(colonIdx + 1).trim();

    if (topVal !== '') {
      // Scalar value
      result[section.key] = parseValue(topVal);
      continue;
    }

    // No value after colon → child content
    if (section.lines.length === 0) {
      result[section.key] = [];
      continue;
    }

    // Determine container type from first non-blank child
    const firstIndent = section.lines[0].indent;
    const firstContent = section.lines[0].raw;

    if (firstContent.startsWith('-')) {
      // List container
      result[section.key] = parseList(section.lines, firstIndent);
    } else {
      // Object container
      result[section.key] = parseObject(section.lines);
    }
  }

  return result;
}

function parseObject(lines) {
  const obj = {};
  for (const { raw } of lines) {
    const colonIdx = raw.indexOf(':');
    if (colonIdx < 0) continue;
    const key = raw.slice(0, colonIdx).trim();
    const val = raw.slice(colonIdx + 1).trim();
    if (val === '') obj[key] = {};
    else obj[key] = parseValue(val);
  }
  return obj;
}

function parseList(lines, baseIndent) {
  const items = [];
  let i = 0;

  while (i < lines.length) {
    const { indent, raw } = lines[i];

    // Non-list-item line: belongs to the last item
    if (!raw.startsWith('-')) {
      if (items.length === 0) { i++; continue; }
      const last = items[items.length - 1];
      if (typeof last !== 'object' || last === null) { i++; continue; }
      const colonIdx = raw.indexOf(':');
      if (colonIdx < 0) { i++; continue; }
      const key = raw.slice(0, colonIdx).trim();
      const val = raw.slice(colonIdx + 1).trim();
      // If last item has no such key yet, add it
      if (!(key in last)) {
        last[key] = val === '' ? {} : parseValue(val);
      }
      i++; continue;
    }

    // List item
    const content = raw.slice(1).trim(); // remove leading '-'

    if (!content.includes(':')) {
      items.push(parseValue(content));
      i++; continue;
    }

    const colonIdx = content.indexOf(':');
    const key = content.slice(0, colonIdx).trim();
    const val = content.slice(colonIdx + 1).trim();

    if (val !== '') {
      // "  - agent: foo"
      items.push({ [key]: parseValue(val) });
      i++; continue;
    }

    // val === '': "  - merge:" or "  - agent:"
    // Collect lines nested under this item (indent > baseIndent, not starting with '-')
    i++;
    const nested = [];
    while (i < lines.length && lines[i].indent > baseIndent) {
      nested.push(lines[i]);
      i++;
    }

    if (nested.length === 0) {
      items.push({ [key]: {} });
      continue;
    }

    // nested[0] determines whether this is a list or object
    if (nested[0].raw.startsWith('-')) {
      // List-valued: "  - key:" with list children
      items.push({ [key]: parseList(nested, nested[0].indent) });
    } else {
      // Object-valued: "  - key:" with key:value children
      items.push({ [key]: parseObject(nested) });
    }
  }

  return items;
}

// ── State Machine ──────────────────────────────────────────────────────────────
const STATE = { IDLE:'IDLE', RUNNING:'RUNNING', DONE:'DONE', ERROR:'ERROR' };

class WorkflowEngine {
  constructor(name, steps) {
    this.name = name; this.steps = steps || [];
    this.state = STATE.IDLE; this.currentStep = 0;
    this.results = []; this.errors = [];
  }

  async execute(ctx = {}) {
    this.state = STATE.RUNNING;
    console.log(`\n▶ Starting workflow: ${this.name} (${this.steps.length} steps)\n`);
    for (let i = 0; i < this.steps.length; i++) {
      this.currentStep = i;
      const step = this.steps[i];
      if (step.merge) {
        const { files, output } = step.merge;
        console.log(`  📦 Step ${i+1}/${this.steps.length}: MERGE → ${output}`);
        if (!dryRun) {
          const { writeFileSync, readFileSync: rf } = await import('fs');
          const content = files.map(f => { try { return rf(f,'utf-8'); } catch { return ''; } }).join('\n\n---\n\n');
          writeFileSync(output, content, 'utf-8');
          this.results.push({ step:i, type:'merge', output, status:'ok' });
        }
        continue;
      }
      const { agent, input, output } = step;
      const inputResolved = typeof input === 'string'
        ? input.replace(/\{([^}]+)\}/g, (_,k) => ctx[k] ?? `{${k}}`)
        : input;
      console.log(`  Step ${i+1}/${this.steps.length}: ${agent} | input: ${inputResolved} | output: ${output}`);
      if (!dryRun) {
        try {
          const result = await this.runAgent(agent, inputResolved, output);
          this.results.push({ step:i, agent, status:'ok', ...result });
        } catch (err) {
          this.errors.push({ step:i, agent, error:err.message });
          this.state = STATE.ERROR;
          console.error(`  ❌ Step ${i+1} failed: ${err.message}`);
          break;
        }
      }
    }
    this.state = this.errors.length === 0 ? STATE.DONE : STATE.ERROR;
    console.log(`\n${this.state===STATE.DONE?'✅':'❌'} Workflow ${this.name} finished: ${this.state}`);
    return { state: this.state, results: this.results, errors: this.errors };
  }

  async runAgent(agent, input, output) {
    // TODO: wire to actual agent (opencli / MCP / CLI)
    return { output };
  }

  preview() {
    console.log(`\n🔍 DRY RUN — ${this.name} (${this.steps.length} steps)\n`);
    for (let i = 0; i < this.steps.length; i++) {
      const s = this.steps[i];
      if (s.merge) console.log(`  ${i+1}. MERGE → ${s.merge.output}`);
      else console.log(`  ${i+1}. ${s.agent} | input: ${JSON.stringify(s.input)} | output: ${s.output}`);
    }
    console.log('\nNo actual execution occurred.\n');
  }
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const workflowsPath = resolve(__dirname, 'AGENT-WORKFLOWS.md');
  let yamlDocs;
  try {
    yamlDocs = parseYaml(readFileSync(workflowsPath, 'utf-8'));
  } catch (err) {
    console.error(`Failed to read ${workflowsPath}: ${err.message}`); process.exit(1);
  }
  const workflows = yamlDocs.filter(d => d.name && d.steps);

  if (listWorkflows) {
    console.log('\n📋 Available workflows:\n');
    workflows.forEach((w,i) => console.log(`  ${i+1}. ${w.name} (${w.steps.length} steps)`));
    console.log(); return;
  }
  if (!action) {
    console.error('Usage:\n  node run-workflow.mjs --list\n  node run-workflow.mjs --dry-run <name>\n  node run-workflow.mjs --execute <name> [k=v...]\n\nWorkflows:', workflows.map(w=>w.name).join(', '));
    process.exit(1);
  }
  const wf = workflows.find(w => w.name === action);
  if (!wf) { console.error(`Workflow "${action}" not found.`); process.exit(1); }

  const engine = new WorkflowEngine(wf.name, wf.steps);
  if (dryRun) { engine.preview(); return; }
  if (!execute) { console.error('Use --dry-run to preview or --execute to run.'); process.exit(1); }

  const ctx = {};
  for (const arg of rest) { const [k,v] = arg.split('='); if (k) ctx[k.trim()] = v?.trim(); }
  await engine.execute(ctx);
}

main().catch(err => { console.error(err); process.exit(1); });
