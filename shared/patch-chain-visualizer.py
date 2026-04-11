#!/usr/bin/env python3
"""Patch chain-visualizer.mjs to add --json output mode"""
import sys
import re

filepath = "80-PROJECTS/task-orchestrator/bin/chain-visualizer.mjs"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

if '--json' in content:
    print("already has --json")
    sys.exit(0)

# Find the main function and inject --json handling
# We need to find where args is defined and add the json block
old_pattern = "const args = process.argv.slice(2);"
new_block = """const args = process.argv.slice(2);
if (args.includes('--json')) {
  const viz = createVisualizer(5);
  viz.start();
  viz.step('browse');
  viz.step('search');
  viz.step('extract');
  viz.step('write');
  viz.step('verify');
  viz.done();
  console.log(JSON.stringify({currentStep: 5, totalSteps: 5, pct: 100}));
  process.exit(0);
}"""

if old_pattern in content and '--json' not in content:
    content = content.replace(old_pattern, new_block)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("added --json")
else:
    print("skip")
