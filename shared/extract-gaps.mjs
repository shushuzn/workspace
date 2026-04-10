#!/usr/bin/env node
/**
 * shared/extract-gaps.mjs
 * 从已shipped seed的reason字段提取缺失环节，写入project-gaps.json
 * Usage: node shared/extract-gaps.mjs
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_PATH = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');
const GAPS_FILE = join(__DIR, '..', '.omc', 'state', 'project-gaps', 'project-gaps.json');

const content = readFileSync(IDEAS_PATH, 'utf-8');
const lines = content.split('\n');

// Parse shipped seeds
const shipped = [];
for (const line of lines) {
  const header = line.match(/^- \[(\d{8})\] seed \[([^\]]+)\] \[score:([^\]]+)\] \[f:(\d+)\]/);
  if (!header) continue;
  const bodyMatch = line.match(/\| shipped:(\d{8})/);
  if (!bodyMatch) continue;

  const reasonMatch = line.match(/\| reason:\s*(.+?)(?:\s*\| approach:|$)/s);
  if (!reasonMatch) continue;

  const focusMatch = line.match(/\[focus:([^\]]+)\]/);
  const angleMatch = line.match(/\[angle:([^\]]+)\]/);
  const reason = reasonMatch[1].trim();

  // Extract missing part from "缺失环节：XXX"
  const missingMatch = reason.match(/缺失环节[：:]\s*(.+?)(?:[；;]|$)/);
  if (missingMatch) {
    shipped.push({
      focus: focusMatch ? focusMatch[1] : 'ws-level',
      angle: angleMatch ? angleMatch[1] : '',
      missing: missingMatch[1].trim(),
      reason
    });
  }
}

// Build gaps map
const gaps = {};
for (const s of shipped) {
  const key = s.focus;
  if (!gaps[key]) gaps[key] = [];
  // Dedupe by missing text
  if (!gaps[key].includes(s.missing)) {
    gaps[key].push(s.missing);
  }
}

// Merge with existing
let existing = { meta: {}, projects: {} };
if (existsSync(GAPS_FILE)) {
  try { existing = JSON.parse(readFileSync(GAPS_FILE, 'utf-8')); } catch {}
}

// Merge
for (const [proj, missingList] of Object.entries(gaps)) {
  if (!existing.projects[proj]) existing.projects[proj] = [];
  for (const m of missingList) {
    if (!existing.projects[proj].includes(m)) existing.projects[proj].push(m);
  }
}

writeFileSync(GAPS_FILE, JSON.stringify(existing, null, 2), 'utf-8');
const total = Object.values(existing.projects).reduce((s, l) => s + l.length, 0);
console.log(`[gaps] Extracted gaps for ${Object.keys(gaps).length} projects, ${total} total gaps written to .omc/state/project-gaps/project-gaps.json`);

