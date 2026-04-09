#!/usr/bin/env node
/**
 * Integration tests for check-deps-health.mjs
 * Verifies script runs end-to-end and produces expected output
 */
import { execSync } from 'child_process';

let output;
try {
  output = execSync('node shared/check-deps-health.mjs', { cwd: '/d/OpenClaw/workspace', encoding: 'utf8', timeout: 15000 });
} catch (e) {
  output = (e.stdout || '') + (e.stderr || '');
}

const hasHeader = output.includes('Dependency Health Check');
const hasSummary = output.includes('healthy') && output.includes('missing');
const hasProjectList = output.includes('✓') || output.includes('✗');
const noCrash = output.includes('Summary:');

console.log(`[IT] Header present: ${hasHeader ? 'PASS' : 'FAIL'}`);
console.log(`[IT] Summary line: ${hasSummary ? 'PASS' : 'FAIL'}`);
console.log(`[IT] Project list: ${hasProjectList ? 'PASS' : 'FAIL'}`);
console.log(`[IT] No crash: ${noCrash ? 'PASS' : 'FAIL'}`);

const allPass = hasHeader && hasSummary && hasProjectList && noCrash;
console.log(allPass ? '\n[IT ALL PASS]' : '\n[IT FAIL]');
process.exit(allPass ? 0 : 1);
