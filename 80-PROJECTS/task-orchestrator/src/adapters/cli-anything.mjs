import { AdapterSandbox } from './adapter-sandbox.mjs';
export class CliAnythingAdapter {
    harnessName;
    id;
    type = 'cli-anything';
    sandbox = new AdapterSandbox();
    constructor(harnessName) {
        this.harnessName = harnessName;
        if (!harnessName)
            throw new Error('harnessName is required');
        this.id = `cli-anything-${harnessName}`;
    }
    canHandle(step) {
        return step.adapterType === 'cli-anything' && step.adapterId === this.id;
    }
    async execute(step, ctx) {
        const bin = `cli-anything-${this.harnessName}`;
        const sandboxResult = await this.sandbox.run(bin, [step.command, ...step.args], {
            workingDir: ctx.workingDir,
            env: ctx.env,
        }, step.timeoutMs);
        return {
            success: sandboxResult.success,
            output: sandboxResult.output,
            logs: sandboxResult.logs,
            artifacts: sandboxResult.artifacts,
            error: sandboxResult.error,
            fatal: sandboxResult.fatal,
        };
    }
    async checkAvailable() {
        try {
            const { execaCommand } = await import('execa');
            await execaCommand(`cli-anything-${this.harnessName} --version`, { stderr: 'ignore', reject: false });
            return true;
        }
        catch {
            return false;
        }
    }
}
