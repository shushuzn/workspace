/**
 * WSHandler.ts
 * WebSocket handler for real-time executor event streaming.
 * Creates a WebSocket server that broadcasts step execution events to connected dashboards.
 */
import { WebSocketServer, WebSocket } from 'ws';
export class WSHandler {
    wss;
    seq = 0;
    runId = null;
    stepCount = 0;
    completedCount = 0;
    failedCount = 0;
    totalDurationMs = 0;
    constructor(options = {}) {
        const port = options.port ?? 9876;
        this.wss = new WebSocketServer({ port });
        this.wss.on('connection', (ws) => {
            console.log(`[dashboard] client connected (${this.wss.clients.size} total)`);
            // Send current state on connect
            if (this.runId) {
                const state = {
                    type: 'run_start',
                    runId: this.runId,
                    timestamp: new Date().toISOString(),
                    seq: 0,
                    runStats: { totalSteps: this.stepCount, completedSteps: this.completedCount, failedSteps: this.failedCount, totalDurationMs: this.totalDurationMs },
                };
                ws.send(JSON.stringify(state));
            }
        });
        console.log(`[dashboard] WebSocket server listening on ws://localhost:${port}`);
    }
    /** Call before executing steps */
    onRunStart(runId, totalSteps) {
        this.runId = runId;
        this.stepCount = totalSteps;
        this.completedCount = 0;
        this.failedCount = 0;
        this.totalDurationMs = 0;
        this.broadcast({
            type: 'run_start',
            runId,
            timestamp: new Date().toISOString(),
            seq: this.seq++,
            runStats: { totalSteps, completedSteps: 0, failedSteps: 0, totalDurationMs: 0 },
        });
    }
    /** Call before each step starts */
    onStepStart(stepIdx, step) {
        this.broadcast({
            type: 'step_start',
            runId: this.runId ?? '',
            timestamp: new Date().toISOString(),
            seq: this.seq++,
            stepIdx,
            step: {
                adapterId: step.adapterId,
                adapterType: step.adapterType,
                command: step.command,
                args: step.args,
            },
        });
    }
    /** Call after each step completes */
    onStepResult(stepIdx, step, result, durationMs) {
        if (result.success)
            this.completedCount++;
        else
            this.failedCount++;
        this.totalDurationMs += durationMs ?? 0;
        const evt = {
            type: 'step_result',
            runId: this.runId ?? '',
            timestamp: new Date().toISOString(),
            seq: this.seq++,
            stepIdx,
            step: {
                adapterId: step.adapterId,
                adapterType: step.adapterType,
                command: step.command,
                args: step.args,
            },
            result: {
                success: result.success,
                output: result.output,
                error: result.error ?? null,
                code: result.code ?? null,
                durationMs: result.durationMs ?? null,
                attempts: result.attempts ?? 1,
                fatal: result.fatal ?? false,
                artifacts: (result.artifacts ?? []),
            },
            runStats: {
                totalSteps: this.stepCount,
                completedSteps: this.completedCount,
                failedSteps: this.failedCount,
                totalDurationMs: this.totalDurationMs,
            },
        };
        this.broadcast(evt);
    }
    /** Call after all steps complete or on fatal error */
    onRunEnd() {
        if (!this.runId)
            return;
        this.broadcast({
            type: 'run_end',
            runId: this.runId,
            timestamp: new Date().toISOString(),
            seq: this.seq++,
            runStats: {
                totalSteps: this.stepCount,
                completedSteps: this.completedCount,
                failedSteps: this.failedCount,
                totalDurationMs: this.totalDurationMs,
            },
        });
    }
    onError(message) {
        this.broadcast({
            type: 'error',
            runId: this.runId ?? '',
            timestamp: new Date().toISOString(),
            seq: this.seq++,
            message,
        });
    }
    broadcast(event) {
        const data = JSON.stringify(event);
        for (const client of this.wss.clients) {
            if (client.readyState === WebSocket.OPEN) {
                client.send(data);
            }
        }
    }
    close() {
        this.wss.close();
    }
}
