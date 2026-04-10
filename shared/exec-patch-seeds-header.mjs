#!/usr/bin/env node
// Fix selfAuditLog SEEDS_FILE entry: header was defined but never used in entry
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

const marker = `        const header = \`\\n## Self-Audit Seeds (\${now})\\n\`;`;
const existing = `        const existing = existsSync(SEEDS_FILE) ? readFileSync(SEEDS_FILE, 'utf-8') : '';`;
const oldLine = `        const entry = header + selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n';`;
const newLine = `        const entry = existing.endsWith(header) ? selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n' : header + selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n';`;

if (!content.includes(oldLine)) {
    console.error('[patch] SEEDS_FILE entry line not found');
    process.exit(1);
}

const next = content.replace(oldLine, newLine);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] selfAuditLog SEEDS_FILE now avoids duplicate header on re-run');
