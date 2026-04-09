#!/usr/bin/env node
/** Export task-orchestrator rule graph as JSON */
import { readFileSync } from 'fs';

const content = readFileSync('80-PROJECTS/task-orchestrator/src/planner.mjs', 'utf8');
const rules = [...content.matchAll(/keywords:\s*\[([^\]]+)\]/g)].map(m => m[1]);
console.log('Rules found:', rules.length);
console.log(JSON.stringify(rules, null, 2));
