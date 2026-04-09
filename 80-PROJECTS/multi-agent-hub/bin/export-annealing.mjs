#!/usr/bin/env node
/** Export annealing data to CSV */
import { readFileSync } from 'fs';

const log = process.argv[2] || 'annealing.log';
const out = process.argv[3] || 'annealing.csv';
console.log('Export', log, 'to', out);
