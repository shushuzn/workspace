#!/usr/bin/env node
/**
 * gate13-prescan.mjs
 * Pre-scan project paths referenced in seeds before execution
 * Usage: node gate13-prescan.mjs <seed_approach_text>
 */
import { existsSync } from 'fs';
import { join, resolve } from 'path';

function extractPaths(text) {
  const paths = [];
  // Match node/python script paths
  const scriptMatch = text.matchAll(/(?:node|python|bash|sh)\s+(\S+\.(?:mjs|js|py))/gi);
  for (const m of scriptMatch) {
    paths.push(m[1]);
  }
  // Match file paths in ideas.md format
  const fileMatch = text.matchAll(/([A-Z]:[\\\/][^\s:]+)/gi);
  for (const m of fileMatch) {
    paths.push(m[1]);
  }
  return [...new Set(paths)];
}

function checkPath(path) {
  // Handle relative paths
  const resolved = resolve(process.cwd(), path);
  return existsSync(resolved) || existsSync(path);
}

const args = process.argv.slice(2);
if (args.length === 0) {
  console.log('Usage: node gate13-prescan.mjs "<approach text>"');
  process.exit(1);
}

const text = args.join(' ');
const paths = extractPaths(text);

console.log('=== Gate13 Path Pre-Scan ===\n');
console.log(`Total paths found: ${paths.length}\n`);

let passCount = 0;
let failCount = 0;

for (const path of paths) {
  const exists = checkPath(path);
  const status = exists ? 'EXISTS' : 'MISSING';
  console.log(`[${status}] ${path}`);
  if (!exists) failCount++;
  else passCount++;
}

console.log(`\n=== Summary ===`);
console.log(`Exists: ${passCount}`);
console.log(`Missing: ${failCount}`);

process.exit(failCount > 0 ? 1 : 0);
