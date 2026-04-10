#!/usr/bin/env node
/**
 * approach-drift-detector.mjs
 * Detect drift between seed approach and actual implementation
 * Usage: node approach-drift-detector.mjs "<seed_approach>" "<actual_implementation>"
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const IDEAS_FILE = join(__DIR, '..', '.omc', 'innovation', 'ideas.md');

function extractStepKeywords(approach) {
  const steps = approach.split('\n').filter(l => l.match(/^\d+\./));
  return steps.map(s => {
    // Extract key actions/verbs
    const verbs = ['Read', 'Edit', 'Write', 'node', 'python', 'bash', 'mkdir', 'grep', 'sed'];
    const found = verbs.filter(v => s.includes(v));
    return found.length > 0 ? found : ['unknown'];
  }).flat();
}

function compareApproachVsImpl(approach, impl) {
  const drift = [];
  const approachKeywords = extractStepKeywords(approach);

  // Check if implementation matches approach keywords
  for (const kw of approachKeywords) {
    if (!impl.includes(kw) && kw !== 'unknown') {
      drift.push(`Approach mentions "${kw}" but implementation doesn't use it`);
    }
  }

  return drift;
}

const args = process.argv.slice(2);
if (args.length < 2) {
  console.log('Usage: node approach-drift-detector.mjs "<approach>" "<implementation>"');
  process.exit(1);
}

const [approach, impl] = args;

console.log('=== Approach Drift Detector ===\n');

const drifts = compareApproachVsImpl(approach, impl);

if (drifts.length === 0) {
  console.log('✅ No drift detected - implementation matches approach');
} else {
  console.log('⚠️ Drift detected:');
  for (const d of drifts) {
    console.log(`  - ${d}`);
  }
}

console.log(`\n=== Result: ${drifts.length === 0 ? 'PASS' : 'DRIFT'} ===`);
process.exit(drifts.length === 0 ? 0 : 1);
