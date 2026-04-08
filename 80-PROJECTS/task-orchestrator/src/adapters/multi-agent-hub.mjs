import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { execa } from 'execa';
// Resolve multi-agent-hub from workspace (sibling to task-orchestrator)
const TASK_ORCHESTRATOR_DIR = dirname(fileURLToPath(import.meta.url));
const WORKSPACE_ROOT = join(TASK_ORCHESTRATOR_DIR, '..', '..', '..', '..', '..');
const MHUB_DIR = join(WORKSPACE_ROOT, 'multi-agent-hub');
const MHUB_PATH = join(MHUB_DIR, 'index.js');
export class MultiAgentHubAdapter {
    id = 'multi-agent-hub';
    type = 'multi-agent-hub';
    canHandle(step) {
        return step.adapterType === 'multi-agent-hub';
    }
    async execute(step, ctx) {
        try {
            // Use 'node' prefix to avoid Windows Git Bash shebang TTY capture issue
            const { stdout, stderr, failed } = await execa('node', [MHUB_PATH, ...step.args], { cwd: MHUB_DIR, env: ctx.env, timeout: step.timeoutMs });
            const output = stdout || stderr || '';
            return {
                success: !failed,
                output,
                logs: stderr,
                artifacts: [],
                error: undefined,
                fatal: false,
            };
        }
        catch (err) {
            // On Windows, content often ends up in stdout of the caught error
            const output = err.stdout || '';
            return {
                success: false,
                output,
                logs: err.stderr ?? '',
                artifacts: [],
                error: err.message,
                fatal: false,
            };
        }
    }
    async checkAvailable() {
        try {
            const { existsSync } = await import('fs');
            return existsSync(MHUB_PATH);
        }
        catch {
            return false;
        }
    }
}
