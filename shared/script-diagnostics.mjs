#!/usr/bin/env node
/**
 * script-diagnostics.mjs
 * Workspace script health diagnostics - scans all .js/.mjs files for issues
 */
import { readdirSync, readFileSync, statSync } from 'fs';
import { join, extname } from 'path';

const WORKSPACE = 'D:/OpenClaw/workspace';
const IGNORE_DIRS = ['node_modules', 'dist', '.git', 'cache', '__pycache__'];

function scan(dir, files = []) {
  try {
    const entries = readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (IGNORE_DIRS.includes(entry.name)) continue;
      const full = join(dir, entry.name);
      if (entry.isDirectory()) {
        scan(full, files);
      } else if (extname(entry.name) === '.js' || extname(entry.name) === '.mjs') {
        files.push(full);
      }
    }
  } catch (e) {
    // skip inaccessible dirs
  }
  return files;
}

function checkFile(filepath) {
  const issues = [];
  try {
    const content = readFileSync(filepath, 'utf8');
    // Check for syntax-like issues
    if (content.includes('require(') && !filepath.includes('node_modules')) {
      const pkgMatch = content.match(/require\(['"]([@\w/-]+)['"]\)/g);
      if (pkgMatch) {
        issues.push({ type: 'require', packages: pkgMatch.length });
      }
    }
    // Basic syntax check via eval-like pattern detection
    if (content.includes('eval(') || content.includes('new Function')) {
      issues.push({ type: 'eval-usage', count: 1 });
    }
  } catch (e) {
    issues.push({ type: 'read-error', msg: e.message });
  }
  return issues;
}

const files = scan(WORKSPACE);
console.log(`[script-diagnostics] Scanning ${files.length} files...`);
const allIssues = [];
for (const f of files) {
  const issues = checkFile(f);
  if (issues.length > 0) {
    allIssues.push({ file: f, issues });
  }
}

if (allIssues.length === 0) {
  console.log('[script-diagnostics] All scripts healthy.');
} else {
  console.log(`[script-diagnostics] Found ${allIssues.length} files with issues:`);
  for (const { file, issues } of allIssues) {
    console.log(`  ${file}`);
    for (const issue of issues) {
      console.log(`    - ${issue.type}: ${JSON.stringify(issue.packages || issue.msg || '')}`);
    }
  }
}
