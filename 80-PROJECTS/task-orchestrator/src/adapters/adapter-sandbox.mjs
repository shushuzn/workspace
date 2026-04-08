/**
 * Adapter sandbox: forks a child process per execution.
 * Parent process is isolated from child crashes, OOM, and infinite loops.
 *
 * Communication: JSON messages over process.send/on('message')
 * Protocol:
 *   parent -> child: { type: 'run', id, bin, args, cwd, env, timeoutMs }
 *   child -> parent: { type: 'result', id, success, output, logs, error, fatal }
 */
import { fork } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
const MAX_OUTPUT_BYTES = 10 * 1024 * 1024; // 10MB cap per output stream
const __dirname = dirname(fileURLToPath(import.meta.url));
export class AdapterSandbox {
    options;
    maxOutputBytes;
    defaultTimeoutMs;
    constructor(options = {}) {
        this.options = options;
        this.maxOutputBytes = options.maxOutputBytes ?? MAX_OUTPUT_BYTES;
        this.defaultTimeoutMs = options.defaultTimeoutMs ?? 60_000;
    }
    /**
     * Run a command in a forked sandbox process.
     * Returns result via message protocol — parent process is fully isolated.
     */
    async run(bin, args, ctx, timeoutMs) {
        const effectiveTimeout = timeoutMs ?? this.defaultTimeoutMs;
        // Resolve the sandbox runner script path (same dir as this file)
        const runnerPath = join(__dirname, 'sandbox-runner.cjs');
        return new Promise((resolve) => {
            let stdout = '';
            let stderr = '';
            let resolved = false;
            let timeoutHandle;
            const child = fork(runnerPath, [bin, ...args], {
                cwd: ctx.workingDir,
                env: ctx.env,
                stdio: ['pipe', 'pipe', 'pipe', 'ipc'],
                execArgv: ['--max-old-space-size=256'],
            });
            const cleanup = () => {
                clearTimeout(timeoutHandle);
                if (!child.killed) {
                    try {
                        child.kill('SIGKILL');
                    }
                    catch { /* already dead */ }
                }
            };
            // Timeout
            timeoutHandle = setTimeout(() => {
                if (resolved)
                    return;
                resolved = true;
                cleanup();
                resolve({
                    success: false,
                    output: stdout,
                    logs: stderr,
                    error: `Sandbox timeout after ${effectiveTimeout}ms`,
                    fatal: true,
                    artifacts: [],
                });
            }, effectiveTimeout);
            child.on('message', (msg) => {
                if (msg.type !== 'result' || resolved)
                    return;
                // Enforce output size cap
                const output = (msg.output ?? '').slice(0, this.maxOutputBytes);
                const logs = (msg.logs ?? '').slice(0, this.maxOutputBytes);
                resolved = true;
                clearTimeout(timeoutHandle);
                cleanup();
                resolve({
                    success: msg.success ?? false,
                    output,
                    logs,
                    error: msg.error,
                    fatal: msg.fatal ?? false,
                    artifacts: [],
                });
            });
            child.on('error', (err) => {
                if (resolved)
                    return;
                resolved = true;
                clearTimeout(timeoutHandle);
                cleanup();
                resolve({
                    success: false,
                    output: stdout,
                    logs: stderr,
                    error: err.message.slice(0, 200),
                    fatal: true,
                    artifacts: [],
                });
            });
            child.on('exit', (code, signal) => {
                if (resolved)
                    return;
                // Child exited without sending result — treat as crash
                resolved = true;
                clearTimeout(timeoutHandle);
                cleanup();
                resolve({
                    success: false,
                    output: stdout.slice(0, this.maxOutputBytes),
                    logs: stderr.slice(0, this.maxOutputBytes),
                    error: `Child exited with code ${code ?? 'null'}${signal ? ` (signal: ${signal})` : ''}`,
                    fatal: true,
                    artifacts: [],
                });
            });
            // Send run command to child
            child.send({
                type: 'run',
                cwd: ctx.workingDir,
                env: ctx.env,
            });
        });
    }
}
