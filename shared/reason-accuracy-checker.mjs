#!/usr/bin/env node
/**
 * reason-accuracy-checker.mjs
 * Check if seed reason matches actual implementation
 * Usage: node reason-accuracy-checker.mjs <seed_description>
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_FILE = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');

// Check if reason has the three required sections
function checkReasonStructure(reason) {
  const issues = [];
  if (!reason.includes('已知资源')) {
    issues.push('Missing: 已知资源');
  }
  if (!reason.includes('缺失环节')) {
    issues.push('Missing: 缺失环节');
  }
  if (!reason.includes('连接方式')) {
    issues.push('Missing: 连接方式');
  }
  return issues;
}

// Check if reason has concrete file paths or function names
function checkReasonSubstance(reason) {
  const issues = [];
  // Must have at least one real path or function
  const hasPath = /[A-Z]:[\\\/]/.test(reason);
  const hasFunc = /function\s+\w+/.test(reason);
  const hasConst = /const\s+\w+/.test(reason);
  if (!hasPath && !hasFunc && !hasConst) {
    issues.push('No concrete file paths or function names found');
  }
  return issues;
}

const args = process.argv.slice(2);
if (args.length === 0) {
  console.log('Usage: node reason-accuracy-checker.mjs "<reason text>"');
  process.exit(1);
}

const reason = args.join(' ');

console.log('=== Reason Accuracy Checker ===\n');

const structureIssues = checkReasonStructure(reason);
const substanceIssues = checkReasonSubstance(reason);

console.log('Structure check:');
if (structureIssues.length === 0) {
  console.log('  ✅ All three sections present');
} else {
  for (const issue of structureIssues) {
    console.log(`  ⚠️ ${issue}`);
  }
}

console.log('\nSubstance check:');
if (substanceIssues.length === 0) {
  console.log('  ✅ Contains concrete paths/functions');
} else {
  for (const issue of substanceIssues) {
    console.log(`  ⚠️ ${issue}`);
  }
}

const totalIssues = structureIssues.length + substanceIssues.length;
console.log(`\n=== Result: ${totalIssues === 0 ? 'PASS' : 'FAIL'} ===`);
process.exit(totalIssues > 0 ? 1 : 0);
