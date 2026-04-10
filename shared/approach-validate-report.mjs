#!/usr/bin/env node
/**
 * approach-validate-report.mjs
 * Validates approach steps and generates a report
 * Usage: node approach-validate-report.mjs "1. node script.mjs\n2. bash cmd"
 */
import { existsSync } from 'fs';

const EXECUTABLE_PREFIXES = ['python ', 'node ', 'bash ', 'sh ', 'cd ', 'mkdir ', '//', '#', '/'];

const FORBIDDEN_PATTERNS = [
  { pattern: /node -[epc]/, name: 'node -e/-p/-c inline' },
  { pattern: /python -c ".*\n/, name: 'python -c multiline' },
  { pattern: /bash.*<<\s*EOF/, name: 'heredoc' },
];

function parseApproach(text) {
  const lines = text.split('\n').filter(l => l.trim());
  const steps = [];
  for (const line of lines) {
    const m = line.match(/^\d+\.\s+(.+)/);
    if (m) steps.push(m[1].trim());
  }
  return steps;
}

function validateStep(step) {
  const issues = [];

  // Check executable prefix
  const hasValidPrefix = EXECUTABLE_PREFIXES.some(p => step.startsWith(p));
  if (!hasValidPrefix) {
    issues.push(`No valid executable prefix`);
  }

  // Check forbidden patterns
  for (const { pattern, name } of FORBIDDEN_PATTERNS) {
    if (pattern.test(step)) {
      issues.push(`Forbidden pattern: ${name}`);
    }
  }

  // Check for script paths
  const nodeMatch = step.match(/node\s+(\S+\.(?:mjs|js))/);
  if (nodeMatch) {
    const scriptPath = nodeMatch[1];
    if (!existsSync(scriptPath)) {
      issues.push(`Script not found: ${scriptPath}`);
    }
  }

  return issues;
}

const args = process.argv.slice(2);
if (args.length === 0) {
  console.log('Usage: node approach-validate-report.mjs "1. node script.mjs" "2. bash cmd"');
  console.log('  Each argument is a step - multiple steps passed as separate args');
  process.exit(1);
}

// If single arg with newlines, parse as multi-line
const approach = args[0].includes('\n') ? args[0] : args.join(' ');
const steps = parseApproach(approach);

console.log('=== Approach Validation Report ===\n');
console.log(`Total steps: ${steps.length}\n`);

let passCount = 0;
let failCount = 0;

for (let i = 0; i < steps.length; i++) {
  const issues = validateStep(steps[i]);
  const status = issues.length === 0 ? 'PASS' : 'FAIL';
  console.log(`Step ${i + 1}: ${status}`);
  console.log(`  ${steps[i]}`);
  if (issues.length > 0) {
    for (const issue of issues) {
      console.log(`  ⚠️ ${issue}`);
    }
    failCount++;
  } else {
    passCount++;
  }
  console.log();
}

console.log('=== Summary ===');
console.log(`Pass: ${passCount}/${steps.length}`);
console.log(`Fail: ${failCount}/${steps.length}`);

process.exit(failCount > 0 ? 1 : 0);
