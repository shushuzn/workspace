import { mkdirSync, writeFileSync, readFileSync, rmSync, appendFileSync, existsSync } from 'fs';
import { join } from 'path';
import os from 'os';
import { randomUUID } from 'crypto';
import chalk from 'chalk';
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
    constructor(registry, options = {}) {
        this.registry = registry;
        this.options = options;
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
        // --explain: show layers, parallel groups, and inputSlot wiring
        if (this.options.explain) {
            process.stderr.write(chalk.blue('\n[execution plan]:\n'));
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
                            for (let j = 0; j < idx; j++) {
                                if (steps[j].outputSlots.includes(input)) {
                                    process.stderr.write(`        ${chalk.gray('←')} ${stepColor(steps[j].adapterType)(steps[j].adapterId)}:${chalk.gray(`outputSlots[${input}]`)}\n`);
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
        const resultMap = new Map(); // step index → result
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
                    resultMap.set(stepIdx, timerResult);
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
                    resultMap.set(stepIdx, err);
                    return;
                }
                // Execute with optional timeout + retry logic
                if (this.options.verbose) {
                    process.stderr.write(`[step] ${stepColor(resolvedStep.adapterType)(resolvedStep.adapterId)} ${resolvedStep.command} ${resolvedStep.args.join(' ')}\n`);
                }
                let maxRetries = resolvedStep.maxRetries ?? this.options.maxRetries ?? 3;
                let result = null;
                let attempt = 0;
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
                                resultMap.set(stepIdx, results[stepIdx]);
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
                                    resultMap.set(stepIdx, fallbackResult);
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
                if (!result)
                    throw new Error('Unexpected: result is null after retry loop');
                result.attempts = attempt + (result.success ? 1 : 0);
                result.durationMs = Date.now() - (stepStartTimes.get(stepIdx) ?? Date.now());
                results[stepIdx] = result;
                resultMap.set(stepIdx, result);
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
                if (this.options.cacheTtlMs && result.success && resolvedStep.inputSlots.length === 0) {
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
        return results;
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
        return `${step.adapterId}:${step.command}:${step.args.join(',')}`;
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
    async recordAuditLog(runId, steps, results, causalityInfo, prompt) {
        try {
            const dir = join(os.homedir(), '.unified-agent-cli');
            if (!existsSync(dir))
                mkdirSync(dir, { recursive: true });
            const logPath = this.options.auditLogPath ?? join(dir, 'audit.jsonl');
            const timestamp = new Date().toISOString();
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
                    prompt: prompt ?? '',
                };
                appendFileSync(logPath, JSON.stringify(entry) + '\n', 'utf-8');
            }
        }
        catch {
            // Silently ignore audit log write failures
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
            let root = i;
            for (const c of chain) {
                if (c < root)
                    root = c;
            }
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
                }
            }
        }
        catch {
            // Silently ignore log write failures
        }
    }
}
