// ~/.omc/patrol-agent/src/index.js
// Main patrol loop — the heart of the patrol agent

import { loadState, saveState } from './state.js';
import { getPendingPlans, markPlanDone, markPlanSkipped } from './plans.js';
import { hasWorkingTreeChanges, createBranch, getCurrentBranch } from './git.js';
import { checkLint, hasLintErrors } from './lint.js';
import { executePlan, fixLintErrors } from './executor.js';
import { setTimeout as sleep } from 'timers/promises';

const WORKSPACE_ROOT = 'D:/OpenClaw/workspace';
const LOOP_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes
const MAX_RETRIES = 2;

let running = true;
let loopCount = 0;

// Handle shutdown signals gracefully
for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, () => {
    console.log(`\n[patrol] Received ${sig}, shutting down after current loop...`);
    running = false;
  });
}

function log(msg) {
  const ts = new Date().toISOString().replace('T', ' ').slice(0, 19);
  console.log(`[${ts}] ${msg}`);
}

function patrolLog(state, entry) {
  state.patrol_log = [entry, ...state.patrol_log].slice(0, 50); // Keep last 50
  saveState(state);
}

async function runLoop() {
  loopCount++;
  const state = loadState();
  state.loop_count = loopCount;
  state.last_patrol = new Date().toISOString();
  state.running = true;
  saveState(state);

  const actions = [];
  let didWork = false;

  // ─── 1. Execute pending plans ───────────────────────────────────────────
  const pendingPlans = getPendingPlans();
  if (pendingPlans.length > 0) {
    const plan = pendingPlans[0];
    log(`📋 Plan: ${plan.id} (${plan.file})`);

    const actionHash = `${plan.id}:${plan.hash || Date.now()}`;
    const alreadyDone = state.completed_actions.some(a => a.type === 'plan' && a.id === plan.id && a.hash === plan.hash);
    if (alreadyDone) {
      log(`  ⏭ Already executed, skipping.`);
    } else {
      let retryCount = 0;
      let success = false;
      while (retryCount <= MAX_RETRIES && !success) {
        const result = executePlan(plan);
        if (result.success) {
          success = true;
          markPlanDone(plan);
          state.completed_actions.push({
            type: 'plan',
            id: plan.id,
            hash: plan.hash || '',
            executed_at: new Date().toISOString(),
          });
          actions.push(`✓ Executed: ${plan.id}`);
          log(`  ✓ Done.`);
          didWork = true;
        } else {
          retryCount++;
          if (retryCount <= MAX_RETRIES) {
            log(`  ⚠ Retry #${retryCount} for: ${plan.id}: ${result.output.slice(0, 100)}`);
            await sleep(5000); // 5s backoff
          } else {
            log(`  ⚠ Skipped permanently: ${plan.id} | Error: ${result.output.slice(0, 200)}`);
            state.skipped.push({
              type: 'plan',
              id: plan.id,
              reason: result.output.slice(0, 200),
              at: new Date().toISOString(),
            });
            markPlanSkipped(plan, result.output);
            actions.push(`⚠ Skipped: ${plan.id}`);
            success = true; // Mark done to avoid re-trying
            didWork = true;
          }
        }
      }
    }
  }

  // ─── 2. Check lint errors (every loop — fast check) ───────────────────
  if (!didWork) { // Only check lint if no plan was executed
    const lintResults = checkLint();
    const projectsWithErrors = lintResults.filter(r => r.errors > 0);

    if (projectsWithErrors.length > 0) {
      for (const lr of projectsWithErrors) {
        if (lr.output === 'no-eslint-config') continue;
        log(`🔧 Lint errors in ${lr.project}: ${lr.errors} errors`);
        // Phase 1: just report, fix in Phase 3
        actions.push(`⚠ ${lr.errors} lint errors in ${lr.project} (fix in Phase 3)`);
        didWork = true;
      }
    }
  }

  // ─── 3. Optimization scan (every 10 loops) ─────────────────────────────
  if (loopCount % 10 === 0) {
    log(`[patrol] Optimization scan #${loopCount} (deferred to Phase 3)`);
  }

  // ─── 4. Research (every 50 loops) ─────────────────────────────────────
  if (loopCount % 50 === 0) {
    log(`[patrol] Research scan #${loopCount} (deferred to Phase 2)`);
  }

  // ─── 5. Patrol log ───────────────────────────────────────────────────
  const entry = {
    loop: loopCount,
    timestamp: new Date().toISOString(),
    actions,
    didWork,
  };
  patrolLog(state, entry);

  if (actions.length > 0) {
    log(`Loop #${loopCount} summary: ${actions.join(' | ')}`);
  } else {
    log(`Loop #${loopCount} — nothing to do.`);
  }

  log(`Next: Loop #${loopCount + 1} in ~${LOOP_INTERVAL_MS / 60000}min | Pending plans: ${pendingPlans.length}`);

  state.running = false;
  saveState(state);
}

async function main() {
  const state = loadState();

  if (state.running) {
    log('Patrol already running (check ~/.omc/patrol-state.json). Exiting.');
    process.exit(1);
  }

  log(`🚀 Patrol agent starting — loop_count resumes from ${state.loop_count}`);
  log(`   Workspace: ${WORKSPACE_ROOT}`);
  log(`   Plans dir: D:/OpenClaw/workspace/docs/superpowers/plans/`);
  log(`   Press Ctrl+C to stop.`);
  log('─'.repeat(60));

  while (running) {
    await runLoop();
    if (running) {
      try {
        await sleep(LOOP_INTERVAL_MS);
      } catch {
        // Interrupted
        break;
      }
    }
  }

  log('[patrol] Patrol loop stopped.');
}

main().catch(err => {
  console.error('[patrol] Fatal error:', err);
  process.exit(1);
});
