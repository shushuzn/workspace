/**
 * sync-memory-projects.js
 * Syncs 80-PROJECTS/ directories with MEMORY.md Active Projects table.
 * Adds missing directories as new entries (no deletion).
 * Run: node scripts/sync-memory-projects.js
 */

import { readFileSync, writeFileSync } from 'fs';
import { readdirSync } from 'fs';
import { join } from 'path';

const WORKSPACE = process.cwd();
const PROJECTS_DIR = join(WORKSPACE, '80-PROJECTS');
const MEMORY_PATH = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory/MEMORY.md';

function getTechStack(projectPath) {
  try {
    const pkgPath = join(projectPath, 'package.json');
    const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
    return pkg.description || 'N/A';
  } catch {
    try {
      const files = readdirSync(projectPath);
      if (files.includes('pyproject.toml') || files.includes('requirements.txt')) return 'Python';
      if (files.includes('go.mod')) return 'Go';
      if (files.includes('Cargo.toml')) return 'Rust';
      if (files.includes('README.md')) {
        const readme = readFileSync(join(projectPath, 'README.md'), 'utf8').slice(0, 200);
        if (readme.includes('React')) return 'React';
        if (readme.includes('Svelte')) return 'Svelte';
        if (readme.includes('TypeScript')) return 'TypeScript';
        if (readme.includes('Python')) return 'Python';
      }
    } catch {}
    return 'N/A';
  }
}

function getToday() {
  return new Date().toISOString().slice(0, 10);
}

const actual = readdirSync(PROJECTS_DIR).filter(n => !n.startsWith('.'));

const memory = readFileSync(MEMORY_PATH, 'utf8');
const lines = memory.split('\n');

// Find header line index and first separator
let headerIdx = -1;
let sepIdx = -1;
for (let i = 0; i < lines.length; i++) {
  if (lines[i].startsWith('| Project |')) headerIdx = i;
}
for (let i = headerIdx; i < lines.length; i++) {
  if (lines[i].match(/\|[-]+\|/)) { sepIdx = i; break; }
}

if (headerIdx === -1 || sepIdx === -1) {
  console.error('Cannot find table header/separator in MEMORY.md');
  process.exit(1);
}

// Extract existing project names from path column
const existingProjects = new Set();
for (let i = sepIdx + 1; i < lines.length; i++) {
  const line = lines[i];
  const m = line.match(/\|\s*([^|]+?)\s*\|\s*80-PROJECTS\//);
  if (m) existingProjects.add(m[1].trim());
}

// Find missing
const today = getToday();
const missing = actual.filter(d =>
  !existingProjects.has(d) &&
  !d.includes('-ARCHIVED') &&
  !d.includes('50-ton')
);

if (missing.length === 0) {
  console.log('No new projects to add.');
  process.exit(0);
}

// Build new rows
const newRows = missing.map(name => {
  const tech = getTechStack(join(PROJECTS_DIR, name));
  return `| ${name} | 80-PROJECTS/${name} | ${tech} | ${today} | 增长中 | |`;
});

// Insert after sepIdx
const newLines = [...lines.slice(0, sepIdx + 1), ...newRows, ...lines.slice(sepIdx + 1)];
writeFileSync(MEMORY_PATH, newLines.join('\n'), 'utf8');

console.log(`Added ${missing.length} project(s): ${missing.join(', ')}`);
