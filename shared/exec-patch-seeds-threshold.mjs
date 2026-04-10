#!/usr/bin/env node
// Move SEEDS_FILE write inside patterns >= 3 threshold
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

// Detect "already patched" state: mkdirSync inside the >= 3 block
const patchedPattern = /if\s*\(\s*selfReflectPatterns\.length\s*>=?\s*3\s*\)\s*\{\s*\n?\s*mkdirSync/;
if (patchedPattern.test(content)) {
  console.log('[patch] ALREADY APPLIED');
  process.exit(0);
}

const oldBlock = `        if (selfReflectPatterns.length === 0) return;

        // Append to seeds file
        mkdirSync(dirname(SEEDS_FILE), { recursive: true });
        const header = \`\\n## Self-Audit Seeds (\${now})\\n\`;
        const existing = existsSync(SEEDS_FILE) ? readFileSync(SEEDS_FILE, 'utf-8') : '';
        const entry = existing.endsWith(header) ? selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n' : header + selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n';
        appendFileSync(SEEDS_FILE, entry, 'utf-8');
        // Trigger auto-seed if patterns accumulated >= 3
        if (selfReflectPatterns.length >= 3) {
            try {
                execSync('node "D:/OpenClaw/workspace/.omc/scripts/hook-auto-seed.mjs" --ingest', {
                    stdio: 'ignore',`;

const newBlock = `        if (selfReflectPatterns.length === 0) return;

        // Only write to SEEDS_FILE and trigger auto-seed if patterns >= 3
        if (selfReflectPatterns.length >= 3) {
            mkdirSync(dirname(SEEDS_FILE), { recursive: true });
            const header = \`\\n## Self-Audit Seeds (\${now})\\n\`;
            const existing = existsSync(SEEDS_FILE) ? readFileSync(SEEDS_FILE, 'utf-8') : '';
            const entry = existing.endsWith(header) ? selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n' : header + selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n';
            appendFileSync(SEEDS_FILE, entry, 'utf-8');
            try {
                execSync('node "D:/OpenClaw/workspace/.omc/scripts/hook-auto-seed.mjs" --ingest', {
                    stdio: 'ignore',`;

if (!content.includes(oldBlock)) {
    console.error('[patch] SEEDS_FILE threshold block not found');
    process.exit(1);
}

const next = content.replace(oldBlock, newBlock);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] SEEDS_FILE write now inside patterns>=3 threshold');
