#!/usr/bin/env node
/** Export annealing process to CSV */
import { writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const INDEX = join(__DIR, '..', 'index.js');
const OUT_DIR = join(__DIR, '..', 'results');

mkdirSync(OUT_DIR, { recursive: true });

const csv = `round,temperature,energy,concept_jumps,accepted
1,1.0,0.85,false,true
2,0.9,0.78,false,true
3,0.8,0.72,true,true
4,0.7,0.68,false,true
5,0.6,0.65,false,true
`;

writeFileSync(join(OUT_DIR, 'annealing.csv'), csv);
console.log('=== Annealing CSV Exporter ===');
console.log('Index:', existsSync(INDEX) ? 'found' : 'not found');
console.log('Output: results/annealing.csv');
console.log('\n[PROTOTYPE] Generated sample CSV');
console.log('Full: integrate with TemperatureScheduler in index.js');
