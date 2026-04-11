#!/usr/bin/env python3
"""Patch exec-history.mjs to add --best CLI flag"""
import sys

filepath = "80-PROJECTS/task-orchestrator/bin/exec-history.mjs"
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

if "process.argv.includes('--best')" in content:
    print("already has --best")
    sys.exit(0)

old = """const cmd = process.argv[2];"""

new = """const cmd = process.argv.includes('--best') ? 'best' : process.argv[2];"""

if old in content:
    content = content.replace(old, new)
    # Also add JSON output for best
    old_best = """  console.log(`Best adapter for "${taskType}": ${best.adapterId}`);"""
    new_best = """  if (process.argv.includes('--json')) {
    console.log(JSON.stringify({ taskType, best }));
  } else {
    console.log(`Best adapter for "${taskType}": ${best.adapterId}`);
  }"""
    if old_best in content:
        content = content.replace(old_best, new_best)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("added --best")
else:
    print("skip: pattern not found")
