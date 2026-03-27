// ~/.omc/patrol-agent/src/plans.js
// Discover, sort, and update plan files in docs/superpowers/plans/

import { readdirSync, readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';

const PLANS_DIR = 'D:/OpenClaw/workspace/docs/superpowers/plans';

export function getPendingPlans() {
  if (!existsSync(PLANS_DIR)) return [];

  const files = readdirSync(PLANS_DIR).filter(f => f.endsWith('.md'));

  /** @type {Array<{id: string, file: string, status: string, hash: string, updated_at: string, frontmatter: object}>} */
  const plans = [];

  for (const file of files) {
    const filePath = join(PLANS_DIR, file);
    let raw;
    try {
      raw = readFileSync(filePath, 'utf-8');
    } catch {
      continue;
    }

    // Parse frontmatter: lines between first `---` markers
    const fmMatch = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n/);
    if (!fmMatch) continue;

    const frontmatter = {};
    for (const line of fmMatch[1].split('\n')) {
      const colonIdx = line.indexOf(':');
      if (colonIdx === -1) continue;
      const key = line.slice(0, colonIdx).trim();
      const val = line.slice(colonIdx + 1).trim();
      frontmatter[key] = val;
    }

    const status = frontmatter.status || 'pending';
    if (status !== 'pending' && status !== 'in_progress') continue;

    plans.push({
      id: frontmatter.id || file.replace('.md', ''),
      file: filePath,
      status,
      hash: frontmatter.hash || '',
      updated_at: frontmatter.updated_at || '',
      frontmatter,
    });
  }

  // Sort by updated_at ascending (oldest first)
  plans.sort((a, b) => {
    const ta = new Date(a.updated_at || 0).getTime();
    const tb = new Date(b.updated_at || 0).getTime();
    return ta - tb;
  });

  return plans;
}

export function markPlanDone(plan) {
  updatePlanStatus(plan, 'done');
}

export function markPlanSkipped(plan, reason) {
  updatePlanStatus(plan, 'skipped');
}

function updatePlanStatus(plan, status) {
  const filePath = plan.file;
  let raw;
  try {
    raw = readFileSync(filePath, 'utf-8');
  } catch {
    return;
  }

  // Replace status in frontmatter
  const updated = raw.replace(
    /^(---\r?\n)([\s\S]*?)(\r?\n---\r?\n)/,
    (_, open, fm, close) => {
      const lines = fm.split('\n').map(line => {
        if (line.startsWith('status:')) return `status: ${status}`;
        if (line.startsWith('updated_at:')) return `updated_at: ${new Date().toISOString()}`;
        return line;
      });
      return open + lines.join('\n') + close;
    }
  );

  try {
    writeFileSync(filePath, updated, 'utf-8');
  } catch {
    // Log but don't fail
  }
}
