#!/usr/bin/env node
/**
 * check-git-dirty.mjs
 * Scans all git repos in workspace for uncommitted changes.
 * Used before dangerous git operations (branch switch, force push, etc.)
 *
 * Usage: node shared/check-git-dirty.mjs [--json]
 */
import { execSync } from 'child_process';
import { join, relative } from 'path';
import { readdirSync } from 'fs';

const __dirname = process.cwd();
const JSON_OUTPUT = process.argv.includes('--json');

/**
 * Check if a directory is a git repo and has dirty status.
 */
function checkGitDirty(dir) {
  try {
    const status = execSync('git status --porcelain', { cwd: dir, encoding: 'utf-8', timeout: 5000 });
    const isDirty = status.trim().length > 0;
    if (isDirty) {
      const lines = status.trim().split('\n');
      return { dir, dirty: true, files: lines.length };
    }
    return null;
  } catch {
    return null; // Not a git repo or git command failed
  }
}

/**
 * Recursively find all git repos under a root directory.
 */
function findGitRepos(root, depth = 0, maxDepth = 2) {
  if (depth > maxDepth) return [];

  const repos = [];
  try {
    const entries = readdirSync(root, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      if (entry.name === 'node_modules' || entry.name === '.git') continue;

      const fullPath = join(root, entry.name);

      // Check if this is a git repo
      try {
        execSync('git rev-parse --git-dir', { cwd: fullPath, timeout: 2000 });
        repos.push(fullPath);
      } catch {
        // Not a repo, descend recursively
        repos.push(...findGitRepos(fullPath, depth + 1, maxDepth));
      }
    }
  } catch {
    // Directory not accessible
  }
  return repos;
}

function main() {
  // Scan workspace root for git repos
  const repos = findGitRepos(__dirname, 0, 2);

  // Check each repo for dirty status
  const dirtyRepos = [];
  for (const repo of repos) {
    const result = checkGitDirty(repo);
    if (result) {
      const relPath = relative(__dirname, repo);
      dirtyRepos.push({ path: relPath, files: result.files });
    }
  }

  if (JSON_OUTPUT) {
    console.log(JSON.stringify({ dirty: dirtyRepos, count: dirtyRepos.length }, null, 2));
  } else {
    if (dirtyRepos.length === 0) {
      console.log('✓ No dirty git repos found');
      process.exit(0);
    } else {
      console.log(`⚠ ${dirtyRepos.length} dirty repo(s) found:`);
      for (const repo of dirtyRepos) {
        console.log(`  ${repo.path} (${repo.files} file(s))`);
      }
      console.log('\nCommit or stash your changes before performing dangerous git operations.');
      process.exit(1);
    }
  }
}

main();
