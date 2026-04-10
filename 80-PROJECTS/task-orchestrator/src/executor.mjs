import { mkdirSync, writeFileSync, readFileSync, rmSync, appendFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import os from 'os';
import { randomUUID } from 'crypto';
import chalk from 'chalk';
import { createVisualizer } from '../bin/chain-visualizer.mjs';
import { createGuard } from './validators/hookify-guard.mjs';
import { spawn } from 'child_process';
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const adapterTypeColors = {
    swarm: chalk.cyan,
    opencli: chalk.green,
    'cli-anything': chalk.yellow,
    'multi-agent-hub': chalk.magenta,
    shell: chalk.gray,
};
function stepColor(adapterType) {
    return adapterTypeColors[adapterType] ?? chalk.white;
}
export class Executor {
    registry;
    options;
    cache = new Map();
    /** Path to persistent cache file */
    cacheFile;
    constructor(registry, options = {}) {
        this.registry = registry;
        this.options = options;
        // Load persisted cache if cacheTtlMs is enabled
        if (this.options.cacheTtlMs) {
            this.cacheFile = join(os.homedir(), '.unified-agent-cli', 'cache.json');
            this.loadCache();
            // Save cache on process exit
            process.on('exit', () => this.saveCache());
        }
    }
    loadCache() {
        if (!this.cacheFile || !existsSync(this.cacheFile)) return;
        try {
            const data = JSON.parse(readFileSync(this.cacheFile, 'utf-8'));
            const now = Date.now();
            for (const [key, entry] of Object.entries(data)) {
                if (entry.expiresAt > now) {
                    this.cache.set(key, entry);
                }
            }
            if (this.cache.size > 0) {
                console.warn(`[cache] loaded ${this.cache.size} entries from ${this.cacheFile}`);
            }
        } catch (e) {
            console.warn(`[cache] failed to parse cache file: ${e.message}`);
        }
    }
    saveCache() {
        if (!this.cacheFile || this.cache.size === 0) return;
        try {
            const obj = Object.fromEntries(this.cache);
            writeFileSync(this.cacheFile, JSON.stringify(obj), 'utf-8');
        } catch {}
    }
    /** Current runId (set at the start of execute()) */
    currentRunId;
    get runId() {
        return this.currentRunId;
    }
    updateProgress(msg) {
        // \r moves cursor to start of line — overwrites previous progress line
        process.stderr.write(`\r${msg.padEnd(80, ' ')}\r`);
    }
    async execute(steps, ctx) {
        // Catch unhandled promise rejections during this execution
        const rejectionHandler = (reason) => {
            console.error(`[unhandledRejection] ${reason instanceof Error ? reason.message : String(reason)}`);
        };
        process.on('unhandledRejection', rejectionHandler);
        try {
        if (steps.length === 0)
            return [];
        const dryRun = ctx?.dryRun || steps.some(s => s.dryRun);
        if (dryRun) {
            console.log('[DRY RUN] Steps that would be executed:');
            for (const step of steps) {
                console.log('  adapter=' + step.adapterId + ' command=' + step.command + ' args=' + JSON.stringify(step.args));
            }
            return steps.map(s => ({ success: true, output: '[DRY RUN]', logs: '', artifacts: [], fatal: false }));
        }
        const workingDir = this.options.workingDir ?? join(os.tmpdir(), 'unified-agent-cli');
        mkdirSync(workingDir, { recursive: true });
        const runId = this.options.runId ?? randomUUID();
        this.currentRunId = runId;
        const viz = createVisualizer(steps.length);
        viz.start();
        const statePath = join(workingDir, `run-${runId}.json`);
        // Initialize empty task context
        let taskContext = {};
        writeFileSync(statePath, JSON.stringify(taskContext), 'utf-8');
        const fullCtx = {
            taskContext,
            workingDir,
            env: process.env,
            interactive: process.stdin.isTTY,
            ...ctx,
        };
        // Build DAG: for each step, which steps does it depend on?
        // A step depends on another if its inputSlots match the other's outputSlots
        const deps = this.buildDependencyGraph(steps);
        // Topological sort into depth layers — all steps in a layer have no unmet dependencies
        const layers = this.topologicalLayers(steps, deps);
        // Map step index → its layer index (= depth from root)
        const stepDepth = new Map();
        for (let li = 0; li < layers.length; li++) {
            for (const idx of layers[li]) stepDepth.set(idx, li);
        }
        // --explain: show layers, parallel groups, and inputSlot wiring
        if (this.options.explain) {
            process.stderr.write(chalk.blue('\n[execution plan]:\n'));
            // Pre-build outputSlot→step index map for O(1) lookups (was O(n²) nested loop)
            const outputSlotMap = new Map(); // outputSlotName → [stepIndex, ...]
            for (let j = 0; j < steps.length; j++) {
                for (const out of (steps[j].outputSlots || [])) {
                    if (!outputSlotMap.has(out)) outputSlotMap.set(out, []);
                    outputSlotMap.get(out).push(j);
                }
            }
            for (let li = 0; li < layers.length; li++) {
                const layerSteps = layers[li].map(idx => steps[idx]);
                const parallel = layerSteps.length > 1;
                const groupLabel = parallel ? `layer ${li} (${layerSteps.length} parallel)` : `layer ${li}`;
                process.stderr.write(`  ${chalk.cyan(groupLabel)}:\n`);
                for (const idx of layers[li]) {
                    const step = steps[idx];
                    const key = `${step.adapterId}:${step.command}`;
                    if (step.inputSlots.length === 0 && (!step.dependsOn || step.dependsOn.length === 0)) {
                        process.stderr.write(`    ${chalk.gray('└─')} ${stepColor(step.adapterType)(step.adapterId)}: ${step.command} ${step.args.join(' ')} ${chalk.gray('[root]')}\n`);
                    }
                    else {
                        process.stderr.write(`    ${chalk.gray('└─')} ${stepColor(step.adapterType)(step.adapterId)}: ${step.command} ${step.args.join(' ')}\n`);
                        for (const input of step.inputSlots) {
                            const producers = outputSlotMap.get(input) || [];
                            for (const prevIdx of producers) {
                                if (prevIdx < idx) {
                                    process.stderr.write(`        ${chalk.gray('←')} ${stepColor(steps[prevIdx].adapterType)(steps[prevIdx].adapterId)}:${chalk.gray(`outputSlots[${input}]`)}\n`);
                                }
                            }
                        }
                        if (step.dependsOn && step.dependsOn.length > 0) {
                            for (const depId of step.dependsOn) {
                                process.stderr.write(`        ${chalk.gray('←')} ${chalk.yellow(depId)} ${chalk.gray('[explicit dependsOn]')}\n`);
                            }
                        }
                    }
                }
            }
        }
        const results = new Array(steps.length);
        const stepStartTimes = new Map(); // step index → start timestamp (spans all layers)
        let cascadeStop = false; // true when a fatal step triggers cascade-on-error
        for (let layerIdx = 0; layerIdx < layers.length; layerIdx++) {
            const layer = layers[layerIdx];
            // cascade-stop: if a previous layer triggered cascade-on-error, skip remaining layers
            if (cascadeStop) {
                for (const stepIdx of layer) {
                    results[stepIdx] = {
                        success: false,
                        output: '',
                        logs: 'cascade-stopped',
                        artifacts: [],
                        error: 'Skipped due to cascade stop from earlier layer',
                        fatal: false,
                    };
                }
                if (!this.options.verbose) {
                    process.stderr.write(`[layer ${layerIdx}] ${chalk.yellow('(cascade stopped)')}\n`);
                }
                continue;
            }
            if (this.options.verbose) {
                const names = layer.map(i => {
                    const c = stepColor(steps[i].adapterType);
                    return `${c(steps[i].adapterId)}:${steps[i].command}`;
                }).join(', ');
                process.stderr.write(`[layer ${layerIdx}] ${layer.length} parallel step(s): ${names}\n`);
            }
            else {
                const names = layer.map(i => {
                    const c = stepColor(steps[i].adapterType);
                    return c(steps[i].adapterId);
                }).join(' ');
                process.stderr.write(`[layer ${layerIdx}] ${names}\n`);
            }
            // Execute all steps in this layer in parallel
            const promises = layer.map(async (stepIdx) => {
                const step = steps[stepIdx];
                // Load latest state — read fresh from disk for each step
                try {
                    const raw = readFileSync(statePath, 'utf-8');
                    Object.assign(taskContext, JSON.parse(raw));
                }
                catch {
                    // State file may not exist yet
                }
                // Inject inputSlots from taskContext into step args
                const resolvedStep = this.resolveInputSlots(step, fullCtx.taskContext, fullCtx.prompt);
                if (!this.options.verbose) {
                    this.updateProgress(`[layer ${layerIdx}] running ${stepColor(resolvedStep.adapterType)(resolvedStep.adapterId)}: ${resolvedStep.command}`);
                }
                // Cache lookup: only cache steps with no inputSlots (deterministic, no prior state needed)
                const cacheKey = this.cacheKey(resolvedStep);
                if (this.options.cacheTtlMs && resolvedStep.inputSlots.length === 0) {
                    const cached = this.cache.get(cacheKey);
                    if (cached && cached.expiresAt > Date.now()) {
                        if (!this.options.verbose) {
                            this.updateProgress(`[layer ${layerIdx}] cached ${stepColor(resolvedStep.adapterType)(resolvedStep.adapterId)}: ${resolvedStep.command}`);
                        }
                        results[stepIdx] = { ...cached.result, cached: true };
                        return;
                    }
                }
                // Find adapter
                // Built-in timer step — no adapter needed, execute inline
                if (resolvedStep.adapterId === ':timer') {
                    const delayMs = parseInt(resolvedStep.args[0]) || 1000;
                    await new Promise(r => setTimeout(r, delayMs));
                    const timerResult = { success: true, output: `waited ${delayMs}ms`, logs: '', artifacts: [], fatal: false };
                    results[stepIdx] = timerResult;
                                        return;
                }
                const adapter = await this.registry.findAdapter(resolvedStep);
                if (!adapter) {
                    const err = {
                        success: false,
                        output: '',
                        logs: '',
                        artifacts: [],
                        error: `No adapter found for step: ${resolvedStep.adapterId}`,
                        code: 'ADAPTER_NOT_FOUND',
                        fatal: true,
                    };
                    results[stepIdx] = err;
                                        return;
                }
                // ── Two-stage review gate ────────────────────────────────────────
                // Skip review if step already has a passed review, or if reviewers are disabled globally
                if (!resolvedStep.review && this.options.enableReview !== false) {
                    if (this.options.verbose) {
                        process.stderr.write(`[review] two-stage review: ${resolvedStep.adapterId}:${resolvedStep.command}\n`);
                    }
                    const reviewResult = await this.runTwoStageReview(resolvedStep, fullCtx);
                    resolvedStep.review = reviewResult;
                    const specFailed = !reviewResult.spec.passed;
                    const codeFailed = !reviewResult.code.passed;
                    if (specFailed || codeFailed) {
                        const allIssues = [
                            ...(specFailed ? reviewResult.spec.issues.map(i => `SPEC: ${i}`) : []),
                            ...(codeFailed ? reviewResult.code.issues.map(i => `CODE: ${i}`) : []),
                        ];
                        const reviewErr = {
                            success: false, output: '', logs: '', artifacts: [],
                            error: `Review failed: ${allIssues.join('; ')}`,
                            code: 'REVIEW_FAILED', fatal: false,
                        };
                        results[stepIdx] = reviewErr;
                                                return;
                    }
                    if (this.options.verbose) {
                        process.stderr.write(`[review] ✓ spec + code both passed\n`);
                    }
                }
                // Execute with optional timeout + retry logic
                if (this.options.verbose) {
                    process.stderr.write(`[step] ${stepColor(resolvedStep.adapterType)(resolvedStep.adapterId)} ${resolvedStep.command} ${resolvedStep.args.join(' ')}\n`);
                }
                let maxRetries = resolvedStep.maxRetries ?? this.options.maxRetries ?? 3;
                let result = null;
                let attempt = 0;
                // Hookify guard — block dangerous commands before execution
                if (this.options.enableHookifyGuard !== false) {
                    const guard = createGuard();
                    const check = guard.check(resolvedStep.command);
                    if (check.blocked) {
                        const blockErr = {
                            success: false, output: '', logs: '', artifacts: [],
                            error: `Hookify blocked: ${check.ruleName} — ${check.message.split('\n')[0]}`,
                            code: 'HOOKIFY_BLOCKED', fatal: false,
                        };
                        results[stepIdx] = blockErr;
                                                return;
                    }
                }
                stepStartTimes.set(stepIdx, Date.now());
                while (attempt <= maxRetries) {
                    try {
                        const effectiveTimeout = resolvedStep.timeoutMs
                            ?? this.options.adapterTimeoutMs?.[resolvedStep.adapterType]
                            ?? this.options.defaultTimeoutMs;
                        if (effectiveTimeout) {
                            result = await Promise.race([
                                adapter.execute(resolvedStep, fullCtx),
                                new Promise((_, reject) => setTimeout(() => reject(new Error(`Step timed out after ${effectiveTimeout}ms`)), effectiveTimeout)),
                            ]);
                        }
                        else {
                            result = await adapter.execute(resolvedStep, fullCtx);
                        }
                        break; // success or fatal error, exit retry loop
                    }
                    catch (err) {
                        attempt++;
                        const errMsg = err instanceof Error ? err.message : String(err);
                        const isTimeout = errMsg.includes('timed out');
                        const errCode = result?.code ?? (isTimeout ? 'STEP_TIMEOUT' : 'EXECUTION_ERROR');
                        // Strategy matching: find first matching strategy
                        const strategy = this.options.strategies?.find(s => {
                            if (s.match === errCode || errMsg.includes(s.match))
                                return true;
                            return false;
                        });
                        if (strategy) {
                            if (this.options.verbose) {
                                process.stderr.write(`[strategy] matched "${strategy.match}" → ${strategy.action}\n`);
                            }
                            if (strategy.action === 'skip') {
                                results[stepIdx] = {
                                    success: false, output: '', logs: '',
                                    artifacts: [], error: `Skipped by strategy: ${errMsg}`,
                                    code: errCode, fatal: false, attempts: attempt,
                                };
                                                                return; // skip this step, continue to next layer
                            }
                            if (strategy.action === 'fallback' && strategy.fallbackCommand) {
                                // Replace command and re-run without incrementing attempt
                                const fallbackStep = { ...resolvedStep, command: strategy.fallbackCommand };
                                if (this.options.verbose) {
                                    process.stderr.write(`[strategy] falling back to: ${fallbackStep.command}\n`);
                                }
                                // Re-execute fallback (no retry loop for fallback to avoid infinite loop)
                                try {
                                    const fallbackResult = await adapter.execute(fallbackStep, fullCtx);
                                    results[stepIdx] = fallbackResult;
                                                                        return;
                                }
                                catch (fbErr) {
                                    // Fallback also failed — fall through to normal retry
                                    if (this.options.verbose) {
                                        process.stderr.write(`[strategy] fallback failed: ${fbErr instanceof Error ? fbErr.message : String(fbErr)}\n`);
                                    }
                                }
                            }
                            // 'retry' action or fallback failed → use strategy maxRetries if set
                            maxRetries = strategy.maxRetries ?? maxRetries;
                        }
                        // Depth-based retry skip: root steps (depth <= 1) are critical — always retry; deeper steps are derived, skip retry if first attempt fails
                        const depth = stepDepth.get(stepIdx) ?? 0;
                        const chainInfo = causalityInfo.get(stepIdx);
                        const isRootRelated = chainInfo && (chainInfo.root === stepIdx || (chainInfo.chain && chainInfo.chain.includes(chainInfo.root)));
                        if ((depth <= 1 || isRootRelated) && attempt === 1) {
                            process.stderr.write(`[retry] depth-${depth} step, forcing retry: ${errMsg.slice(0, 60)}\n`);
                        } else if (depth > 1 && attempt === 1) {
                            process.stderr.write(`[retry-skip] depth-${depth} step (downstream), skipping retry: ${errMsg.slice(0, 60)}\n`);
                            result = { success: false, output: '', logs: '', artifacts: [], error: errMsg, code: errCode, fatal: false };
                                                        return;
                        }
                        if (attempt > maxRetries) {
                            result = {
                                success: false,
                                output: '',
                                logs: '',
                                artifacts: [],
                                error: errMsg,
                                code: errCode,
                                fatal: true,
                            };
                            if (this.options.cascadeOnError)
                                cascadeStop = true;
                            break;
                        }
                        // Exponential backoff: 1s, 2s, 4s...
                        const delay = result?.retryMs ?? 1000 * Math.pow(2, attempt - 1);
                        process.stderr.write(`[RETRY ${resolvedStep.adapterId} attempt ${attempt}/${maxRetries}] backing off ${delay}ms: ${errMsg}\n`);
                        await new Promise(r => setTimeout(r, delay));
                    }
                }
                if (!result) {
                    result = {
                        success: false,
                        output: '',
                        logs: '',
                        artifacts: [],
                        error: 'Unexpected: result is null after retry loop',
                        code: 'NULL_RESULT',
                        fatal: true,
                    };
                    if (this.options.cascadeOnError)
                        cascadeStop = true;
                }
                result.attempts = attempt + (result.success ? 1 : 0);
                result.durationMs = Date.now() - (stepStartTimes.get(stepIdx) ?? Date.now());
                results[stepIdx] = result;
                                viz.step(resolvedStep.command);
                if (!this.options.verbose) {
                    const elapsed = ((Date.now() - (stepStartTimes.get(stepIdx) ?? Date.now())) / 1000).toFixed(1);
                    const status = result.success ? `\u2713` : `\u2717`;
                    // Print each completed step on its own line (streaming — no \r overwrite)
                    process.stderr.write(`[layer ${layerIdx}] ${status} ${stepColor(resolvedStep.adapterType)(resolvedStep.adapterId)} ${resolvedStep.command} (${elapsed}s)\n`);
                    if (result.durationMs !== undefined) {
                        process.stderr.write(`[PERF ${resolvedStep.adapterId}: ${result.durationMs}ms]\n`);
                    }
                }
                // onStepResult callback for streaming JSON Lines output
                if (this.options.onStepResult) {
                    this.options.onStepResult(resolvedStep, result, result.durationMs ?? 0);
                }
                if (this.options.verbose) {
                    process.stderr.write(`[result] success=${result.success} artifacts=${result.artifacts.length}\n`);
                }
                // Update state with outputSlots (only on success)
                if (result.success && result.artifacts.length > 0) {
                    for (const artifact of result.artifacts) {
                        const ref = `${artifact.type}:path`; // simple convention
                        taskContext[ref] = artifact;
                    }
                    writeFileSync(statePath, JSON.stringify(taskContext), 'utf-8');
                }
                // Cache successful results with no inputSlots (only for deterministic steps)
                if (this.options.cacheTtlMs && result.success && resolvedStep.inputSlots.length === 0 && !this.options.dryRunCache) {
                    this.cache.set(cacheKey, { result: { ...result }, expiresAt: Date.now() + this.options.cacheTtlMs });
                    if (this.options.verbose) {
                        process.stderr.write(`[cache] STORED ${resolvedStep.adapterId}: ${resolvedStep.command} (TTL ${this.options.cacheTtlMs}ms)\n`);
                    }
                }
            });
            await Promise.all(promises);
            // After this layer, check for fatal errors — stop if any and not continueOnError
            const layerResults = layer.map(i => results[i]).filter(Boolean);
            const fatalInLayer = layerResults.find(r => r.fatal && !this.options.continueOnError);
            if (fatalInLayer) {
                // Mark remaining steps as skipped
                for (let li = layerIdx + 1; li < layers.length; li++) {
                    for (const stepIdx of layers[li]) {
                        if (!results[stepIdx]) {
                            results[stepIdx] = { success: false, output: '', logs: '', artifacts: [], error: 'Skipped due to earlier fatal error', code: 'CASCADE_STOP', fatal: true };
                        }
                    }
                }
                break;
            }
        }
        // Cleanup
        try {
            rmSync(statePath, { force: true });
        }
        catch { /* ignore */ }
        // Compute causality chains per step from the dependency graph
        const causalityInfo = this.buildCausalityInfo(steps, deps);
        // Record audit log (append-only event sourcing log)
        await this.recordAuditLog(runId, steps, results, causalityInfo, fullCtx.prompt);
        // Persist per-step stdout/stderr logs
        this.persistLogs(runId, results);
        // ── Meta-cognitive self-audit ─────────────────────────────────────
        // After execution, scan for "未审视自己" patterns and generate seeds
        if (this.options.enableSelfAudit !== false) {
            this.runSelfAudit(steps, results, fullCtx.prompt).catch(e => { console.error('[self-audit] error:', e.message); });
        }
        // JSON output export
        if (this.options.outputJson) {
            const outPath = join(fullCtx.workingDir || process.cwd(), `run-${runId}.json`);
            writeFileSync(outPath, JSON.stringify({ runId, steps: results }, null, 2), 'utf-8');
            console.log(`[executor] JSON output written to ${outPath}`);
        }
        viz.done();
        return results;
        } finally {
            process.removeListener('unhandledRejection', rejectionHandler);
        }
    }
    /** Build a dependency graph: for each step index, which other step indices it depends on */
    buildDependencyGraph(steps) {
        const deps = new Map();
        for (let i = 0; i < steps.length; i++) {
            deps.set(i, new Set());
        }
        // For each step, find which earlier steps produce its required inputSlots
        for (let i = 0; i < steps.length; i++) {
            for (const input of steps[i].inputSlots) {
                for (let j = 0; j < i; j++) {
                    if (steps[j].outputSlots.includes(input)) {
                        deps.get(i).add(j);
                    }
                }
            }
            // Add explicit dependsOn edges (adapterId:command format)
            if (steps[i].dependsOn) {
                for (const depId of steps[i].dependsOn) {
                    for (let j = 0; j < i; j++) {
                        const stepKey = `${steps[j].adapterId}:${steps[j].command}`;
                        if (stepKey === depId) {
                            deps.get(i).add(j);
                        }
                    }
                }
            }
        }
        
// Detect cycles using single DFS pass (Tarjan-inspired) — O(V+E)
const visited = new Set();
const onStack = new Set();
let hasGlobalCycle = false;
let cycleNode = -1;
function dfsCycle(node) {
    if (onStack.has(node)) { hasGlobalCycle = true; cycleNode = node; return; }
    if (visited.has(node)) return;
    visited.add(node);
    onStack.add(node);
    for (const dep of (deps.get(node) || new Set())) {
        dfsCycle(dep);
        if (hasGlobalCycle) return;
    }
    onStack.delete(node);
}
for (let i = 0; i < steps.length; i++) {
    if (!visited.has(i)) {
        dfsCycle(i);
        if (hasGlobalCycle) throw new Error(`[dependency] cycle detected at step ${cycleNode}`);
    }
}

        return deps;
    }
    /** Public: compute topological layers for a step list (used by index.ts for --dry-run display) */
    static computeLayers(steps) {
        // Build deps graph
        const deps = new Map();
        for (let i = 0; i < steps.length; i++)
            deps.set(i, new Set());
        for (let i = 0; i < steps.length; i++) {
            for (const input of steps[i].inputSlots) {
                for (let j = 0; j < i; j++) {
                    if (steps[j].outputSlots.includes(input))
                        deps.get(i).add(j);
                }
            }
            if (steps[i].dependsOn) {
                for (const depId of steps[i].dependsOn) {
                    for (let j = 0; j < i; j++) {
                        if (`${steps[j].adapterId}:${steps[j].command}` === depId)
                            deps.get(i).add(j);
                    }
                }
            }
        }
        // Kahn's algorithm
        const inDegree = new Array(steps.length).fill(0);
        for (const [i, d] of deps)
            inDegree[i] = d.size;
        const layers = [];
        const remaining = new Set(steps.map((_, i) => i));
        while (remaining.size > 0) {
            const ready = [];
            for (const i of remaining)
                if (inDegree[i] === 0)
                    ready.push(i);
            if (ready.length === 0) {
                layers.push(Array.from(remaining));
                break;
            }
            layers.push(ready);
            for (const i of ready) {
                remaining.delete(i);
                for (const j of remaining) {
                    if (deps.get(j).has(i))
                        inDegree[j]--;
                }
            }
        }
        return layers;
    }
    /** Kahn's algorithm → array of layers (each layer = steps with no unmet dependencies) */
    topologicalLayers(steps, deps) {
        // inDegree = how many deps each step has
        const inDegree = new Array(steps.length).fill(0);
        for (const [i, d] of deps) {
            inDegree[i] = d.size;
        }
        const layers = [];
        const remaining = new Set(steps.map((_, i) => i));
        while (remaining.size > 0) {
            // All steps with zero in-degree = no unmet dependencies
            const ready = [];
            for (const i of remaining) {
                if (inDegree[i] === 0)
                    ready.push(i);
            }
            if (ready.length === 0) {
                // Cycle detected — fall back: execute remaining sequentially
                const remainingArr = Array.from(remaining);
                layers.push(remainingArr);
                break;
            }
            layers.push(ready);
            // Remove ready steps and update in-degrees
            for (const i of ready) {
                remaining.delete(i);
                for (const j of remaining) {
                    if (deps.get(j).has(i)) {
                        inDegree[j]--;
                    }
                }
            }
        }
        return layers;
    }
    resolveInputSlots(step, taskContext, prompt) {
        const resolvedArgs = step.args.map(arg => this.resolveEnvVar(arg, prompt));
        if (step.inputSlots.length === 0)
            return { ...step, args: resolvedArgs };
        // Inject artifact paths as extra args
        const extraArgs = step.inputSlots
            .map(ref => taskContext[ref]?.path ?? '')
            .filter(Boolean);
        return { ...step, args: [...resolvedArgs, ...extraArgs] };
    }
    /** Replace $VAR_NAME with process.env.VAR_NAME, leave unchanged if unset */
    resolveEnvVar(arg, prompt) {
        return arg.replace(/\$(\w+)/g, (_, name) => {
            if (name === 'DATE')
                return new Date().toISOString().slice(0, 10);
            if (name === 'TIME')
                return new Date().toTimeString().slice(0, 8).replace(/ /g, '');
            if (name === 'RANDOM')
                return Math.random().toString(36).slice(2, 8);
            if (name === 'PROMPT')
                return prompt ?? '';
            return process.env[name] ?? '';
        });
    }
    cacheKey(step) {
        return `${step.adapterId}:${step.command}:${step.args.join(',')}:${step.workingDir||''}`;
    }
    /**
     * Pre-flight check: verify all adapters are available for the given steps.
     * Returns an array of { step, adapterId, available, error }.
     */
    async checkAdapters(steps) {
        const results = [];
        for (const step of steps) {
            const adapter = await this.registry.findAdapter(step);
            if (!adapter) {
                results.push({ step, adapterId: step.adapterId, available: false, error: 'No adapter found' });
            }
            else {
                const avail = await adapter.checkAvailable();
                results.push({ step, adapterId: step.adapterId, available: avail, error: avail ? undefined : 'Adapter not available' });
            }
        }
        return results;
    }
    /**
     * Two-stage review pipeline:
     *   Stage 1 — Spec reviewer: does the step spec (adapter+command+args) match the task goal?
     *   Stage 2 — Code reviewer: is the implementation correct and safe?
     * Each stage runs a fresh subagent. Both must pass before the step proceeds.
     * Review result is stamped on the step: { spec: { passed, issues }, code: { passed, issues } }
     */
    async runTwoStageReview(step, ctx) {
        const reviewers = [
            {
                name: 'spec',
                prompt: `You are a spec compliance reviewer.
Given this step:
  adapterId: ${step.adapterId}
  adapterType: ${step.adapterType}
  command: ${step.command}
  args: ${JSON.stringify(step.args)}
  inputSlots: ${JSON.stringify(step.inputSlots)}
  outputSlots: ${JSON.stringify(step.outputSlots)}

Task goal: ${ctx.prompt || '(none)'}

Critically evaluate:
1. Does this adapter+command correctly address the task goal?
2. Are the args correct and complete?
3. Are the inputSlots/outputSlots wired correctly?
4. Is there any spec-level issue (wrong tool, missing params, wrong data flow)?

Respond ONLY with a JSON object:
{"passed": true/false, "issues": ["issue1", "issue2", ...]}

If you find NO issues, set passed=true with an empty issues array.
Do not add explanations outside the JSON.`,
            },
            {
                name: 'code',
                prompt: `You are a code quality reviewer.
Given this step:
  adapterId: ${step.adapterId}
  adapterType: ${step.adapterType}
  command: ${step.command}
  args: ${JSON.stringify(step.args)}
  inputSlots: ${JSON.stringify(step.inputSlots)}
  outputSlots: ${JSON.stringify(step.outputSlots)}

Evaluate implementation quality:
1. Are there potential runtime errors (null checks, type errors)?
2. Are there security concerns (injection, credential exposure)?
3. Is the error handling adequate?
4. Are there race conditions or concurrency issues?

Respond ONLY with a JSON object:
{"passed": true/false, "issues": ["issue1", "issue2", ...]}

If you find NO issues, set passed=true with an empty issues array.
Do not add explanations outside the JSON.`,
            },
        ];

        const result = { spec: { passed: false, issues: [] }, code: { passed: false, issues: [] } };

        // Run reviewers in parallel, each with 1 retry on timeout
        await Promise.all(reviewers.map(async (reviewer) => {
            for (let attempt = 1; attempt <= 2; attempt++) {
                try {
                    const res = await new Promise((resolve) => {
                        const promptFile = join(os.tmpdir(), `review-${randomUUID()}.txt`);
                        writeFileSync(promptFile, reviewer.prompt, 'utf-8');
                        const child = spawn('claude.cmd', ['--print', '--dangerously-skip-permissions', `--system-prompt-file=${promptFile}`], {
                            shell: true,
                            stdio: ['pipe', 'pipe', 'pipe'],
                            windowsHide: true,
                        });
                        let stdout = '';
                        let stderr = '';
                        child.stdout.on('data', (d) => { stdout += d.toString(); });
                        child.stderr.on('data', (d) => { stderr += d.toString(); });
                        child.on('close', () => {
                            try { rmSync(promptFile); } catch {}
                            let parsed = null;
                            try {
                                const cleaned = stdout.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
                                parsed = JSON.parse(cleaned);
                            } catch (e) {
                                parsed = { passed: false, issues: [`reviewer parse error: ${stderr || stdout || 'no output'}`.slice(0, 200)] };
                            }
                            resolve({ parsed, stderr, stdout });
                        });
                        child.on('error', () => {
                            try { rmSync(promptFile); } catch {}
                            resolve({ parsed: null, stderr: '', stdout: '' });
                        });
                        // 60s timeout per reviewer (up from 30s)
                        setTimeout(() => {
                            child.kill();
                            resolve({ parsed: null, stderr: 'timeout', stdout: '' });
                        }, 60000);
                    });

                    if (res.parsed) {
                        result[reviewer.name] = { passed: res.parsed.passed === true, issues: Array.isArray(res.parsed.issues) ? res.parsed.issues : [] };
                    } else {
                        // Timeout or spawn error — retry once
                        if (attempt < 2) {
                            await new Promise(r => setTimeout(r, 2000)); // 2s backoff
                            continue;
                        }
                        result[reviewer.name] = { passed: false, issues: ['reviewer timeout (60s) or spawn error'] };
                    }
                    break; // success or exhausted retries
                } catch {
                    if (attempt === 2) {
                        result[reviewer.name] = { passed: false, issues: ['reviewer error'] };
                    }
                }
            }
        }));

        return result;
    }

    /**
     * Meta-cognitive self-audit: scan execution results for "未审视自己" patterns.
     * Detects:
     *   - Steps that failed with REVIEW_FAILED (self-check skipped or failed)
     *   - Steps that required retries (first attempt was wrong → didn't self-verify before acting)
     *   - Steps with cascade-stop (downstream hit an error that upstream should have caught)
     *   - Steps with no artifacts despite being non-trivial (assumed success without verifying output)
     *
     * For each detected pattern, append a seed to ~/.unified-agent-cli/self-audit-seeds.md
     * so the next session can reflect on it.
     */
    async runSelfAudit(steps, results, prompt) {
        const SEEDS_FILE = join(os.homedir(), '.unified-agent-cli', 'self-audit-seeds.md');
        const selfReflectPatterns = [];
        const now = new Date().toISOString().slice(0, 10);

        for (let i = 0; i < results.length; i++) {
            const r = results[i];
            const s = steps[i];

            // Pattern 1: review failed — step was not checked before acting
            if (r.code === 'REVIEW_FAILED') {
                selfReflectPatterns.push(`[${now}] REVIEW_FAILED | step ${i + 1}: ${s.adapterId}:${s.command} | reason: step proceeded without self-check | fix: before executing, ask "am I using the right adapter and args?"`);
            }

            // Pattern 2: required retry — first attempt was wrong
            if ((r.attempts ?? 1) > 1 && r.success) {
                selfReflectPatterns.push(`[${now}] RETRY_SUCCESS | step ${i + 1}: ${s.adapterId}:${s.command} | reason: needed ${r.attempts - 1} retries — first attempt was wrong | fix: before acting, ask "is my first attempt correct? what might be wrong?"`);
            }

            // Pattern 3: cascade-stop — upstream should have caught the error
            if (r.code === 'CASCADE_STOP' && i > 0) {
                selfReflectPatterns.push(`[${now}] CASCADE_STOP | step ${i + 1}: ${s.adapterId}:${s.command} | reason: downstream error indicates upstream didn't validate contract | fix: after each step, ask "what can go wrong downstream?"`);
            }

            // Pattern 4: no artifacts on non-trivial step (command ≠ empty, no output checked)
            if (r.success && r.artifacts.length === 0 && s.command !== '' && s.outputSlots.length > 0 && !r.output) {
                selfReflectPatterns.push(`[${now}] NO_OUTPUT_VERIFY | step ${i + 1}: ${s.adapterId}:${s.command} | reason: produced no artifacts despite declared outputSlots | fix: after execution, ask "did I get the expected output?"`);
            }

            // Pattern 5: null result after retry loop — adapter returned nothing
            if (r.code === 'NULL_RESULT') {
                selfReflectPatterns.push(`[${now}] NULL_RESULT | step ${i + 1}: ${s.adapterId}:${s.command} | reason: adapter returned null after all retries | fix: before acting, ask "is the adapter available and is the args correct?"`);
            }
        }

        if (selfReflectPatterns.length === 0) return;

        // Only write to SEEDS_FILE and trigger auto-seed if patterns >= 3
        if (selfReflectPatterns.length >= 3) {
            mkdirSync(dirname(SEEDS_FILE), { recursive: true });
            const header = `\n## Self-Audit Seeds (${now})\n`;
            const existing = existsSync(SEEDS_FILE) ? readFileSync(SEEDS_FILE, 'utf-8') : '';
            const entry = existing.endsWith(header) ? selfReflectPatterns.map(p => `- ${p}`).join('\n') + '\n' : header + selfReflectPatterns.map(p => `- ${p}`).join('\n') + '\n';
            appendFileSync(SEEDS_FILE, entry, 'utf-8');
            try {
                execSync('node "D:/OpenClaw/workspace/.omc/scripts/hook-auto-seed.mjs" --ingest', {
                    stdio: 'ignore',
                    timeout: 5000
                });
            } catch { /* ignore */ }
        }

        if (this.options.verbose) {
            for (const p of selfReflectPatterns) {
                process.stderr.write(`[self-audit] ${p}\n`);
            }
        }
    }

    async recordAuditLog(runId, steps, results, causalityInfo, prompt) {
        try {
            const dir = join(os.homedir(), '.unified-agent-cli');
            if (!existsSync(dir))
                mkdirSync(dir, { recursive: true });
            const logPath = this.options.auditLogPath ?? join(dir, 'audit.jsonl');
            const timestamp = new Date().toISOString();
            // Write run header entry (prompt stored once)
            appendFileSync(logPath, JSON.stringify({
                runId,
                seq: -1,
                timestamp,
                type: 'run-header',
                prompt: prompt ?? '',
                stepCount: steps.length
            }) + '\n', 'utf-8');

            // Write one AuditLogEntry per step (append-only)
            let seq = 0;
            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                const result = results[i];
                const info = causalityInfo.get(i);
                const entry = {
                    runId,
                    seq: seq++,
                    timestamp,
                    stepIdx: i,
                    adapterId: step.adapterId,
                    adapterType: step.adapterType,
                    command: step.command,
                    args: step.args,
                    inputSlots: step.inputSlots,
                    outputSlots: step.outputSlots,
                    success: result?.success ?? false,
                    error: result?.error ?? null,
                    code: result?.code ?? null,
                    durationMs: result?.durationMs ?? null,
                    attempts: result?.attempts ?? 1,
                    causalityChain: info.chain,
                    parentStepIdx: info.parent,
                    rootStepIdx: info.root,
                    causalityDepth: info.depth,
                    cached: result?.cached ?? false,
                    fatal: result?.fatal ?? false,
                    
                    review: step.review ?? null,
                };
                appendFileSync(logPath, JSON.stringify(entry) + '\n', 'utf-8');
            }
        }
        catch (e) {
            // Silently ignore audit log write failures
            console.error(`[audit] failed to write log: ${e.message}`);
        }
    }
    /** Build causality metadata: chain, parent, root, depth for each step */
    buildCausalityInfo(steps, deps) {
        const info = new Map();
        for (let i = 0; i < steps.length; i++) {
            const stepDeps = deps.get(i) ?? new Set();
            // Parent = direct predecessor (highest index < i that is a dep), or null
            const parent = stepDeps.size > 0 ? Math.max(...Array.from(stepDeps)) : null;
            // Build chain: walk up to root collecting all ancestors
            const chain = [];
            let current = i;
            const visited = new Set();
            while (current !== undefined && !visited.has(current)) {
                visited.add(current);
                const deps_i = deps.get(current) ?? new Set();
                if (deps_i.size === 0)
                    break;
                const maxDep = Math.max(...Array.from(deps_i));
                chain.push(maxDep);
                current = maxDep;
            }
            // Root = first step in chain (has no deps)
            let root = chain.length > 0 ? Math.min(...chain) : i;
            // If no deps, root is self
            if (stepDeps.size === 0)
                root = i;
            info.set(i, { chain, parent, root, depth: chain.length });
        }
        return info;
    }
    persistLogs(runId, results) {
        try {
            const logsDir = join(os.homedir(), '.unified-agent-cli', 'logs', runId);
            mkdirSync(logsDir, { recursive: true });
            for (let i = 0; i < results.length; i++) {
                const r = results[i];
                if (r.logs) {
                    writeFileSync(join(logsDir, `step-${i + 1}.log`), r.logs, 'utf-8');
                }
                if (r.output) {
                    writeFileSync(join(logsDir, `step-${i + 1}.stdout`), r.output, 'utf-8');
                if (r.artifacts && r.artifacts.length > 0) {
                    writeFileSync(join(logsDir, `step-${i + 1}.artifacts.json`), JSON.stringify(r.artifacts, null, 2), 'utf-8');
                }
                }
            }
        }
        catch (e) {
            // Silently ignore log write failures
            console.error(`[persistLogs] failed to write logs: ${e.message}`);
        }
    }
}
