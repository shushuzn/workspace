#!/usr/bin/env node
// Patch recordAuditLog to write run header and not duplicate prompt per entry
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

// Step 1: Remove prompt from per-step entry
const oldEntryPrompt = "prompt: prompt ?? '',";
const newEntryPrompt = "";
if (content.includes(oldEntryPrompt)) {
  content = content.replace(oldEntryPrompt, newEntryPrompt);
}

// Step 2: Add run header before the step loop
const marker = '// Write one AuditLogEntry per step';
const headerEntry = `// Write run header entry (prompt stored once)
            appendFileSync(logPath, JSON.stringify({
                runId,
                seq: -1,
                timestamp,
                type: 'run-header',
                prompt: prompt ?? '',
                stepCount: steps.length
            }) + '\\n', 'utf-8');
`;

if (!content.includes(marker)) {
  console.error('[patch] audit marker not found');
  process.exit(1);
}

const next = content.replace(marker, headerEntry + '\n            ' + marker);
writeFileSync(TARGET, next, 'utf8');
console.log('[patch] recordAuditLog now writes run header once and removes prompt bloat');
