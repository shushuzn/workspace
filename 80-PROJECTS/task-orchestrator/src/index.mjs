#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import chokidar from 'chokidar';
import yaml from 'yaml';
import { existsSync, readFileSync, readdirSync, writeFileSync, mkdirSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import { Registry } from './registry.mjs';
import { Planner } from './planner.mjs';
import { Executor } from './executor.mjs';
export { chalk };
export { Planner } from './planner.mjs';
export { Executor } from './executor.mjs';
export { Registry } from './registry.mjs';
export { runMcpServer } from './mcp-server.mjs';
// ── Watch mode persistence ──────────────────────────────────────────────────
const REQUEUE_PATH = join(homedir(), '.unified-agent-cli', 'requeue.json');
function loadRequeue() {
    if (!existsSync(REQUEUE_PATH))
        return { pending: [], completed: [] };
    try {
        return JSON.parse(readFileSync(REQUEUE_PATH, 'utf-8'));
    }
    catch {
        return { pending: [], completed: [] };
    }
}
function saveRequeue(state) {
    mkdirSync(join(homedir(), '.unified-agent-cli'), { recursive: true });
    writeFileSync(REQUEUE_PATH, JSON.stringify(state, null, 2), 'utf-8');
}
/** Compute average duration (ms) for each (adapterId, command) from history.jsonl */
function getAvgDurations() {
    const histPath = join(homedir(), '.unified-agent-cli', 'history.jsonl');
    const out = new Map();
    const tmp = new Map();
    if (!existsSync(histPath))
        return out;
    try {
        const lines = readFileSync(histPath, 'utf-8').split('\n').filter(Boolean);
        for (const line of lines) {
            const rec = JSON.parse(line);
            for (const s of rec.steps ?? []) {
                if (s.durationMs != null) {
                    const key = `${s.adapterId}:${s.command}`;
                    const cur = tmp.get(key) ?? { sum: 0, count: 0 };
                    tmp.set(key, { sum: cur.sum + s.durationMs, count: cur.count + 1 });
                }
            }
        }
    }
    catch { /* ignore */ }
    for (const [key, val] of tmp) {
        out.set(key, Math.round(val.sum / val.count));
    }
    return out;
}
function rulesPath() {
    return join(homedir(), '.unified-agent-cli', 'rules.yaml');
}
function loadUserRulesForEdit() {
    try {
        const path = rulesPath();
        if (!existsSync(path))
            return [];
        const content = readFileSync(path, 'utf-8');
        const parsed = yaml.parse(content);
        if (!parsed || !Array.isArray(parsed.rules))
            return [];
        return parsed.rules;
    }
    catch {
        return [];
    }
}
function saveUserRulesForEdit(rules) {
    const dir = join(homedir(), '.unified-agent-cli');
    mkdirSync(dir, { recursive: true });
    const content = yaml.stringify({ rules });
    writeFileSync(join(dir, 'rules.yaml'), content, 'utf-8');
}
function templatesDir() {
    return join(homedir(), '.unified-agent-cli', 'templates');
}
function loadTemplate(name) {
    const dir = templatesDir();
    const exts = ['.yaml', '.yml', '.json'];
    for (const ext of exts) {
        const path = join(dir, `${name}${ext}`);
        if (existsSync(path)) {
            const content = readFileSync(path, 'utf-8');
            const parsed = yaml.parse(content);
            if (parsed?.steps) {
                return { steps: parsed.steps, description: parsed.description ?? name };
            }
        }
    }
    return null;
}
function listTemplates() {
    const dir = templatesDir();
    if (!existsSync(dir))
        return [];
    const files = readdirSync(dir).filter(f => /\.(yaml|yml|json)$/.test(f));
    const templates = [];
    for (const file of files) {
        const name = file.replace(/\.(yaml|yml|json)$/, '');
        try {
            const content = readFileSync(join(dir, file), 'utf-8');
            const parsed = yaml.parse(content);
            templates.push({ name, description: parsed?.description ?? name });
        }
        catch {
            templates.push({ name, description: name });
        }
    }
    return templates;
}
function scaffoldAdapterTemplate(name) {
    return `import { execa } from 'execa';
import type { Adapter, Step, Context, Result } from './types.mjs';

export class ${name}Adapter implements Adapter {
  id = '${name}';
  type = 'cli-anything' as const;

  canHandle(step: Step): boolean {
    return step.adapterType === 'cli-anything' && step.adapterId === this.id;
  }

  async execute(step: Step, ctx: Context): Promise<Result> {
    try {
      const result = await execa(\`${name}\`, [step.command, ...step.args], {
        cwd: ctx.workingDir,
        env: ctx.env,
        stderr: 'pipe',
      });
      return { success: true, output: result.stdout, logs: result.stderr ?? '', artifacts: [], fatal: false };
    } catch (err: unknown) {
      const error = err instanceof Error ? err.message.slice(0, 200) : String(err);
      return { success: false, output: '', logs: error, artifacts: [], error, fatal: true };
    }
  }

  async checkAvailable(): Promise<boolean> {
    try {
      const { execaCommand } = await import('execa');
      await execaCommand(\`${name} --version\`, { stderr: 'ignore', reject: false });
      return true;
    } catch {
      return false;
    }
  }

  register() {
    return {
      adapterId: this.id,
      keywords: [],  // TODO: add keywords that trigger this adapter
      commands: [],   // TODO: add commands this adapter supports
      outputSlots: [],
      priority: 0,
    };
  }
}
`;
}
async function main() {
    const program = new Command();
    program
        .name('task')
        .description('Chain opencli + CLI-Anything via rule-based task planner')
        .version('0.1.0');
    program
        .argument('[prompt...]', 'Natural language task description')
        .option('--dry-run', 'Parse only, do not execute', false)
        .option('--adapter-check', 'Pre-flight check: verify all adapters are available (implies --dry-run)', false)
        .option('--confirm-steps', 'Confirm before executing each step', false)
        .option('--continue-on-error', 'Continue on recoverable errors', false)
        .option('--cascade-on-error', 'When a step fails fatally, stop all remaining steps in later layers', false)
        .option('--max-parallel <n>', 'Max parallel steps per layer (default: unlimited)', undefined)
        .option('--default-timeout-ms <ms>', 'Global default timeout per step (no default)', undefined)
        .option('--output-dir <path>', 'Directory for artifacts and temp state (default: system temp)', undefined)
        .option('--adapter-dir <path>', 'Extra directory to scan for third-party adapters', undefined)
        .option('--verbose', 'Show step-by-step logs', false)
        .option('--no-review', 'Disable two-stage review gate (spec + code)', false)
        .option('--no-self-audit', 'Disable meta-cognitive self-audit after execution', false)
        .option('--no-pre-audit', 'Disable meta-cognitive pre-audit before execution', false)
        .option('--check', 'Check adapter availability', false)
        .option('--stream-to <port>', 'Start WebSocket server on port and stream step events as JSON Lines to connected clients', undefined)
        .option('--metrics [port]', 'Start Prometheus /metrics server on port (default 9090)', undefined)
        .option('--list', 'List all available adapters', false)
        .option('--watch <dir>', 'Watch a directory for changes and run tasks', undefined)
        .option('--ui', 'Launch browser UI with real-time SVG task chain visualization', false)
        .option('--batch <file>', 'Read prompts from file (one per line) and execute sequentially', undefined)
        .option('--output-format <format>', 'Output format: json (default) or yaml', 'json')
        .option('--dot', 'Output step dependency graph in Graphviz DOT format (implies --dry-run)', false)
        .option('--export-d3 <path>', 'Output {tasks,edges} JSON for D3.js visualization (implies --dry-run)', undefined)
        .option('--script <path>', 'Output executable shell script replaying the plan (implies --dry-run)', undefined)
        .option('--json-schema', 'Output JSON Schema for PlannerOutput and exit', false)
        .option('--edit-rules', 'Interactively edit rules.yaml (add/view/delete rules)', false)
        .option('--scaffold-adapter <name>', 'Scaffold a new adapter named <name> to stdout', undefined)
        .option('--template <name>', 'Run a named template from ~/.unified-agent-cli/templates/', undefined)
        .option('--list-templates', 'List available templates', false)
        .option('--explain', 'Show which keywords matched and why', false).alias('e')
        .option('--status', 'Show adapter health and recent run status', false)
        .option('--env-file <path>', 'Load environment variables from a .env file', undefined)
        .option('--replay <runId>', 'Replay a previous run by runId (use --dry-run to preview)', undefined)
        .option('--step <n>', 'With --replay: start replay from step N (skip first N-1 steps)', undefined)
        .option('--mcp', 'Run as MCP server via stdio protocol', false)
        .option('--export-rules <path>', 'Export current user rules to a YAML file', undefined)
        .option('--chain <file>', 'Execute a YAML task chain file (implies --dry-run)', undefined)
        .option('--json', 'Output pure JSON (no ANSI colors)', false)
        .option('--json-lines', 'Output JSON Lines (one JSON object per step result)', false)
        .option('--import-rules <path>', 'Import rules from a YAML file (merge with existing)', undefined)
        .option('--swarm-id <id>', 'Run as swarm worker: read JSON dispatch from stdin, write JSON result to stdout', undefined)
        .option('--install-template <url>', 'Install a template from a GitHub URL (e.g. owner/repo#branch or full URL)', undefined)
        .option('--search-templates [query]', 'Search GitHub for public workflow templates (optional query)', false)
        .option('--workspace-scripts', 'List all workspace/*.mjs scripts and register them as shell adapters', false)
        .action(async (promptParts, options) => {
        const prompt = promptParts.join(' ');
        // --scaffold-adapter: output a starter adapter .ts file
        if (options.scaffoldAdapter) {
            const name = options.scaffoldAdapter;
            const safeName = name.replace(/[^a-zA-Z0-9_-]/g, '_');
            process.stdout.write(scaffoldAdapterTemplate(safeName));
            return;
        }
        // --swarm-id: swarm worker mode — read structured ISCP dispatch from stdin, write JSON result to stdout
        if (options.swarmId) {
            const { createCoordinatorMessage } = await import('./swarm/protocol-ext.js');
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const sendMsg = (msg) => process.stdout.write(JSON.stringify(msg) + '\n');
            const swarmId = String(options.swarmId);
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const sendResult = (result) => sendMsg(createCoordinatorMessage(`swarm-${swarmId}-${Date.now()}`, { rootId: '', chain: [], depth: 0 }, 'task_result', { result }));
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const sendError = (code, message, recoverable) => sendMsg(createCoordinatorMessage(`swarm-${swarmId}-${Date.now()}`, { rootId: '', chain: [], depth: 0 }, 'error_result', { error: { code, message, recoverable, source: `task-orchestrator:${swarmId}` } }));
            // Register stdin handler for ISCP messages
            const stdin = process.stdin;
            let buf = '';
            stdin.on('data', async (chunk) => {
                buf += chunk.toString();
                let newline;
                while ((newline = buf.indexOf('\n')) !== -1) {
                    const line = buf.slice(0, newline);
                    buf = buf.slice(newline + 1);
                    if (!line.trim())
                        continue;
                    // eslint-disable-next-line @typescript-eslint/no-explicit-any
                    let msg;
                    try {
                        msg = JSON.parse(line);
                    }
                    catch {
                        continue;
                    }
                    if (msg.type !== 'task_dispatch') {
                        if (msg.correlationId) {
                            sendMsg(createCoordinatorMessage(msg.correlationId, msg.lineage ?? { rootId: '', chain: [], depth: 0 }, 'ack', { ack: { taskId: '', accepted: false } }));
                        }
                        continue;
                    }
                    const dispatch = msg.payload?.task;
                    if (!dispatch) {
                        sendError('PROTOCOL_ERROR', 'No task in dispatch', false);
                        continue;
                    }
                    const taskId = dispatch.taskId;
                    const lineage = msg.lineage ?? { rootId: taskId, chain: [], depth: 0 };
                    try {
                        sendMsg(createCoordinatorMessage(msg.correlationId, lineage, 'ack', { ack: { taskId, accepted: true } }));
                        let steps;
                        if (dispatch.steps?.length) {
                            steps = dispatch.steps.map((s) => ({
                                adapterId: '', adapterType: s.adapterType, command: s.command,
                                args: s.args, inputSlots: s.inputSlots, outputSlots: s.outputSlots, timeoutMs: s.timeoutMs,
                            }));
                        }
                        else {
                            const planner = new Planner(registry);
                            const parsed = planner.parse(dispatch.prompt);
                            if (parsed.errors.length > 0 && parsed.steps.length === 0) {
                                sendResult({ taskId, success: false, output: '', artifacts: [], error: { code: 'STEP_FAILED', message: parsed.errors.join('; '), recoverable: false, source: `task-orchestrator:${swarmId}` } });
                                continue;
                            }
                            steps = parsed.steps;
                        }
                        const executor = new Executor(registry, { continueOnError: true, verbose: false });
                        const results = await executor.execute(steps, { prompt: dispatch.prompt });
                        const allSuccess = results.every(r => r.success);
                        sendResult({
                            taskId,
                            success: allSuccess,
                            output: results.map(r => r.output).join('\n---\n'),
                            artifacts: results.flatMap(r => r.artifacts.map(a => ({ ...a, slot: '', type: a.type }))),
                            error: allSuccess ? undefined : { code: 'STEP_FAILED', message: results.find(r => !r.success)?.error ?? 'Unknown', recoverable: true, source: `task-orchestrator:${swarmId}` },
                        });
                    }
                    catch (err) {
                        const m = err instanceof Error ? err.message : String(err);
                        sendError('INTERNAL_ERROR', m, false);
                    }
                }
            });
            sendMsg(createCoordinatorMessage(`swarm-${swarmId}-ready`, { rootId: '', chain: [], depth: 0 }, 'ack', { ack: { taskId: '', accepted: true } }));
            return;
        }
        // --list-templates: show all available templates
        if (options.listTemplates) {
            const templates = listTemplates();
            if (templates.length === 0) {
                console.log(chalk.yellow('No templates found. Create ~/.unified-agent-cli/templates/<name>.yaml with steps array.'));
            }
            else {
                console.log(chalk.blue(`Templates (${templates.length}):`));
                for (const t of templates) {
                    console.log(`  ${chalk.green(t.name.padEnd(24))} ${t.description}`);
                }
                console.log(chalk.gray(`\n  Templates dir: ${templatesDir()}`));
            }
            return;
        }
        // --template: run a named template
        if (options.template) {
            const tmpl = loadTemplate(options.template);
            if (!tmpl) {
                console.error(chalk.red(`Template not found: ${options.template}`));
                console.error(chalk.gray(`Create ~/.unified-agent-cli/templates/${options.template}.yaml`));
                process.exit(1);
            }
            const registry = new Registry({ adapterDirs: options.adapterDir ? [options.adapterDir] : [] });
            await registry.load();
            const exec = new Executor(registry, { verbose: true });
            const results = await exec.execute(tmpl.steps, { prompt: `template:${options.template}` });
            const failures = results.filter(r => !r.success);
            console.log(chalk.blue(`\n${results.length - failures.length}/${results.length} steps succeeded`));
            for (const r of results) {
                if (r.success && r.output) {
                    console.log(chalk.gray('  output:'), r.output.slice(0, 500));
                }
                if (!r.success) {
                    console.error(chalk.red(`  ✗ ${r.error}`));
                }
            }
            if (failures.length > 0) {
                process.exit(1);
            }
            return;
        }
        // --search-templates: search GitHub for workflow templates
        if (options.searchTemplates) {
            const { execSync } = await import('child_process');
            const query = encodeURIComponent((options.searchTemplates === true ? 'task-orchestrator workflow yaml' : String(options.searchTemplates)));
            const url = `https://api.github.com/search/code?q=${query}+extension:yaml+extension:yml&per_page=10`;
            try {
                const result = execSync(`curl -s -H "Accept: application/vnd.github.v3+json" "${url}"`, { timeout: 15000 });
                const data = JSON.parse(result.toString());
                const items = data.items || [];
                if (items.length === 0) {
                    console.log(chalk.yellow('No templates found.'));
                }
                else {
                    console.log(chalk.blue(`Found ${items.length} template(s):`));
                    for (const item of items) {
                        const repo = item.repository?.full_name || 'unknown';
                        const path = item.path || '';
                        console.log(`  ${chalk.green(repo)}/${path}`);
                    }
                }
            }
            catch (e) {
                console.error(chalk.red('GitHub search failed:', e.message));
            }
            return;
        }
        // --install-template: install a template from GitHub URL
        if (options.installTemplate) {
            const { execSync } = await import('child_process');
            const url = String(options.installTemplate);
            const templatesPath = templatesDir();
            mkdirSync(templatesPath, { recursive: true });
            let gitUrl = url;
            let branch = 'main';
            if (url.includes('#')) {
                const [u, b] = url.split('#');
                gitUrl = u;
                branch = b;
            }
            else if (url.includes('github.com') && !url.endsWith('.yaml') && !url.endsWith('.yml')) {
                gitUrl = url;
            }
            // owner/repo → github.com/owner/repo
            if (!gitUrl.includes('github.com') && gitUrl.includes('/')) {
                gitUrl = `https://github.com/${gitUrl}`;
            }
            // Extract owner/repo for dir name
            const match = gitUrl.match(/github\.com\/([^/]+\/[^/]+)/);
            const repoName = match ? match[1].replace('/', '-') : `template-${Date.now()}`;
            const destDir = join(templatesPath, repoName);
            console.log(chalk.blue(`Installing template from ${gitUrl} (branch: ${branch})...`));
            try {
                execSync(`git clone --depth 1 -b ${branch} ${gitUrl} "${destDir}"`, { stdio: 'pipe', timeout: 60000 });
                // Find .yaml/.yml files and copy to templates root
                const { readdirSync, readFileSync, writeFileSync, cpSync } = await import('fs');
                const yamlFiles = readdirSync(destDir).filter(f => /\.(yaml|yml)$/.test(f));
                if (yamlFiles.length === 0) {
                    console.log(chalk.yellow('No .yaml/.yml files found in repo.'));
                }
                else {
                    for (const f of yamlFiles) {
                        const src = join(destDir, f);
                        const dst = join(templatesPath, `${repoName}-${f}`);
                        cpSync(src, dst);
                        console.log(chalk.green(`  Installed: ${repoName}-${f}`));
                    }
                }
                console.log(chalk.green(`\nTemplate installed! Run with: task --template <name>`));
            }
            catch (e) {
                console.error(chalk.red('Install failed:', e.message));
            }
            return;
        }
        // --workspace-scripts: scan workspace scripts and register as shell adapters
        if (options.workspaceScripts) {
            const scriptsDir = 'D:/OpenClaw/workspace/scripts';
            const files = readdirSync(scriptsDir).filter(f => /\.(mjs|js)$/.test(f));
            if (files.length === 0) {
                console.log(chalk.yellow('No scripts found.'));
                return;
            }
            console.log(chalk.blue(`Workspace scripts (${files.length}):`));
            for (const f of files.sort()) {
                const name = f.replace(/\.(mjs|js)$/, '');
                console.log(`  ${chalk.green(name.padEnd(40))} → shell:${name}`);
            }
            console.log(chalk.gray(`\nUsage: task -- shell:${name} [args]`));
            return;
        }
        const registry = new Registry({
            adapterDirs: options.adapterDir ? [options.adapterDir] : [],
        });
        await registry.load();
        // --export-rules: dump current rules.yaml to a file
        if (options.exportRules) {
            const rules = loadUserRulesForEdit();
            const yamlContent = yaml.stringify({ rules });
            if (options.exportRules === '-') {
                process.stdout.write(yamlContent);
            }
            else {
                writeFileSync(options.exportRules, yamlContent, 'utf-8');
                console.log(chalk.green(`Exported ${rules.length} rule(s) to ${options.exportRules}`));
            }
            return;
        }
        // --export-plan: parse and export plan as YAML (implies --dry-run)
        if (options.exportPlan) {
            const planner = new Planner(registry);
            const { steps } = planner.parse(prompt);
            const yamlContent = yaml.stringify({ name: 'exported-plan', steps });
            if (options.exportPlan === '-') {
                process.stdout.write(yamlContent);
            }
            else {
                writeFileSync(options.exportPlan, yamlContent, 'utf-8');
                console.log(chalk.green(`Exported ${steps.length} step(s) to ${options.exportPlan}`));
            }
            return;
        }
        // --import-rules: merge rules from a file into rules.yaml
        if (options.importRules) {
            const imported = yaml.parse(readFileSync(options.importRules, 'utf-8'));
            if (!imported || !Array.isArray(imported.rules)) {
                console.error(chalk.red(`Invalid rules file: ${options.importRules}`));
                process.exit(1);
            }
            const existing = loadUserRulesForEdit();
            const merged = [...existing, ...imported.rules];
            saveUserRulesForEdit(merged);
            console.log(chalk.green(`Imported ${imported.rules.length} rule(s), ${merged.length} total.`));
            return;
        }
        // --mcp: run as MCP server via stdio
        if (options.mcp) {
            const { runMcpServer } = await import('./mcp-server.js');
            await runMcpServer();
            return;
        }
        // --watch: directory watch mode
        if (options.watch) {
            const watchDir = options.watch;
            const planner = new Planner(registry);
            console.log(chalk.blue(`Watching ${watchDir} for changes...`));
            let debounceTimer = null;
            const pendingFiles = [];
            const processedFiles = [];
            const run = async (filePath) => {
                if (debounceTimer)
                    clearTimeout(debounceTimer);
                debounceTimer = setTimeout(async () => {
                    console.log(chalk.yellow(`\nChange detected: ${filePath}`));
                    const { steps, errors } = planner.parse(`process ${filePath}`);
                    if (steps.length === 0) {
                        console.log(chalk.gray('  No matching rules, skipping.'));
                        return;
                    }
                    if (options.dryRun) {
                        console.log(chalk.blue(`  [dry-run] Would execute ${steps.length} step(s):`));
                        for (let i = 0; i < steps.length; i++) {
                            const step = steps[i];
                            const argsStr = step.args.length > 0 ? ` ${step.args.join(' ')}` : '';
                            console.log(`    ${chalk.yellow(`${i + 1}.`)} ${chalk.green(step.adapterId)}: ${step.command}${argsStr}`);
                        }
                        // Validate adapters in watch mode too
                        for (let i = 0; i < steps.length; i++) {
                            const step = steps[i];
                            const candidates = await registry.findAdapters(step);
                            if (candidates.length === 0) {
                                console.log(chalk.red(`  Error: step ${i + 1} — no adapter handles "${step.adapterId}"`));
                            }
                            else {
                                const available = await Promise.all(candidates.map(a => a.checkAvailable()));
                                if (!available.some(Boolean)) {
                                    console.log(chalk.red(`  Error: step ${i + 1} — ${step.adapterId} not available`));
                                }
                            }
                        }
                        // Validate inputSlots: each step's inputSlots must be produced by a prior step
                        let hasSlotError = false;
                        for (let i = 0; i < steps.length; i++) {
                            for (const slot of steps[i].inputSlots) {
                                let found = false;
                                for (let j = 0; j < i; j++) {
                                    if (steps[j].outputSlots.includes(slot)) {
                                        found = true;
                                        break;
                                    }
                                }
                                if (!found) {
                                    console.log(chalk.red(`  Error: step ${i + 1} — missing slot "${slot}" (no prior step produces it)`));
                                    hasSlotError = true;
                                }
                            }
                        }
                        if (hasSlotError) {
                            process.exit(1);
                        }
                    }
                    else {
                        const executor = new Executor(registry, { verbose: true });
                        await executor.execute(steps);
                        processedFiles.push(filePath);
                        pendingFiles.push(filePath);
                        saveRequeue({ pending: pendingFiles.filter(f => !processedFiles.includes(f)), completed: processedFiles });
                    }
                }, 500);
            };
            const watcher = chokidar.watch(watchDir, { persistent: true, ignoreInitial: true });
            watcher
                .on('add', (path) => run(path))
                .on('change', (path) => run(path))
                .on('error', (err) => console.error(chalk.red(`Watch error: ${err instanceof Error ? err.message : String(err)}`)));
            // Watch mode persistence
            const { pending } = loadRequeue();
            // Replay pending tasks from previous session
            if (pending.length > 0) {
                console.log(chalk.blue(`Replaying ${pending.length} pending task(s) from previous session...`));
                for (const filePath of pending) {
                    if (existsSync(filePath)) {
                        await run(filePath);
                    }
                }
            }
            // Graceful exit on SIGINT/SIGTERM
            let exiting = false;
            const exit = async () => {
                if (exiting)
                    return;
                exiting = true;
                console.log(chalk.blue('\nShutting down watcher... saving state...'));
                saveRequeue({ pending: [], completed: [] });
                await watcher.close();
                process.exit(0);
            };
            process.on('SIGINT', exit);
            process.on('SIGTERM', exit);
            // Keep process alive until signaled
            await new Promise(() => { });
        }
        // --ui: browser-based SVG task chain visualization
        if (options.ui) {
            const http = await import('http');
            const planner = new Planner(registry);
            const executor = new Executor(registry);
            const SVG_WIDTH = 900;
            const LAYER_GAP = 160;
            const NODE_GAP = 80;
            const NODE_W = 140;
            const NODE_H = 50;
            const PADDING = 40;
            let currentSteps = [];
            let currentResults = [];
            let currentPrompt = '';
            const buildSvg = () => {
                if (currentSteps.length === 0) {
                    return `<svg xmlns="http://www.w3.org/2000/svg" width="${SVG_WIDTH}" height="120"><text x="450" y="60" text-anchor="middle" fill="#666" font-family="sans-serif" font-size="14">No task running — use --ui with --chain or --watch</text></svg>`;
                }
                // Group steps by rough depth for visualization
                const layerOf = new Array(currentSteps.length).fill(0);
                for (let i = 0; i < currentSteps.length; i++) {
                    layerOf[i] = Math.floor(i / Math.max(1, Math.ceil(currentSteps.length / 4)));
                }
                const maxLayer = Math.max(...layerOf);
                const svgHeight = PADDING * 2 + (maxLayer + 1) * LAYER_GAP + NODE_H;
                let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${SVG_WIDTH}" height="${svgHeight}">`;
                svg += `<style>
            .node rect { fill: #1a1a2e; stroke: #4a4a6a; stroke-width: 2; rx: 8 }
            .node text { fill: #e0e0e0; font-family: monospace; font-size: 12px; }
            .node.pending rect { fill: #2d2d44; stroke: #6a6a9a; }
            .node.running rect { fill: #1a3a5c; stroke: #4a9fff; stroke-width: 3; }
            .node.success rect { fill: #1a3a2e; stroke: #4aff8a; }
            .node.error rect { fill: #3a1a1a; stroke: #ff4a4a; }
            .edge { stroke: #4a4a6a; stroke-width: 1.5; fill: none; }
            .edge.active { stroke: #4a9fff; stroke-width: 2; }
          </style>`;
                // Draw layers
                const layerNodes = new Map();
                for (let i = 0; i < currentSteps.length; i++) {
                    const l = layerOf[i];
                    if (!layerNodes.has(l))
                        layerNodes.set(l, []);
                    layerNodes.get(l).push(i);
                }
                for (const [layer, indices] of [...layerNodes.entries()].sort((a, b) => a[0] - b[0])) {
                    const layerX = PADDING + layer * LAYER_GAP;
                    const totalH = indices.length * NODE_GAP;
                    let startY = PADDING + (svgHeight - totalH) / 2;
                    for (const idx of indices) {
                        const step = currentSteps[idx];
                        const result = currentResults[idx];
                        const y = startY;
                        const color = !result ? 'pending' : result.success ? 'success' : 'error';
                        const label = `${step.adapterId}: ${step.command}`.substring(0, 18);
                        svg += `<g class="node ${color}" transform="translate(${layerX}, ${y})">
                <rect width="${NODE_W}" height="${NODE_H}"/>
                <text x="70" y="20" text-anchor="middle">${label}</text>
                <text x="70" y="36" text-anchor="middle" font-size="10" fill="#888">${step.args.join(' ') || '—'}</text>
                ${result ? `<text x="70" y="${NODE_H - 6}" text-anchor="middle" font-size="10" fill="${result.success ? '#4aff8a' : '#ff4a4a'}">${result.success ? '✓' : '✗'}</text>` : ''}
              </g>`;
                        startY += NODE_GAP;
                    }
                }
                svg += '</svg>';
                return svg;
            };
            const HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Task Chain</title>
<style>
  body { margin: 0; background: #0d0d1a; color: #e0e0e0; font-family: monospace; }
  #header { padding: 16px 24px; border-bottom: 1px solid #2a2a4a; display: flex; gap: 24px; align-items: center; }
  #prompt { color: #4a9fff; font-size: 13px; flex: 1; }
  #svg-container { padding: 24px; }
  #status { padding: 8px 24px; font-size: 12px; color: #666; }
  #prompt-input { margin: 16px 24px; display: flex; gap: 8px; }
  #prompt-input input { flex: 1; background: #1a1a2e; border: 1px solid #3a3a5a; color: #e0e0e0; padding: 8px 12px; border-radius: 4px; font-family: monospace; }
  #prompt-input button { background: #4a9fff; border: none; color: #fff; padding: 8px 16px; border-radius: 4px; cursor: pointer; }
  svg { display: block; margin: 0 auto; background: #111122; border-radius: 8px; }
</style>
</head>
<body>
<div id="header">
  <span style="color:#4a9fff;font-size:16px;font-weight:bold">Task Chain UI</span>
  <span id="prompt">${currentPrompt || 'ready'}</span>
</div>
<div id="svg-container">${buildSvg()}</div>

<form id="prompt-input">
  <input name="prompt" placeholder="Enter a task prompt..." autofocus/>
  <button type="submit">Run</button>
</form>
<script>
let steps = [], results = [];
async function refresh() {
  const r = await fetch('/state').then(r=>r.json());
  steps = r.steps || [];
  results = r.results || [];
  document.getElementById('svg-container').innerHTML = r.svg;
  document.getElementById('prompt').textContent = r.prompt || '';
}
document.getElementById('prompt-input').onsubmit = async (e) => {
  e.preventDefault();
  const p = e.target.prompt.value;
  await fetch('/run?prompt=' + encodeURIComponent(p));
  e.target.reset();
  await refresh();
};
setInterval(refresh, 1000);
</script>
</body>
</html>`;
            const state = { steps: [], results: [], prompt: '' };
            const server = http.createServer(async (req, res) => {
                const url = new URL(req.url, 'http://localhost:8000');
                res.setHeader('Access-Control-Allow-Origin', '*');
                res.setHeader('Content-Type', 'text/html');
                if (url.pathname === '/') {
                    res.end(HTML);
                }
                else if (url.pathname === '/state') {
                    res.setHeader('Content-Type', 'application/json');
                    const layerOf = new Array(currentSteps.length).fill(0);
                    for (let i = 0; i < currentSteps.length; i++) {
                        layerOf[i] = Math.floor(i / Math.max(1, Math.ceil(currentSteps.length / 4)));
                    }
                    const maxLayer = Math.max(1, ...layerOf);
                    const svgHeight = PADDING * 2 + (maxLayer + 1) * LAYER_GAP + NODE_H;
                    let svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${SVG_WIDTH}" height="${svgHeight}">`;
                    svg += `<style>
              .node rect { fill: #1a1a2e; stroke: #4a4a6a; stroke-width: 2; rx: 8 }
              .node text { fill: #e0e0e0; font-family: monospace; font-size: 12px; }
              .node.pending rect { fill: #2d2d44; stroke: #6a6a9a; }
              .node.running rect { fill: #1a3a5c; stroke: #4a9fff; stroke-width: 3; }
              .node.success rect { fill: #1a3a2e; stroke: #4aff8a; }
              .node.error rect { fill: #3a1a1a; stroke: #ff4a4a; }
              .edge { stroke: #4a4a6a; stroke-width: 1.5; fill: none; }
            </style>`;
                    const layerNodes = new Map();
                    for (let i = 0; i < currentSteps.length; i++) {
                        const l = layerOf[i];
                        if (!layerNodes.has(l))
                            layerNodes.set(l, []);
                        layerNodes.get(l).push(i);
                    }
                    for (const [layer, indices] of [...layerNodes.entries()].sort((a, b) => a[0] - b[0])) {
                        const layerX = PADDING + layer * LAYER_GAP;
                        const totalH = indices.length * NODE_GAP;
                        let startY = PADDING + (svgHeight - totalH) / 2;
                        for (const idx of indices) {
                            const step = currentSteps[idx];
                            const result = currentResults[idx];
                            const y = startY;
                            const color = !result ? 'pending' : result.success ? 'success' : 'error';
                            const label = `${step.adapterId}: ${step.command}`.substring(0, 18);
                            svg += `<g class="node ${color}" transform="translate(${layerX}, ${y})">
                  <rect width="${NODE_W}" height="${NODE_H}"/>
                  <text x="70" y="20" text-anchor="middle">${label}</text>
                  <text x="70" y="36" text-anchor="middle" font-size="10" fill="#888">${step.args.join(' ') || '—'}</text>
                  ${result ? `<text x="70" y="${NODE_H - 6}" text-anchor="middle" font-size="10" fill="${result.success ? '#4aff8a' : '#ff4a4a'}">${result.success ? '✓' : '✗'}</text>` : ''}
                </g>`;
                            startY += NODE_GAP;
                        }
                    }
                    svg += '</svg>';
                    res.end(JSON.stringify({ steps: currentSteps, results: currentResults, prompt: currentPrompt, svg }));
                }
                else if (url.pathname === '/adapters') {
                    res.setHeader('Content-Type', 'application/json');
                    const registrations = registry.getRegistrations();
                    res.end(JSON.stringify({ adapters: registrations }));
                }
                else if (url.pathname.startsWith('/adapters/')) {
                    res.setHeader('Content-Type', 'application/json');
                    const id = url.pathname.slice('/adapters/'.length);
                    const registrations = registry.getRegistrations();
                    const reg = registrations.find(r => r.adapterId === id);
                    if (reg) {
                        res.end(JSON.stringify(reg));
                    }
                    else {
                        res.statusCode = 404;
                        res.end(JSON.stringify({ error: `Adapter not found: ${id}` }));
                    }
                }
                else if (url.pathname.startsWith('/run')) {
                    const p = url.searchParams.get('prompt') ?? '';
                    currentPrompt = p;
                    const { steps: parsedSteps } = planner.parse(p);
                    currentSteps = parsedSteps;
                    currentResults = new Array(currentSteps.length).fill(null);
                    if (currentSteps.length > 0) {
                        const results = await executor.execute(currentSteps);
                        currentResults = results.map(r => ({ success: r.success, error: r.error }));
                    }
                    res.end('ok');
                }
                else {
                    res.statusCode = 404;
                    res.end();
                }
            });
            server.listen(8080, () => {
                console.log(chalk.blue('Task Chain UI: http://localhost:8080'));
            });
            return;
        }
        // --chain: execute a YAML task chain file (local path or https:// URL)
        if (options.chain) {
            const yaml = await import('yaml');
            const { readFileSync, existsSync } = await import('fs');
            let content;
            if (/^https?:\/\//.test(options.chain)) {
                // Remote URL — fetch and parse
                try {
                    const res = await fetch(options.chain);
                    if (!res.ok)
                        throw new Error(`HTTP ${res.status}`);
                    content = await res.text();
                    console.log(chalk.blue(`Chain: fetched ${options.chain}`));
                }
                catch (err) {
                    console.error(chalk.red(`Failed to fetch chain from ${options.chain}: ${err instanceof Error ? err.message : String(err)}`));
                    process.exit(1);
                }
            }
            else {
                // Local file
                if (!existsSync(options.chain)) {
                    console.error(chalk.red(`Chain file not found: ${options.chain}`));
                    process.exit(1);
                }
                content = readFileSync(options.chain, 'utf-8');
            }
            const chain = yaml.parse(content);
            if (!chain || !Array.isArray(chain.steps)) {
                console.error(chalk.red('Invalid chain file: missing "steps" array'));
                process.exit(1);
            }
            const steps = chain.steps.map((s) => ({
                adapterId: s.adapter ?? s.adapterId ?? 'unknown',
                adapterType: (s.adapterType ?? 'cli-anything'),
                command: s.command ?? '',
                args: Array.isArray(s.args) ? s.args : [],
                inputSlots: Array.isArray(s.inputSlots) ? s.inputSlots : [],
                outputSlots: Array.isArray(s.outputSlots) ? s.outputSlots : [],
                timeoutMs: s.timeoutMs,
            }));
            console.log(chalk.blue(`Chain mode: ${steps.length} step(s) from ${options.chain}`));
            const executor = new Executor(registry, {
                continueOnError: options.continueOnError,
                maxRetries: Number(options.maxRetries),
                verbose: options.verbose,
                maxParallel: options.maxParallel ? Number(options.maxParallel) : undefined,
            });
            const results = await executor.execute(steps, { prompt: chain.prompt ?? '' });
            const failures = results.filter(r => !r.success);
            if (failures.length > 0) {
                console.log(chalk.red(`  ${failures.length} step(s) failed:`));
                for (const f of failures)
                    console.log(chalk.red(`    - ${f.error}`));
            }
            else {
                console.log(chalk.green('All steps completed successfully.'));
            }
            return;
        }
        // --batch: read prompts from file and execute sequentially
        if (options.batch) {
            const { readFileSync } = await import('fs');
            const prompts = readFileSync(options.batch, 'utf-8').split('\n').filter(l => l.trim());
            console.log(chalk.blue(`Batch mode: ${prompts.length} prompt(s) from ${options.batch}`));
            for (let i = 0; i < prompts.length; i++) {
                const prompt = prompts[i];
                console.log(chalk.blue(`\n[${i + 1}/${prompts.length}] ${prompt}`));
                const planner = new Planner(registry);
                const { steps, errors } = planner.parse(prompt);
                if (steps.length === 0) {
                    console.log(chalk.yellow(`  No matching rules, skipping.`));
                    continue;
                }
                const executor = new Executor(registry, {
                    continueOnError: options.continueOnError,
                    maxRetries: Number(options.maxRetries),
                    verbose: options.verbose,
                    maxParallel: options.maxParallel ? Number(options.maxParallel) : undefined,
                });
                const results = await executor.execute(steps, { prompt });
                const failures = results.filter(r => !r.success);
                if (failures.length > 0) {
                    console.log(chalk.red(`  ${failures.length} step(s) failed:`));
                    for (const f of failures)
                        console.log(chalk.red(`    - ${f.error}`));
                    if (!options.continueOnError) {
                        console.log(chalk.red('Aborting batch due to failure.'));
                        process.exit(1);
                    }
                }
            }
            console.log(chalk.blue('\nBatch complete.'));
            return;
        }
        // --check: adapter availability
        if (options.check) {
            console.log(chalk.blue('Checking adapters...'));
            for (const adapter of registry.list()) {
                const available = await adapter.checkAvailable();
                const status = available ? chalk.green('✓') : chalk.red('✗');
                console.log(`${status} ${adapter.id}`);
            }
            return;
        }
        // --json-schema: output PlannerOutput JSON Schema and exit
        if (options.jsonSchema) {
            const schema = {
                $schema: 'https://json-schema.org/draft/2020-12/schema',
                title: 'PlannerOutput',
                description: 'Output of the rule-based task planner',
                type: 'object',
                properties: {
                    steps: {
                        type: 'array',
                        items: {
                            type: 'object',
                            properties: {
                                adapterId: { type: 'string' },
                                adapterType: { type: 'string', enum: ['opencli', 'cli-anything', 'multi-agent-hub'] },
                                command: { type: 'string' },
                                args: { type: 'array', items: { type: 'string' } },
                                inputSlots: { type: 'array', items: { type: 'string' } },
                                outputSlots: { type: 'array', items: { type: 'string' } },
                                timeoutMs: { type: 'number' },
                            },
                            required: ['adapterId', 'adapterType', 'command', 'args', 'inputSlots', 'outputSlots'],
                        },
                    },
                    errors: { type: 'array', items: { type: 'string' } },
                },
                required: ['steps', 'errors'],
            };
            process.stdout.write(JSON.stringify(schema, null, 2) + '\n');
            return;
        }
        // --edit-rules: interactive rules editor
        if (options.editRules) {
            const rules = loadUserRulesForEdit();
            const rl = (await import('readline')).createInterface({ input: process.stdin, output: process.stdout });
            const q = (text) => new Promise(resolve => rl.question(text, resolve));
            console.log(chalk.blue('rules.yaml Editor'));
            console.log('Loaded rules:', rules.length);
            for (let i = 0; i < rules.length; i++) {
                const r = rules[i];
                console.log(`  [${i}] ${r.keywords.join(', ')} → ${r.adapterId}: ${r.command}`);
            }
            console.log('\nActions: add, delete <index>, quit');
            const action = await q(chalk.bold('Action: '));
            if (action === 'add') {
                const keywordsRaw = await q('Keywords (comma-separated): ');
                const adapterId = await q('Adapter ID: ');
                const command = await q('Command: ');
                const outputSlotsRaw = await q('Output slots (comma-separated, optional): ');
                const newRule = {
                    keywords: keywordsRaw.split(',').map(s => s.trim()).filter(Boolean),
                    adapterId: adapterId.trim(),
                    adapterType: (adapterId.startsWith('opencli-') ? 'opencli' : adapterId.startsWith('multi-agent-hub') ? 'multi-agent-hub' : 'cli-anything'),
                    command: command.trim(),
                    outputSlots: outputSlotsRaw ? outputSlotsRaw.split(',').map(s => s.trim()).filter(Boolean) : [],
                };
                rules.push(newRule);
                saveUserRulesForEdit(rules);
                console.log(chalk.green('Rule added.'));
            }
            else if (action.startsWith('delete ')) {
                const idx = parseInt(action.split(' ')[1], 10);
                if (!isNaN(idx) && idx >= 0 && idx < rules.length) {
                    const removed = rules.splice(idx, 1)[0];
                    saveUserRulesForEdit(rules);
                    console.log(chalk.green(`Deleted: ${removed.keywords.join(', ')}`));
                }
                else {
                    console.log(chalk.red('Invalid index.'));
                }
            }
            rl.close();
            return;
        }
        // --list: show adapters
        if (options.list) {
            console.log(chalk.blue('Available adapters:'));
            for (const adapter of registry.list()) {
                console.log(`  - ${chalk.green(adapter.id)} [${adapter.type}]`);
                if (options.verbose) {
                    const knownCommands = {
                        'opencli': ['operate open', 'operate screenshot', 'operate click', 'operate type', 'operate eval', 'operate network'],
                        'cli-anything-obs': ['record', 'export'],
                        'cli-anything-blender': ['render'],
                        'cli-anything-gimp': ['export'],
                    };
                    const cmds = knownCommands[adapter.id] ?? [];
                    for (const cmd of cmds) {
                        console.log(`      ${chalk.gray('→')} ${cmd}`);
                    }
                }
            }
            // Show usage stats from history if verbose
            if (options.verbose) {
                try {
                    const histPath = join(homedir(), '.unified-agent-cli', 'history.jsonl');
                    if (existsSync(histPath)) {
                        const lines = readFileSync(histPath, 'utf-8').split('\n').filter(Boolean);
                        const stats = {};
                        for (const line of lines) {
                            try {
                                const rec = JSON.parse(line);
                                for (const step of rec.steps ?? []) {
                                    const key = step.adapterId;
                                    if (!stats[key])
                                        stats[key] = { success: 0, fail: 0 };
                                    if (step.success)
                                        stats[key].success++;
                                    else
                                        stats[key].fail++;
                                }
                            }
                            catch { /* skip malformed lines */ }
                        }
                        const histStats = Object.entries(stats);
                        if (histStats.length > 0) {
                            console.log(chalk.blue('\nUsage stats (from history):'));
                            for (const [id, { success, fail }] of histStats) {
                                console.log(`  ${chalk.green(id)}: ${success} success, ${fail} fail`);
                            }
                        }
                    }
                }
                catch { /* ignore stats errors */ }
            }
            return;
        }
        // --status: show adapter health and recent run status
        if (options.status) {
            console.log(chalk.blue('Adapter health:'));
            const adapters = registry.list();
            for (const adapter of adapters) {
                const available = await adapter.checkAvailable();
                console.log(`  ${available ? chalk.green('●') : chalk.red('○')} ${chalk.green(adapter.id)} [${adapter.type}]`);
            }
            const histPath = join(homedir(), '.unified-agent-cli', 'history.jsonl');
            if (existsSync(histPath)) {
                const lines = readFileSync(histPath, 'utf-8').split('\n').filter(Boolean).slice(-10);
                const stats = {};
                for (const line of lines) {
                    try {
                        const rec = JSON.parse(line);
                        for (const step of rec.steps ?? []) {
                            if (!stats[step.adapterId])
                                stats[step.adapterId] = { success: 0, fail: 0 };
                            if (step.success)
                                stats[step.adapterId].success++;
                            else
                                stats[step.adapterId].fail++;
                        }
                    }
                    catch { /* skip */ }
                }
                const entries = Object.entries(stats);
                if (entries.length > 0) {
                    console.log(chalk.blue('\nRecent stats (last 10 runs):'));
                    for (const [id, { success, fail }] of entries) {
                        const pct = success + fail > 0 ? Math.round((success / (success + fail)) * 100) : 0;
                        console.log(`  ${chalk.green(id)}: ${success} ok, ${fail} fail (${pct}% ok)`);
                    }
                }
            }
            else {
                console.log(chalk.gray('\nNo history found.'));
            }
            return;
        }
        // --replay: replay a previous run by runId
        if (options.replay) {
            const histPath = join(homedir(), '.unified-agent-cli', 'history.jsonl');
            if (!existsSync(histPath)) {
                console.log(chalk.red('No history found. Run a task first.'));
                return;
            }
            const runId = options.replay;
            const lines = readFileSync(histPath, 'utf-8').split('\n').filter(Boolean);
            let targetRecord = null;
            for (const line of lines) {
                try {
                    const rec = JSON.parse(line);
                    if (rec.runId === runId) {
                        targetRecord = rec;
                        break;
                    }
                }
                catch { /* skip */ }
            }
            if (!targetRecord) {
                console.log(chalk.red(`Run not found: ${runId}`));
                console.log(chalk.gray('Hint: use --list --verbose to see recent runIds'));
                return;
            }
            console.log(chalk.blue(`Replaying run ${runId} from ${targetRecord.timestamp}`));
            console.log(chalk.gray(`Original prompt: ${targetRecord.prompt}`));
            const planner = new Planner(registry);
            const { steps, errors } = planner.parse(targetRecord.prompt);
            if (errors.length > 0) {
                for (const err of errors)
                    console.log(chalk.yellow(`Warning: ${err}`));
            }
            console.log(chalk.blue(`Parsed ${steps.length} step(s):`));
            for (let i = 0; i < steps.length; i++) {
                const s = steps[i];
                const prev = targetRecord.steps[i];
                const match = prev ? (prev.adapterId === s.adapterId && prev.command === s.command ? chalk.green('✓') : chalk.yellow('⚠')) : chalk.gray('?');
                console.log(`  ${match} [${i + 1}] ${s.adapterId}: ${s.command} ${s.args.join(' ')}`);
            }
            const startStep = options.step ? Math.max(1, Math.min(Number(options.step), steps.length)) : 1;
            if (startStep > 1) {
                console.log(chalk.blue(`Resuming from step ${startStep} (skipping ${startStep - 1} step(s))`));
                for (let i = 0; i < startStep - 1; i++) {
                    const prev = targetRecord.steps[i];
                    console.log(`  ${chalk.gray('→')} [${i + 1}] ${prev ? chalk.green('OK') : chalk.gray('skipped')} ${steps[i].adapterId}: ${steps[i].command}`);
                }
            }
            if (!options.dryRun) {
                const execSteps = steps.slice(startStep - 1);
                const executor = new Executor(registry, { continueOnError: options.continueOnError, verbose: options.verbose, maxParallel: options.maxParallel ? Number(options.maxParallel) : undefined });
                await executor.execute(execSteps, { prompt: targetRecord.prompt });
            }
            return;
        }
        // --dry-run: parse only, show detailed plan
        if (options.dryRun) {
            const planner = new Planner(registry);
            const { steps, errors, warnings, matchedKeywords, matchedRules } = planner.parse(prompt);
            // --explain: show which keywords matched and rule conflicts (always human-readable)
            if (options.explain) {
                if ((matchedRules ?? []).length > 0) {
                    console.log(chalk.blue('Match path (keyword → rule → step):'));
                    for (const m of (matchedRules ?? [])) {
                        console.log(`  ${chalk.green('✓')} "${m.keyword}" → ${chalk.yellow(m.ruleId)} → [${m.adapterId}] ${m.command}`);
                    }
                }
                if ((warnings ?? []).length > 0) {
                    console.log(chalk.blue('\nRule conflicts:'));
                    for (const w of warnings ?? []) {
                        console.log(`  ${chalk.yellow('⚠')} ${w}`);
                    }
                }
                if (options.outputFormat && options.outputFormat !== 'text' && options.outputFormat !== 'json') {
                    const data = { steps, errors, warnings, matchedKeywords };
                    if (options.outputFormat === 'yaml') {
                        process.stdout.write(yaml.stringify(data));
                    }
                    else {
                        process.stdout.write(JSON.stringify(data, null, 2));
                    }
                    return;
                }
            }
            // --adapter-check: pre-flight check all adapters
            if (options.adapterCheck) {
                const checkExecutor = new Executor(registry, {});
                const checks = await checkExecutor.checkAdapters(steps);
                const allOk = checks.every(c => c.available);
                for (const c of checks) {
                    const icon = c.available ? chalk.green('✓') : chalk.red('✗');
                    const name = `${c.step.adapterId}:${c.step.command}`;
                    if (c.available) {
                        console.log(`${icon} ${name}`);
                    }
                    else {
                        console.log(`${icon} ${name} — ${c.error}`);
                    }
                }
                if (!allOk) {
                    console.log(chalk.red(`\nAdapter check failed: ${checks.filter(c => !c.available).length} unavailable`));
                    process.exit(1);
                }
                console.log(chalk.green(`\nAll ${checks.length} adapters available`));
                return;
            }
            // Structured output when --output-format is specified (text is default for human-readable)
            if (options.outputFormat && options.outputFormat !== 'text' && options.outputFormat !== 'json') {
                const data = { steps, errors, warnings, matchedKeywords };
                if (options.outputFormat === 'yaml') {
                    process.stdout.write(yaml.stringify(data));
                }
                else {
                    process.stdout.write(JSON.stringify(data, null, 2));
                }
                return;
            }
            // --dot: output Graphviz DOT digraph
            if (options.dot) {
                const lines = ['digraph steps {', '  rankdir=LR;', '  node [shape=box];'];
                for (let i = 0; i < steps.length; i++) {
                    const step = steps[i];
                    lines.push(`  step${i} [label="${step.adapterId}: ${step.command}"];`);
                    if (i > 0 && steps[i - 1].outputSlots.length > 0) {
                        lines.push(`  step${i - 1} -> step${i} [label="data flow"];`);
                    }
                }
                lines.push('}');
                process.stdout.write(lines.join('\n') + '\n');
                return;
            }
            // --export-d3: output {tasks, edges} JSON for D3.js Gantt/timeline visualization
            if (options.exportD3) {
                const layers = Executor.computeLayers(steps);
                const deps = new Map();
                for (let i = 0; i < steps.length; i++)
                    deps.set(i, new Set());
                for (let i = 0; i < steps.length; i++) {
                    for (const input of steps[i].inputSlots) {
                        for (let j = 0; j < i; j++) {
                            if (steps[j].outputSlots.includes(input))
                                deps.get(i).add(j);
                        }
                        const stepDeps = steps[i].dependsOn;
                        if (stepDeps) {
                            for (const depId of stepDeps) {
                                for (let j = 0; j < i; j++) {
                                    if (`${steps[j].adapterId}:${steps[j].command}` === depId)
                                        deps.get(i).add(j);
                                }
                            }
                        }
                    }
                }
                const tasks = steps.map((step, i) => ({
                    id: i,
                    name: `${step.adapterId}: ${step.command}`,
                    adapterType: step.adapterType,
                    args: step.args,
                    layer: layers.findIndex(l => l.includes(i)) ?? 0,
                    status: 'pending',
                }));
                const edges = [];
                for (const [to, fromSet] of deps) {
                    for (const from of fromSet) {
                        edges.push({ from, to });
                    }
                }
                const d3 = { tasks, edges };
                const json = JSON.stringify(d3);
                if (options.exportD3 === '-') {
                    process.stdout.write(json + '\n');
                }
                else {
                    writeFileSync(options.exportD3, json, 'utf-8');
                    console.log(chalk.green(`Exported D3 JSON: ${tasks.length} tasks, ${edges.length} edges → ${options.exportD3}`));
                }
                return;
            }
            // --script: output a shell script that replays the plan
            if (options.script) {
                const lines = ['#!/bin/bash', '# Generated by unified-agent-cli --dry-run --script', ''];
                for (let i = 0; i < steps.length; i++) {
                    const step = steps[i];
                    const argsStr = step.args.map(a => a.includes(' ') ? `'${a}'` : a).join(' ');
                    if (step.adapterType === 'opencli') {
                        lines.push(`# step ${i + 1}: ${step.adapterId} ${step.command} ${argsStr}`);
                        lines.push(`opencli ${step.command} ${argsStr}`);
                    }
                    else {
                        lines.push(`# step ${i + 1}: ${step.adapterId} ${step.command} ${argsStr}`);
                        lines.push(`${step.adapterId} ${step.command} ${argsStr}`);
                    }
                    lines.push('');
                }
                const content = lines.join('\n');
                if (options.script === '-') {
                    process.stdout.write(content + '\n');
                }
                else {
                    writeFileSync(options.script, content, 'utf-8');
                    console.log(chalk.green(`Script written to ${options.script}`));
                }
                return;
            }
            // Layer + parallel group display (always shown in dry-run, uses same layering logic as executor)
            const layers = Executor.computeLayers(steps);
            for (let li = 0; li < layers.length; li++) {
                const parallel = layers[li].length > 1;
                const groupLabel = parallel ? `layer ${li} (${layers[li].length} parallel)` : `layer ${li}`;
                console.log(chalk.cyan(`[${groupLabel}]`));
                for (const idx of layers[li]) {
                    const step = steps[idx];
                    const key = `${step.adapterId}:${step.command}`;
                    const status = chalk.green('✓');
                    console.log(`  ${status} [${idx + 1}] ${step.adapterId}: ${step.command} ${step.args.join(' ')}`);
                    if (step.inputSlots.length > 0)
                        console.log(`       inputSlots: ${step.inputSlots.join(', ')}`);
                    if (step.outputSlots.length > 0)
                        console.log(`       outputSlots: ${step.outputSlots.join(', ')}`);
                }
            }
            // ASCII flow graph (always shown in dry-run)
            if (steps.length > 0) {
                process.stderr.write(chalk.gray('  ' + '┌' + '─'.repeat(26) + '┐\n'));
                for (let i = 0; i < steps.length; i++) {
                    const step = steps[i];
                    const label = `${i + 1}. ${step.adapterId}: ${step.command}`;
                    const pad = Math.max(0, 24 - label.length);
                    process.stderr.write(chalk.gray('  │') + ` ${chalk.white(label.padEnd(24))} ` + chalk.gray('│\n'));
                    if (i < steps.length - 1) {
                        process.stderr.write(chalk.gray('  │' + ' '.repeat(26) + '│\n'));
                        process.stderr.write(chalk.gray('  │') + chalk.cyan('  ↓'.padEnd(25)) + chalk.gray('│\n'));
                    }
                }
                process.stderr.write(chalk.gray('  └' + '─'.repeat(26) + '┘\n'));
            }
            console.log(chalk.blue(`Parsed ${steps.length} step(s):`));
            const avgDurations = getAvgDurations();
            let totalEstimatedMs = 0;
            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                const num = chalk.yellow(`[${i + 1}]`);
                console.log(`  ${num} ${chalk.green(step.adapterId)}: ${step.command} ${step.args.join(' ')}`);
                if (step.inputSlots.length > 0) {
                    console.log(`       ${chalk.gray('inputSlots:')} ${step.inputSlots.join(', ')}`);
                }
                if (step.outputSlots.length > 0) {
                    console.log(`       ${chalk.gray('outputSlots:')} ${step.outputSlots.join(', ')}`);
                }
                const key = `${step.adapterId}:${step.command}`;
                const ms = avgDurations.get(key);
                if (ms != null) {
                    totalEstimatedMs += ms;
                    console.log(`       ${chalk.gray('estimated:')} ~${(ms / 1000).toFixed(1)}s`);
                }
            }
            if (totalEstimatedMs > 0) {
                console.log(chalk.blue(`Total estimated: ~${(totalEstimatedMs / 1000).toFixed(1)}s`));
            }
            // Validate each step against registry (check adapter availability)
            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                const candidates = await registry.findAdapters(step);
                if (candidates.length === 0) {
                    errors.push(`step ${i + 1}: no adapter handles "${step.adapterId}" (adapterType=${step.adapterType})`);
                }
                else {
                    const available = await Promise.all(candidates.map(a => a.checkAvailable()));
                    const availableAdapters = candidates.filter((_, j) => available[j]);
                    if (availableAdapters.length === 0) {
                        errors.push(`step ${i + 1}: ${step.adapterId} is installed but not available (check health with --check)`);
                    }
                }
            }
            // Show ASCII DAG of step dependencies
            if (steps.length > 1) {
                console.log(chalk.blue('\nStep dependency graph:'));
                for (let i = 0; i < steps.length; i++) {
                    const step = steps[i];
                    const prefix = i === 0 ? '┌─' : '│ ';
                    const connector = i === steps.length - 1 ? '└─' : '├─';
                    const argsStr = step.args.length > 0 ? ` ${step.args.join(' ')}` : '';
                    console.log(`${prefix}[${i + 1}] ${step.adapterId} ${step.command}${argsStr}`);
                    if (step.inputSlots.length > 0) {
                        console.log(`${connector}  input: ${step.inputSlots.join(', ')}`);
                    }
                    if (step.outputSlots.length > 0) {
                        console.log(`${connector}  output: ${step.outputSlots.join(', ')}`);
                    }
                }
                // Summary arrows
                console.log(chalk.gray('\nData flow:'));
                for (let i = 0; i < steps.length; i++) {
                    const step = steps[i];
                    if (step.outputSlots.length > 0) {
                        const nextStep = steps[i + 1];
                        const consumes = nextStep?.inputSlots.length ? ` → [${i + 2}] consumes ${nextStep.inputSlots.join(', ')}` : ' → (end)';
                        console.log(`  [${i + 1}] ${step.outputSlots.join(', ')}${consumes}`);
                    }
                }
            }
            if (options.explain && (warnings ?? []).length > 0) {
                console.log(chalk.blue('\nRule conflicts:'));
                for (const w of warnings ?? []) {
                    console.log(`  ${chalk.yellow('⚠')} ${w}`);
                }
            }
            for (const err of errors) {
                console.log(chalk.red(`Error: ${err}`));
            }
            return;
        }
        // Full execution
        const planner = new Planner(registry);
        // Meta-cognitive pre-audit: ask "am I solving the right problem?" before parsing
        if (!options.noPreAudit) {
            const audit = planner.preAudit(prompt);
            if (audit.blocked) {
                console.error(chalk.red('[pre-audit] BLOCKED: ' + audit.issues.join('; ')));
                process.exit(1);
            }
            if (audit.issues.length > 0) {
                for (const issue of audit.issues) {
                    console.error(chalk.yellow('[pre-audit] ' + issue));
                }
            }
        }
        const { steps, errors } = planner.parse(prompt);
        if (errors.length > 0 && steps.length === 0) {
            console.error(chalk.red(`Error: ${errors[0]}`));
            process.exit(1);
        }
        // --env-file: load .env file and merge into process.env
        if (options.envFile) {
            try {
                const envContent = readFileSync(options.envFile, 'utf-8');
                for (const line of envContent.split('\n')) {
                    const trimmed = line.trim();
                    if (!trimmed || trimmed.startsWith('#'))
                        continue;
                    const eqIdx = trimmed.indexOf('=');
                    if (eqIdx < 0)
                        continue;
                    const key = trimmed.slice(0, eqIdx).trim();
                    const val = trimmed.slice(eqIdx + 1).trim().replace(/^["']|["']$/g, '');
                    if (key)
                        process.env[key] = val;
                }
            }
            catch (err) {
                console.error(chalk.red(`Failed to load env-file: ${err instanceof Error ? err.message : String(err)}`));
                process.exit(1);
            }
        }
        // Env var overrides: UNIFIED_AGENT_* maps to executor options
        const envOpts = {
            maxRetries: process.env.UNIFIED_AGENT_MAX_RETRIES ? Number(process.env.UNIFIED_AGENT_MAX_RETRIES) : undefined,
            defaultTimeoutMs: process.env.UNIFIED_AGENT_DEFAULT_TIMEOUT_MS ? Number(process.env.UNIFIED_AGENT_DEFAULT_TIMEOUT_MS) : undefined,
            continueOnError: process.env.UNIFIED_AGENT_CONTINUE_ON_ERROR === '1' ? true : undefined,
        };
        // --confirm-steps: interactive Y/n confirmation before execution
        if (options.confirmSteps) {
            console.log(chalk.blue('Planned steps:'));
            for (let i = 0; i < steps.length; i++) {
                const step = steps[i];
                const argsStr = step.args.length > 0 ? ` ${step.args.join(' ')}` : '';
                console.log(`  ${chalk.yellow(`${i + 1}.`)} ${chalk.green(step.adapterId)}: ${step.command}${argsStr}`);
                if (step.inputSlots.length > 0) {
                    console.log(`      ${chalk.gray('input:')} ${step.inputSlots.join(', ')}`);
                }
                if (step.outputSlots.length > 0) {
                    console.log(`      ${chalk.gray('output:')} ${step.outputSlots.join(', ')}`);
                }
                if (step.timeoutMs !== undefined) {
                    console.log(`      ${chalk.gray('timeout:')} ${step.timeoutMs}ms`);
                }
                if (step.maxRetries !== undefined) {
                    console.log(`      ${chalk.gray('retries:')} ${step.maxRetries}`);
                }
            }
            const readline = await import('readline');
            const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
            const answer = await new Promise(resolve => {
                rl.question(chalk.bold('\nProceed with execution? ') + chalk.gray('[Y/n] '), resolve);
            });
            rl.close();
            if (answer.trim().toLowerCase() === 'n') {
                console.log(chalk.yellow('Aborted.'));
                process.exit(0);
            }
        }
        // JSON Lines streaming: each step result goes to stdout immediately
        const executorOpts = {
            continueOnError: options.continueOnError,
            maxRetries: Number(options.maxRetries),
            defaultTimeoutMs: options.defaultTimeoutMs ? Number(options.defaultTimeoutMs) : undefined,
            adapterTimeoutMs: { opencli: 30000, 'cli-anything': 60000 },
            workingDir: options.outputDir,
            enableReview: options.review !== false,
            enableSelfAudit: options.selfAudit !== false,
            verbose: options.verbose,
            explain: options.explain,
            cascadeOnError: options.cascadeOnError,
            outputJson: options.outputFormat === 'json',
            ...Object.fromEntries(Object.entries(envOpts).filter(([, v]) => v !== undefined)),
        };
        if (options.jsonLines) {
            executorOpts.onStepResult = (step, result, durationMs) => {
                process.stdout.write(JSON.stringify({ step, result, durationMs }) + '\n');
            };
        }
        // WebSocket streaming: start WS server and push step events to connected dashboard
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        let wss = null;
        let seq = 0;
        const broadcast = (payload) => {
            if (!wss)
                return;
            wss.clients.forEach((client) => {
                if (client.readyState === 1)
                    client.send(payload);
            });
        };
        if (options.streamTo) {
            const { WebSocketServer } = await import('ws');
            const port = Number(options.streamTo) || 9876;
            wss = new WebSocketServer({ port });
            console.log(chalk.blue(`Streaming step events to ws://localhost:${port}`));
            console.log(chalk.gray(`  Dashboard: open src/web-dashboard/index.html in browser`));
            wss.on('connection', (ws) => {
                ws.on('error', () => { });
            });
            executorOpts.onStepResult = (step, result, durationMs) => {
                broadcast(JSON.stringify({ type: 'step_result', seq: seq++, step, result, durationMs }));
            };
        }
        const executor = new Executor(registry, executorOpts);
        // Emit run_start before execution
        if (options.streamTo) {
            broadcast(JSON.stringify({ type: 'run_start', seq: seq++, runId: executor.runId ?? '', steps: steps.length, timestamp: new Date().toISOString() }));
        }
        const results = await executor.execute(steps, { prompt });
        if (options.streamTo) {
            const ok = results.filter(r => r.success).length;
            const fail = results.filter(r => !r.success).length;
            broadcast(JSON.stringify({ type: 'run_end', seq: seq++, runId: executor.runId ?? '', timestamp: new Date().toISOString(), stats: { total: results.length, ok, fail } }));
        }
        // Output results to stdout (non-JSON-Lines mode)
        const outputData = { results, errors };
        if (!options.jsonLines && options.outputFormat === 'yaml') {
            process.stdout.write(yaml.stringify(outputData));
        }
        else if (!options.jsonLines) {
            process.stdout.write(JSON.stringify(outputData, null, 2));
        }
        // Human-readable summary to stderr (suppressed in --json mode)
        if (!options.json) {
            for (const err of errors) {
                console.error(chalk.yellow(`Warning: ${err}`));
            }
            const failures = results.filter(r => !r.success);
            if (failures.length > 0) {
                console.error(chalk.red(`\n${failures.length} step(s) failed:`));
                for (const f of failures) {
                    console.error(chalk.red(`  - ${f.error}`));
                }
                process.exit(1);
            }
        }
        // --metrics: start Prometheus /metrics server
        // @ts-ignore - metrics option added at runtime
        if (options.metrics) {
            // @ts-ignore
            const { register, incr, startMetricsServer } = await import('shared/metrics.js');
            register('task_orchestrator_runs_total', 'counter', 'Total task-orchestrator runs');
            incr('task_orchestrator_runs_total');
            const port = typeof options.metrics === 'number' ? options.metrics : 9090;
            startMetricsServer(port);
        }
    });
    await program.parseAsync();
}
main().catch((err) => {
    console.error(chalk.red(err.message));
    process.exit(1);
});
