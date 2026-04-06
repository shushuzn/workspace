/**
 * wiki-git-backup.mjs — Wikipedia articles Git auto-commit
 *
 * Usage:
 *   node wiki-git-backup.mjs [--message "msg"]  # commit once
 *   node wiki-git-backup.mjs --watch           # watch mode (cron-style)
 */

import { execSync } from 'child_process';
import { readdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const ARTICLES_DIR = join(__DIR, 'articles');
const WIKI_DIR = __DIR;

const isWatch = process.argv.includes('--watch');
const customMsg = (() => {
  const i = process.argv.indexOf('--message');
  return i > -1 ? process.argv[i + 1] : null;
})();

function getArticleCount() {
  let count = 0;
  const scan = (d) => {
    for (const e of readdirSync(d, { withFileTypes: true })) {
      if (e.isDirectory()) scan(join(d, e.name));
      else if (e.name.endsWith('.md')) count++;
    }
  };
  if (existsSync(ARTICLES_DIR)) scan(ARTICLES_DIR);
  return count;
}

function runBackup() {
  const date = new Date().toISOString().slice(0, 19).replace('T', ' ');
  const count = getArticleCount();
  const msg = customMsg || `wiki backup: ${date} | ${count} articles`;

  try {
    execSync('git add articles/', { cwd: WIKI_DIR });
    const status = execSync('git status --porcelain', { cwd: WIKI_DIR }).toString().trim();
    if (!status) {
      console.log(`[wiki-backup] No changes — nothing to commit`);
      return false;
    }
    execSync(`git commit -m "${msg}"`, { cwd: WIKI_DIR });
    console.log(`[wiki-backup] Committed: ${count} articles`);
    return true;
  } catch (e) {
    if (e.message.includes('no git')) {
      console.error('[wiki-backup] Not a git repository — skip');
    } else {
      console.error('[wiki-backup] Error:', e.message);
    }
    return false;
  }
}

if (isWatch) {
  // Watch mode: check every 6 hours
  const INTERVAL = 6 * 60 * 60 * 1000;
  console.log(`[wiki-backup] Watch mode — backing up every 6 hours`);
  runBackup();
  setInterval(runBackup, INTERVAL);
} else {
  runBackup();
}
