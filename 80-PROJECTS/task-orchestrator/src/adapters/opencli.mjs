import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { AdapterSandbox } from './adapter-sandbox.mjs';
// Resolve opencli from opencli project dist (sibling to task-orchestrator in workspace)
const TASK_ORCHESTRATOR_DIR = dirname(fileURLToPath(import.meta.url));
const WORKSPACE_ROOT = join(TASK_ORCHESTRATOR_DIR, '..', '..', '..', '..', 'opencli', 'dist', 'main.js');
const OPENCLI_BIN = join(WORKSPACE_ROOT);
export class OpencliAdapter {
    id = 'opencli';
    type = 'opencli';
    sandbox = new AdapterSandbox();
    canHandle(step) {
        return step.adapterType === 'opencli';
    }
    async execute(step, ctx) {
        const sandboxResult = await this.sandbox.run(process.execPath, [OPENCLI_BIN, step.command, ...step.args], { workingDir: ctx.workingDir, env: ctx.env }, step.timeoutMs);
        const artifacts = [];
        const screenshotMatch = sandboxResult.output.match(/screenshot saved to (.+)/i);
        if (screenshotMatch) {
            artifacts.push({ type: 'screenshot', path: screenshotMatch[1].trim() });
        }
        return {
            success: sandboxResult.success,
            output: sandboxResult.output,
            logs: sandboxResult.logs,
            artifacts,
            error: sandboxResult.error,
            fatal: sandboxResult.fatal,
        };
    }
    async checkAvailable() {
        try {
            const { execaCommand } = await import('execa');
            await execaCommand(`"${OPENCLI_BIN}" --version`, { stderr: 'ignore', reject: false });
            return true;
        }
        catch {
            return false;
        }
    }
}
