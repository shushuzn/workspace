#!/usr/bin/env node
// Move SEEDS_FILE write inside patterns >= 3 threshold
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

const oldBlock = `        if (selfReflectPatterns.length === 0) return;\r\n\r\n        // Append to seeds file\r\n        mkdirSync(dirname(SEEDS_FILE), { recursive: true });\r\n        const header = \`\\n## Self-Audit Seeds (\${now})\\n\`;\r\n        const existing = existsSync(SEEDS_FILE) ? readFileSync(SEEDS_FILE, 'utf-8') : '';\r\n        const entry = existing.endsWith(header) ? selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n' : header + selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n';\r\n        appendFileSync(SEEDS_FILE, entry, 'utf-8');\r\n        // Trigger auto-seed if patterns accumulated >= 3\r\n        if (selfReflectPatterns.length >= 3) {\r\n            try {\r\n                execSync('node "D:/OpenClaw/workspace/.omc/scripts/hook-auto-seed.mjs" --ingest', {\r\n                    stdio: 'ignore',`;

const newBlock = `        if (selfReflectPatterns.length === 0) return;\r\n\r\n        // Only write to SEEDS_FILE and trigger auto-seed if patterns >= 3\r\n        if (selfReflectPatterns.length >= 3) {\r\n            mkdirSync(dirname(SEEDS_FILE), { recursive: true });\r\n            const header = \`\\n## Self-Audit Seeds (\${now})\\n\`;\r\n            const existing = existsSync(SEEDS_FILE) ? readFileSync(SEEDS_FILE, 'utf-8') : '';\r\n            const entry = existing.endsWith(header) ? selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n' : header + selfReflectPatterns.map(p => \`- \${p}\`).join('\\n') + '\\n';\r\n            appendFileSync(SEEDS_FILE, entry, 'utf-8');\r\n            try {\r\n                execSync('node "D:/OpenClaw/workspace/.omc/scripts/hook-auto-seed.mjs" --ingest', {\r\n                    stdio: 'ignore',`;

if (!content.includes(oldBlock)) {
    console.error('[patch] SEEDS_FILE threshold block not found');
    process.exit(1);
}

const next = content.replace(oldBlock, newBlock);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] SEEDS_FILE write now inside patterns>=3 threshold');
