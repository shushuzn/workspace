/**
 * TaskOrchestrator OAP Dispatcher
 * Integrates OAP task dispatching into task-orchestrator's execution pipeline.
 *
 * Usage:
 *   import { OAPDispatcher } from './oap-dispatcher.mjs';
 *   const dispatcher = new OAPDispatcher({ hubUrl: 'http://localhost:3847' });
 *   await dispatcher.dispatch({ intent: 'browse', input: { url: '...' } });
 */
// OAP helpers — inlined to avoid cross-project build dependency
let _oapIdCounter = 0;
function generateOAPId(prefix = 'oap') { return `${prefix}-${Date.now()}-${++_oapIdCounter}`; }
function createTask(intent, description, input, opts = {}) {
  return {
    header: { id: generateOAPId(), version: '1.0.0', intent, priority: opts.priority ?? 'normal', sourceAgent: opts.sourceAgent },
    body: { action: 'dispatch', task: { id: generateOAPId('task'), intent, description, input, outputFormat: opts.outputFormat ?? 'json', maxDuration: opts.maxDuration } },
  };
}
function createResult(taskId, status, output, opts = {}) {
  return {
    header: { id: generateOAPId(), version: '1.0.0', intent: 'orchestrate', priority: 'normal', sourceAgent: 'local' },
    body: { action: 'result', result: { taskId, status, output, format: opts.format ?? 'json', metrics: opts.durationMs ? { durationMs: opts.durationMs } : undefined } },
  };
}
const INTENT_ADAPTER_MAP = { browse: 'opencli', execute: 'task-orchestrator', debate: 'multi-agent-hub', analyze: 'multi-agent-hub', orchestrate: 'task-orchestrator' };

export class OAPDispatcher {
    hubUrl;
    agentId;
    localCapabilities;
    agents = new Map();
    pendingTasks = new Map();
    constructor(config = {}) {
        this.hubUrl = config.hubUrl ?? 'http://localhost:3847';
        this.agentId = config.agentId ?? 'task-orchestrator';
        this.localCapabilities = config.localCapabilities ?? [
            {
                name: 'task-chain-executor',
                version: '1.0.0',
                inputSlots: ['taskChain', 'workflowDef'],
                outputSlots: ['executionResult', 'log'],
                adapterType: 'task-orchestrator',
            },
            {
                name: 'planner',
                version: '1.0.0',
                inputSlots: ['yaml', 'dsl'],
                outputSlots: ['parsedWorkflow', 'taskGraph'],
                adapterType: 'task-orchestrator',
            },
        ];
    }
    /** Register local capabilities with the hub */
    async registerCapabilities() {
        for (const cap of this.localCapabilities) {
            try {
                const res = await fetch(`${this.hubUrl}/agent/register`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        agentId: this.agentId,
                        intent: 'orchestrate',
                        capability: cap,
                    }),
                });
                if (res.ok)
                    console.log(`[OAP Dispatcher] Registered: ${cap.name}`);
            }
            catch (e) {
                console.warn(`[OAP Dispatcher] Failed to register ${cap.name}: ${e.message}`);
            }
        }
    }
    /** Route and dispatch a task to the appropriate agent */
    async dispatch(task, opts = {}) {
        const envelope = createTask(task.intent, task.description, task.input, {
            ...task,
            sourceAgent: this.agentId,
            correlationId: opts.correlationId,
        });
        // Find target agent
        const target = this.findAgent(task.intent);
        if (!target) {
            throw new Error(`No agent registered for intent: ${task.intent}`);
        }
        if (target.endpoint) {
            // Remote dispatch
            return this.remoteDispatch(envelope, target.endpoint, opts.timeout ?? task.maxDuration ?? 30000);
        }
        else {
            // Local execution
            return this.localDispatch(envelope, task.intent);
        }
    }
    /** Remote dispatch via HTTP to a known agent endpoint */
    async remoteDispatch(envelope, endpoint, timeout) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), timeout);
        try {
            const res = await fetch(`${endpoint}/dispatch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(envelope),
                signal: controller.signal,
            });
            clearTimeout(timer);
            if (!res.ok)
                throw new Error(`Agent responded with ${res.status}`);
            const resultEnvelope = await res.json();
            return resultEnvelope.body.result;
        }
        catch (e) {
            clearTimeout(timer);
            throw e;
        }
    }
    /** Execute a task locally based on intent */
    async localDispatch(envelope, intent) {
        const task = envelope.body.task;
        const start = Date.now();
        try {
            let output;
            switch (intent) {
                case 'execute':
                case 'orchestrate':
                    output = { status: 'handled', intent, taskId: task.id, note: 'TaskOrchestrator local execution' };
                    break;
                case 'analyze':
                    output = { status: 'handled', intent, taskId: task.id, note: 'Use multi-agent-hub for analysis' };
                    break;
                default:
                    output = { status: 'no-local-handler', intent };
            }
            return {
                taskId: task.id,
                status: 'success',
                output: output,
                format: task.outputFormat ?? 'json',
                metrics: { durationMs: Date.now() - start },
            };
        }
        catch (e) {
            return {
                taskId: task.id,
                status: 'failed',
                output: { error: e.message },
                format: task.outputFormat ?? 'json',
                metrics: { durationMs: Date.now() - start },
            };
        }
    }
    /** Find the best registered agent for a given intent */
    findAgent(intent) {
        const targetAdapter = INTENT_ADAPTER_MAP[intent];
        for (const agent of this.agents.values()) {
            if (agent.intent === intent)
                return agent;
        }
        return null;
    }
    /** Handle an incoming dispatch envelope (when acting as a receiver) */
    async handleDispatch(envelope) {
        const task = envelope.body.task;
        const start = Date.now();
        try {
            const result = await this.localDispatch(envelope, task.intent);
            return createResult(task.id, result.status, result.output, {
                format: result.format,
                durationMs: result.metrics?.durationMs ?? Date.now() - start,
            });
        }
        catch (e) {
            return {
                header: { id: generateOAPId(), version: '1.0.0', intent: task.intent, priority: 'normal', sourceAgent: this.agentId },
                body: { action: 'error', error: { code: 'DISPATCH_FAILED', message: e.message, recoverable: true } },
            };
        }
    }
    /** Start the built-in OAP HTTP server (receives dispatches) */
    async startServer(port = 3848) {
        const http = await import('node:http');
        const server = http.createServer(async (req, res) => {
            if (req.method === 'POST' && req.url === '/dispatch') {
                let body = '';
                req.on('data', (c) => { body += c.toString(); });
                req.on('end', async () => {
                    try {
                        const envelope = JSON.parse(body);
                        const result = await this.handleDispatch(envelope);
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify(result));
                    }
                    catch (e) {
                        res.writeHead(500, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify({ error: e.message }));
                    }
                });
            }
            else if (req.method === 'GET' && req.url === '/agents') {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify([...this.agents.values()]));
            }
            else {
                res.writeHead(404);
                res.end();
            }
        });
        return new Promise((resolve) => {
            server.listen(port, () => {
                console.log(`[OAP Dispatcher] Server listening on port ${port}`);
                resolve();
            });
        });
    }
}
