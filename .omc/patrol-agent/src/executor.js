// ~/.omc/patrol-agent/src/executor.js
// Execute a plan by invoking claude CLI with instructions
// Reads plan content and feeds it as context to claude

import { readFileSync } from 'fs';
import { execSync } from 'child_process';

const WORKSPACE_ROOT = 'D:/OpenClaw/workspace';

/**
 * Execute a plan file using claude CLI.
 * The plan content is read and passed as context.
 * @param {{ id: string, file: string, frontmatter: object }} plan
 * @returns {{ success: boolean, output: string }}
 */
export function executePlan(plan) {
  let planContent;
  try {
    planContent = readFileSync(plan.file, 'utf-8');
  } catch (err) {
    return { success: false, output: `Failed to read plan: ${err.message}` };
  }

  // Extract markdown body (skip frontmatter)
  const bodyMatch = planContent.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n([\s\S]*)$/);
  const body = bodyMatch ? bodyMatch[1].trim() : planContent;

  // Build the claude command instruction
  const instruction = `Execute the following plan:\n\n# Plan: ${plan.id}\n\n${body}`;

  try {
    // Use claude --print with the instruction
    // The claude CLI will execute the task autonomously
    const output = execSync(
      `claude --print "${instruction.replace(/"/g, '\\"')}"`,
      {
        cwd: WORKSPACE_ROOT,
        encoding: 'utf-8',
        timeout: 300000, // 5 min per plan
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, CLAUDE_NO_CHECK_UPDATE: '1' },
      }
    );
    return { success: true, output: output.trim() };
  } catch (err) {
    return { success: false, output: err.stdout || err.message };
  }
}

/**
 * Fix lint errors in a project by running eslint --fix.
 * @param {string} projectDir
 * @returns {{ success: boolean, output: string }}
 */
export function fixLintErrors(projectDir) {
  try {
    const output = execSync(
      `npx eslint . --fix --max-warnings 0`,
      { cwd: projectDir, encoding: 'utf-8', timeout: 120000, stdio: ['pipe', 'pipe', 'pipe'] }
    );
    return { success: true, output: output || 'lint fixed' };
  } catch (err) {
    return { success: false, output: err.stdout || err.message };
  }
}
