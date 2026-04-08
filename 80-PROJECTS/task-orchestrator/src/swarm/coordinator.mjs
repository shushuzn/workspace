/**
 * Swarm Coordinator - orchestrates multiple task-orchestrator instances
 *
 * Usage:
 *   const swarm = new SwarmCoordinator({ instanceCount: 3, registry });
 *   await swarm.start();
 *   const result = await swarm.submit('opencli screenshot && opencli open');
 *   await swarm.shutdown();
 *
 * Communication protocol: ISCP (Inter-System Coordination Protocol)
 *   - Uses protocol-ext.ts CoordinatorMessage envelope
 *   - Backward-compatible: workers without ISCP support ignore extra envelope fields
 */
import { spawn } from 'child_process';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { createCoordinatorMessage, } from './protocol-ext.mjs';
const TASK_ORCHESTRATOR_DIR = dirname(fileURLToPath(import.meta.url));
export class SwarmCoordinator {
    instances = new Map();
    pendingTasks = new Map();
    taskQueue = [];
    instanceCount;
    registry;
    maxParallel;
    constructor(options = {}) {
        this.instanceCount = options.instanceCount ?? 2;
        this.registry = options.registry;
        this.maxParallel = options.maxParallel ?? 1;
    }
    async start() {
        for (let i = 0; i < this.instanceCount; i++) {
            const id = `swarm-${i}`;
            await this.spawnInstance(id);
        }
    }
    async spawnInstance(id) {
        const indexPath = join(TASK_ORCHESTRATOR_DIR, '..', 'index.js');
        const proc = spawn('node', [indexPath, '--swarm-id', id], {
            stdio: ['pipe', 'pipe', 'pipe'],
            env: { ...process.env, FORCE_COLOR: '0' },
        });
        const instance = { id, process: proc, status: 'idle', isIscp: false };
        this.instances.set(id, instance);
        proc.stdout?.on('data', (data) => {
            const lines = data.toString().trim().split('\n');
            for (const line of lines) {
                if (!line)
                    continue;
                try {
                    const msg = JSON.parse(line);
                    // Detect ISCP support: messages with version field are ISCP-aware
                    if (msg.version && !instance.isIscp) {
                        instance.isIscp = true;
                    }
                    this.handleMessage(instance.id, msg, !!instance.isIscp);
                }
                catch {
                    // Non-JSON output (human-readable logs) - ignore
                }
            }
        });
        proc.stderr?.on('data', (_data) => {
            // Swarm instance stderr — could log in verbose mode
        });
        proc.on('exit', (code) => {
            instance.status = 'dead';
            if (this.instances.has(id)) {
                setTimeout(() => this.spawnInstance(id), 1000);
            }
        });
    }
    handleMessage(fromId, msg, isIscp) {
        const instance = this.instances.get(fromId);
        if (!instance)
            return;
        // ISCP path
        if (isIscp && 'type' in msg) {
            const imsg = msg;
            switch (imsg.type) {
                case 'task_result': {
                    const result = imsg.payload.result;
                    if (result?.taskId) {
                        const pending = this.pendingTasks.get(result.taskId);
                        if (pending) {
                            pending.resolve({
                                taskId: result.taskId,
                                success: result.success,
                                output: result.output,
                                artifacts: result.artifacts.map(a => ({ type: a.type, path: a.path ?? a.data ?? '' })),
                                error: result.error?.message,
                            });
                            this.pendingTasks.delete(result.taskId);
                        }
                    }
                    instance.status = 'idle';
                    instance.currentTaskId = undefined;
                    this.dispatchNext();
                    break;
                }
                case 'error_result': {
                    const err = imsg.payload.error;
                    // Find pending task by checking the rootId in lineage
                    for (const [taskId, pending] of this.pendingTasks) {
                        pending.reject(new Error(err?.message ?? 'Unknown error'));
                        this.pendingTasks.delete(taskId);
                        break;
                    }
                    instance.status = 'idle';
                    instance.currentTaskId = undefined;
                    this.dispatchNext();
                    break;
                }
                case 'ack': {
                    // Worker acknowledged - nothing to do, task is in progress
                    break;
                }
                case 'cascade_signal': {
                    const cascade = imsg.payload.cascade;
                    if (cascade?.severity === 'stop') {
                        // Cascade stop: cancel pending tasks
                        for (const [taskId, pending] of this.pendingTasks) {
                            pending.reject(new Error(`Cascade stop: ${cascade.triggeredBy}`));
                            this.pendingTasks.delete(taskId);
                        }
                    }
                    break;
                }
            }
            return;
        }
        // Legacy (non-ISCP) path — old protocol.ts format
        if (!('type' in msg))
            return;
        const legacy = msg;
        switch (legacy.type) {
            case 'task_result': {
                const result = legacy.payload;
                const pending = this.pendingTasks.get(result.taskId);
                if (pending) {
                    pending.resolve(result);
                    this.pendingTasks.delete(result.taskId);
                }
                instance.status = 'idle';
                instance.currentTaskId = undefined;
                this.dispatchNext();
                break;
            }
            case 'heartbeat':
                break;
        }
    }
    dispatchNext() {
        if (this.taskQueue.length === 0)
            return;
        const idleInstance = [...this.instances.values()].find(i => i.status === 'idle');
        if (!idleInstance)
            return;
        const { taskId, prompt, steps, resolve, reject } = this.taskQueue.shift();
        this.dispatchToInstance(idleInstance.id, taskId, prompt, steps).then(resolve).catch(reject);
    }
    async dispatchToInstance(instanceId, taskId, prompt, steps) {
        const instance = this.instances.get(instanceId);
        if (!instance || instance.status === 'dead')
            throw new Error(`Instance ${instanceId} is dead`);
        instance.status = 'busy';
        instance.currentTaskId = taskId;
        // Use ISCP envelope when worker supports it
        if (instance.isIscp) {
            const lineage = { rootId: taskId, chain: [], depth: 0 };
            const dispatch = {
                taskId,
                prompt,
                steps: steps?.map((s, i) => ({
                    stepId: `step-${i}`,
                    adapterType: s.adapterType,
                    command: s.command,
                    args: s.args,
                    inputSlots: s.inputSlots,
                    outputSlots: s.outputSlots,
                    timeoutMs: s.timeoutMs,
                    maxRetries: s.maxRetries,
                })),
            };
            const msg = createCoordinatorMessage(`coord-${taskId}-${Date.now()}`, lineage, 'task_dispatch', { task: dispatch });
            return this.sendAndWait(instanceId, taskId, msg);
        }
        // Legacy protocol
        const dispatch = { taskId, prompt };
        const legacyMsg = createMessage('task_dispatch', 'coordinator', dispatch, instanceId);
        return this.sendAndWait(instanceId, taskId, legacyMsg);
    }
    sendAndWait(instanceId, taskId, msg) {
        return new Promise((resolve, reject) => {
            this.pendingTasks.set(taskId, { resolve, reject });
            const instance = this.instances.get(instanceId);
            if (!instance) {
                this.pendingTasks.delete(taskId);
                reject(new Error(`Instance ${instanceId} gone`));
                return;
            }
            const sent = instance.process.stdin?.write(JSON.stringify(msg) + '\n');
            if (!sent) {
                this.pendingTasks.delete(taskId);
                instance.status = 'idle';
                reject(new Error(`Failed to write to instance ${instanceId}`));
                return;
            }
            setTimeout(() => {
                if (this.pendingTasks.has(taskId)) {
                    this.pendingTasks.delete(taskId);
                    const inst = this.instances.get(instanceId);
                    if (inst)
                        inst.status = 'idle';
                    reject(new Error(`Task ${taskId} timed out`));
                }
            }, 5 * 60 * 1000);
        });
    }
    async submit(prompt, steps) {
        const taskId = `task-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`;
        const idleInstance = [...this.instances.values()].find(i => i.status === 'idle');
        if (idleInstance && this.taskQueue.length < this.maxParallel) {
            const result = await this.dispatchToInstance(idleInstance.id, taskId, prompt, steps);
            return [result];
        }
        return new Promise((resolve, reject) => {
            this.taskQueue.push({ taskId, prompt, steps, resolve: (r) => resolve([r]), reject });
            this.dispatchNext();
        });
    }
    async shutdown() {
        for (const instance of this.instances.values()) {
            instance.process.kill();
        }
        this.instances.clear();
        this.pendingTasks.clear();
        this.taskQueue = [];
    }
    getStatus() {
        return [...this.instances.values()].map(i => ({
            id: i.id,
            status: i.status,
            currentTaskId: i.currentTaskId,
        }));
    }
}
// Legacy protocol factory (for backward compat with old workers)
function createMessage(type, from, payload, to) {
    return {
        type,
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        from,
        to,
        payload,
        timestamp: Date.now(),
    };
}
