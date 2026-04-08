import { SwarmCoordinator } from '../swarm/index.mjs';
export class SwarmAdapter {
    id = 'swarm';
    type = 'swarm';
    canHandle(step) {
        return step.adapterType === 'swarm' || step.adapterId === 'swarm';
    }
    coordinator;
    async execute(step, ctx) {
        try {
            if (!this.coordinator) {
                this.coordinator = new SwarmCoordinator({ instanceCount: 2 });
                await this.coordinator.start();
            }
            const prompt = step.args.join(' ') || (ctx.prompt ?? '');
            const results = await this.coordinator.submit(prompt);
            const success = results.every(r => r.success);
            const output = results.map(r => r.output).join('\n---\n');
            return {
                success,
                output,
                logs: '',
                artifacts: results.flatMap(r => r.artifacts.map((a) => ({ type: a.type, path: a.path ?? a.data ?? '' }))),
                error: success ? undefined : results.find(r => !r.success)?.error,
                fatal: false,
            };
        }
        catch (err) {
            const msg = err instanceof Error ? err.message : String(err);
            return {
                success: false,
                output: '',
                logs: msg,
                artifacts: [],
                error: msg,
                fatal: false,
            };
        }
    }
    async checkAvailable() {
        return true;
    }
    register() {
        return {
            adapterId: 'swarm',
            keywords: ['swarm', 'multi-agent', '多智能体', 'multiagent'],
            commands: ['orchestrate'],
            outputSlots: [],
            priority: 10,
        };
    }
}
