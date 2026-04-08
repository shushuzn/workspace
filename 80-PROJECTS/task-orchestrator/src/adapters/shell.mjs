import { execaCommand } from 'execa';
export class ShellAdapter {
    id = 'shell';
    type = 'cli-anything';
    canHandle(step) {
        return step.adapterId.startsWith('shell:');
    }
    async execute(step, ctx) {
        // shell:<command> — extract command from adapterId; step.command is the arg
        const command = step.command;
        try {
            const { stdout, stderr, exitCode } = await execaCommand(command, {
                cwd: ctx.workingDir,
                env: ctx.env,
                reject: false,
            });
            return {
                success: exitCode === 0,
                output: stdout,
                logs: stderr,
                artifacts: [],
                error: exitCode !== 0 ? `exit ${exitCode}` : undefined,
                fatal: false,
            };
        }
        catch (err) {
            return {
                success: false,
                output: '',
                logs: '',
                artifacts: [],
                error: err instanceof Error ? err.message : String(err),
                fatal: false,
            };
        }
    }
    async checkAvailable() {
        return true;
    }
}
