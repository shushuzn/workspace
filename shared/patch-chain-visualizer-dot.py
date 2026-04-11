#!/usr/bin/env python3
"""Patch chain-visualizer.mjs to add --dot output mode"""
import sys

filepath = "80-PROJECTS/task-orchestrator/bin/chain-visualizer.mjs"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

if '"--dot"' in content or "'--dot'" in content:
    print("already has --dot")
    sys.exit(0)

old = """function demo() {
  const viz = createVisualizer(5);"""

new = """const args = process.argv.slice(2);
if (args.includes('--dot')) {
  const outFile = args[args.indexOf('--dot') + 1] || 'chain.dot';
  const steps = ['step1', 'step2', 'step3'];
  let dot = 'digraph chain {\\n  rankdir=LR;\\n';
  for (let i = 0; i < steps.length; i++) {
    dot += `  "${steps[i]}" [label="${steps[i]} (${i+1}/3)"];
`;
    if (i > 0) dot += `  "${steps[i-1]}" -> "${steps[i]}";
`;
  }
  dot += '}\\n';
  const { writeFileSync } = await import('fs');
  writeFileSync(outFile, dot, 'utf8');
  console.log('[DOT] Exported to ' + outFile);
  process.exit(0);
}

function demo() {
  const viz = createVisualizer(5);"""

if old in content:
    content = content.replace(old, new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("added --dot")
else:
    print("skip: pattern not found")
