/**
 * Replayer.ts
 * Reconstructs execution state from audit logs and supports replay from checkpoints.
 */
import { AppendOnlyEventStore } from './EventStore.mjs';
export class Replayer {
    store;
    constructor(options = {}) {
        this.store = options.eventStore ?? new AppendOnlyEventStore();
    }
    /**
     * Reconstruct the full Step[] sequence from a run's audit log.
     */
    async reconstructSteps(runId) {
        const entries = await this.store.replayRun(runId);
        return entries.map(entry => ({
            adapterId: entry.adapterId,
            adapterType: entry.adapterType,
            command: entry.command,
            args: entry.args,
            inputSlots: entry.inputSlots,
            outputSlots: entry.outputSlots,
        }));
    }
    /**
     * Replay a run from the beginning: returns metadata about what happened.
     */
    async replayFromStart(runId) {
        const entries = await this.store.replayRun(runId);
        if (entries.length === 0) {
            return { runId, steps: [], entries: [], completedSteps: 0, failedStepIdx: null, totalDurationMs: null };
        }
        const steps = entries.map(entry => ({
            adapterId: entry.adapterId,
            adapterType: entry.adapterType,
            command: entry.command,
            args: entry.args,
            inputSlots: entry.inputSlots,
            outputSlots: entry.outputSlots,
        }));
        // Find the first failed step
        let failedStepIdx = null;
        for (const entry of entries) {
            if (!entry.success) {
                failedStepIdx = entry.stepIdx;
                break;
            }
        }
        // Sum durations
        const totalDurationMs = entries.reduce((sum, e) => sum + (e.durationMs ?? 0), 0);
        return {
            runId,
            steps,
            entries,
            completedSteps: entries.filter(e => e.success).length,
            failedStepIdx,
            totalDurationMs,
        };
    }
    /**
     * Replay from a checkpoint: returns only entries at and after the given seq.
     * Useful for resuming interrupted runs.
     */
    async replayFromCheckpoint(runId, checkpointSeq) {
        const entries = await this.store.replayRun(runId);
        return entries.filter(e => e.seq >= checkpointSeq);
    }
    /**
     * Find the checkpoint (last successful step seq) for a run.
     * Returns seq of the last completed step, or -1 if no step completed.
     */
    async findCheckpoint(runId) {
        const entries = await this.store.replayRun(runId);
        let lastSuccessful = -1;
        for (const entry of entries) {
            if (entry.success)
                lastSuccessful = entry.seq;
        }
        return lastSuccessful;
    }
    /**
     * Get a summary of all runs in the audit log.
     */
    async listRuns() {
        const runIds = await this.store.listRunIds();
        const summaries = [];
        for (const runId of runIds) {
            const entries = await this.store.replayRun(runId);
            const completedSteps = entries.filter(e => e.success).length;
            const failed = entries.some(e => !e.success);
            const totalDurationMs = entries.reduce((sum, e) => sum + (e.durationMs ?? 0), 0);
            summaries.push({ runId, totalSteps: entries.length, completedSteps, failed, totalDurationMs });
        }
        return summaries;
    }
}
