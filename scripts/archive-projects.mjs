/**
 * archive-projects.mjs — Archives inactive projects to ARCHIVED/
 * Run: node scripts/archive-projects.mjs [--dry-run]
 */

import { readdirSync, existsSync, renameSync, mkdirSync, readFileSync, writeFileSync } from 'fs';
import { resolve, join } from 'path';
import { execSync } from 'child_process';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const MEMORY = 'C:/Users/adm/.claude/projects/D--OpenClaw-workspace/memory/MEMORY.md';
const DRY = process.argv.includes('--dry-run');

const TO_ARCHIVE = ['ai-scientist', 'idle-empire-cli', 'terminal-chat'];

function exists(p) { try { return existsSync(p); } catch { return false; } }

let archived = 0;
for (const name of TO_ARCHIVE) {
  const src = join(ROOT, name);
  const dst = join(ROOT, 'ARCHIVED', name);

  if (!exists(src)) { console.log(`  - ${name}: not found`); continue; }
  if (exists(dst)) { console.log(`  - ${name}: already archived`); continue; }

  if (!DRY) {
    mkdirSync(join(ROOT, 'ARCHIVED'), { recursive: true });
    // Try git mv first (for real repos), fall back to fs.rename (empty dirs)
    try {
      execSync(`git mv "${src}" "${dst}"`, { stdio: 'ignore' });
    } catch {
      renameSync(src, dst);
    }
    // Update MEMORY.md
    try {
      let content = readFileSync(MEMORY, 'utf8');
      const escaped = name.replace(/-/g, '\u2011'); // non-breaking hyphen
      content = content.replace(
        new RegExp(`^(\\|[^\\|]*\\|\\s*)${escaped}(\\|[^\\|]*\\|)`, 'm'),
        (m, before, after) => before + name + after
      );
      // Simpler: just update the table row status
      content = content.replace(
        new RegExp(`(${name})`, 'g'),
        (match) => match // placeholder for sed-like replacement
      );
      writeFileSync(MEMORY, content, 'utf8');
    } catch (e) { console.log(`  ! MEMORY.md update failed: ${e.message}`); }
  }
  console.log(`  + ${name} → ARCHIVED/${name}`);
  archived++;
}

console.log(`\n  ${archived} project(s) archived\n`);
