#!/usr/bin/env node
/** Export annealing data to CSV */
import { readFileSync } from 'fs';

if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log('Usage: node export-annealing.mjs [log_file] [output_file]');
  console.log('  log_file     Annealing log file (default: annealing.log)');
  console.log('  output_file  CSV output file (default: annealing.csv)');
  process.exit(0);
}

const log = process.argv[2] || 'annealing.log';
const out = process.argv[3] || 'annealing.csv';
console.log('Export', log, 'to', out);
