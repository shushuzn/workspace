/**
 * generate-issue-templates.mjs — Generates GitHub ISSUE_TEMPLATE directories
 * Run: node scripts/generate-issue-templates.mjs [--dry-run]
 */

import { readdirSync, existsSync, mkdirSync, writeFileSync } from 'fs';
import { resolve, join } from 'path';

const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');
const args = process.argv.includes('--dry-run');

const BUG = `---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Description
<!-- Describe the bug clearly -->

## Steps to Reproduce
1.
2.
3.

## Expected Behavior
<!-- What you expected to happen -->

## Actual Behavior
<!-- What actually happened -->

## Environment
- Node version:
- OS:
`;

const FEATURE = `---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Summary
<!-- Brief description of the feature -->

## Motivation
<!-- Why is this feature needed? -->

## Proposed Solution
<!-- Describe your proposed solution -->

## Alternatives
<!-- Describe any alternative solutions considered -->
`;

const QUESTION = `---
name: Question
about: Ask a question about this project
title: '[Q] '
labels: question
assignees: ''
---

## Question
<!-- What is your question? -->

## Context
<!-- Provide additional context -->
`;

const dirs = readdirSync(ROOT, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules')
  .map(d => join(ROOT, d.name));

let generated = 0;
for (const dir of dirs) {
  const rel = dir.replace(ROOT, '').replace(/\\/g, '/').replace(/^\//, '');
  const ghDir = join(dir, '.github', 'ISSUE_TEMPLATE');
  if (!existsSync(ghDir)) {
    if (!args) {
      mkdirSync(ghDir, { recursive: true });
      writeFileSync(join(ghDir, 'bug_report.md'), BUG);
      writeFileSync(join(ghDir, 'feature_request.md'), FEATURE);
      writeFileSync(join(ghDir, 'question.md'), QUESTION);
    }
    console.log(`  + ${rel}/.github/ISSUE_TEMPLATE/`);
    generated++;
  }
}
console.log(`\n  ${generated} issue template(s) generated\n`);
