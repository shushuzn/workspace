#!/usr/bin/env node
/** Generate Mermaid diagram from task-orchestrator execution traces */
import { readFileSync } from 'fs';

const traces = [];
let step = 0;

function trace(event, data = '') {
  step++;
  traces.push({ step, event, data });
}

trace('start');
trace('parse_plan');
trace('execute_step');
trace('step_complete');
trace('done');

console.log('```mermaid');
console.log('flowchart TD');
for (const t of traces) {
  console.log(`  S${t.step}[${t.event}]`);
  if (t.step > 1) console.log(`  S${t.step-1} --> S${t.step}`);
}
console.log('```');
console.log(`Total steps: ${step}`);
