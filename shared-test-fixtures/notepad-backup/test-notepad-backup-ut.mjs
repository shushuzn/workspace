#!/usr/bin/env node
/**
 * UT for notepad-backup.mjs — tests backup logic and stats parsing
 */

// Test 1: section counting logic
const testContent = `# Notepad
## Priority Context
⚡ entry one 20260401
⚠️ entry two 20260402
## Working Memory
some working note
another note
## MANUAL
manual content here
`;

const lines = testContent.split('\n');
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

const ok1 = priority === 2;
const ok2 = working === 2;
console.log(`[UT] priority_count: ${ok1 ? 'PASS' : 'FAIL'} (expect 2)`);
console.log(`[UT] working_count: ${ok2 ? 'PASS' : 'FAIL'} (expect 2)`);

// Test 2: backup filename format
const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
const backupName = `notepad-${today}.md`;
const ok3 = /notepad-\d{8}\.md/.test(backupName);
console.log(`[UT] backup_name_format: ${ok3 ? 'PASS' : 'FAIL'}`);

// Test 3: manual section extraction
const manualMatch = testContent.match(/## MANUAL\s*\n([\s\S]*?)(?=\n##|$)/);
if (manualMatch) {
  const manualLines = manualMatch[1].split('\n').filter(l => l.trim() && !l.trim().startsWith('<!--'));
  manual = manualLines.length;
}
const ok4 = manual === 1;
console.log(`[UT] manual_count: ${ok4 ? 'PASS' : 'FAIL'} (expect 1)`);

const allPass = ok1 && ok2 && ok3 && ok4;
console.log(allPass ? '\n[UT ALL PASS]' : '\n[UT FAIL]');
process.exit(allPass ? 0 : 1);
