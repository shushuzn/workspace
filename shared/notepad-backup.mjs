#!/usr/bin/env node
/**
 * notepad-backup.mjs
 * Backup .omc/notepad.md and generate activity statistics
 */
import { existsSync, mkdirSync, readFileSync, copyFileSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const NOTEPAD = join(__DIR, '..', '.omc', 'notepad.md');
const BACKUP_DIR = join(__DIR, '..', '.omc', 'backups');
const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');

if (!existsSync(NOTEPAD)) {
  console.error('[notepad-backup] notepad.md not found');
  process.exit(1);
}

// Ensure backup dir exists
mkdirSync(BACKUP_DIR, { recursive: true });

// Backup
const backupPath = join(BACKUP_DIR, `notepad-${today}.md`);
copyFileSync(NOTEPAD, backupPath);
console.log(`[notepad-backup] Backed up to backups/notepad-${today}.md`);

// Stats
const content = readFileSync(NOTEPAD, 'utf8');
const lines = content.split('\n');

let priority = 0, working = 0, manual = 0;
let inPriority = false, inWorking = false;

for (const line of lines) {
  const trimmed = line.trim();
  if (trimmed === '## Priority Context') { inPriority = true; inWorking = false; continue; }
  if (trimmed === '## Working Memory') { inWorking = true; inPriority = false; continue; }
  if (trimmed.startsWith('## ')) { inPriority = false; inWorking = false; continue; }

  if (inPriority && (trimmed.startsWith('⚡') || trimmed.startsWith('⚠️'))) priority++;
  if (inWorking && trimmed.length > 0 && !trimmed.startsWith('<!--')) working++;
}

const manualMatch = content.match(/## MANUAL\s*\n([\s\S]*?)(?=\n##|$)/);
if (manualMatch) {
  const manualLines = manualMatch[1].split('\n').filter(l => l.trim() && !l.trim().startsWith('<!--'));
  manual = manualLines.length;
}

console.log('\n╔══════════════════════════════════════╗');
console.log('║  Notepad Activity Report             ║');
console.log('╚══════════════════════════════════════╝');
console.log(`  Priority Context entries: ${priority}`);
console.log(`  Working Memory entries:  ${working}`);
console.log(`  Manual entries:          ${manual}`);
console.log(`  Total:                  ${priority + working + manual}`);
console.log(`  Date:                   ${today}`);
console.log('');

// List backups
const backups = readdirSync(BACKUP_DIR).filter(f => f.startsWith('notepad-')).sort().reverse();
console.log(`  Backups: ${backups.length} (latest: ${backups[0] || 'none'})`);
console.log('');
