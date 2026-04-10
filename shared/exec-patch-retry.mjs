#!/usr/bin/env node
// Patch executor.mjs retry to use full causalityChain info
import { readFileSync, writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TARGET = join(__DIR, '..', '80-PROJECTS', 'task-orchestrator', 'src', 'executor.mjs');
let content = readFileSync(TARGET, 'utf8');

// Step 1: Add chainInfo variable after depth declaration
const depthLine = 'const depth = stepDepth.get(stepIdx) ?? 0;';
const chainInfoLine = 'const chainInfo = causalityInfo.get(stepIdx);';
const isRootRelatedLine = "const isRootRelated = chainInfo && (chainInfo.root === stepIdx || (chainInfo.chain && chainInfo.chain.includes(chainInfo.root)));";

if (!content.includes(depthLine)) {
  console.error('[patch] depth line not found');
  process.exit(1);
}
if (!content.includes('causalityInfo.get(stepIdx)')) {
  // Not patched yet, add chainInfo line
  content = content.replace(depthLine, depthLine + '\n                        ' + chainInfoLine + '\n                        ' + isRootRelatedLine);
}

// Step 2: Modify the retry condition
const oldCondition = 'if (depth <= 1 && attempt === 1) {';
const newCondition = 'if ((depth <= 1 || isRootRelated) && attempt === 1) {';

if (!content.includes(oldCondition)) {
  console.error('[patch] retry condition not found');
  process.exit(1);
}

content = content.replace(oldCondition, newCondition);
writeFileSync(TARGET, content, 'utf8');
console.log('[patch] retry now uses causalityChain for root-related decisions');
