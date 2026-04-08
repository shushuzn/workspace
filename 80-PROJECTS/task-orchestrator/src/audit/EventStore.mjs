/**
 * EventStore.ts
 * Append-only audit log store for task-orchestrator.
 * Supports append, query by runId, query by time range, and replay.
 */
import { existsSync, appendFileSync } from 'fs';
import { createReadStream } from 'fs';
import { createInterface } from 'readline';
import { join } from 'path';
import { mkdirSync } from 'fs';
export class AppendOnlyEventStore {
    logPath;
    constructor(options = {}) {
        const defaultDir = join(process.env.HOME ?? process.env.USERPROFILE ?? '.', '.unified-agent-cli');
        if (!existsSync(defaultDir))
            mkdirSync(defaultDir, { recursive: true });
        this.logPath = options.logPath ?? join(defaultDir, 'audit.jsonl');
    }
    /**
     * Append a single audit log entry to the log file.
     */
    append(entry) {
        appendFileSync(this.logPath, JSON.stringify(entry) + '\n', 'utf-8');
    }
    /**
     * Append multiple entries in batch (more efficient for bulk inserts).
     */
    appendBatch(entries) {
        const lines = entries.map(e => JSON.stringify(e)).join('\n') + '\n';
        appendFileSync(this.logPath, lines, 'utf-8');
    }
    /**
     * Query all entries for a specific runId.
     */
    async queryByRunId(runId) {
        const entries = [];
        const stream = createReadStream(this.logPath, { encoding: 'utf-8' });
        const rl = createInterface({ input: stream, crlfDelay: Infinity });
        for await (const line of rl) {
            if (!line.trim())
                continue;
            try {
                const entry = JSON.parse(line);
                if (entry.runId === runId)
                    entries.push(entry);
            }
            catch {
                // Skip malformed lines
            }
        }
        return entries;
    }
    /**
     * Query entries within a time range (ISO timestamp strings).
     */
    async queryByTimeRange(start, end) {
        const entries = [];
        const stream = createReadStream(this.logPath, { encoding: 'utf-8' });
        const rl = createInterface({ input: stream, crlfDelay: Infinity });
        for await (const line of rl) {
            if (!line.trim())
                continue;
            try {
                const entry = JSON.parse(line);
                if (entry.timestamp >= start && entry.timestamp <= end)
                    entries.push(entry);
            }
            catch {
                // Skip malformed lines
            }
        }
        return entries;
    }
    /**
     * List all distinct runIds in the log.
     */
    async listRunIds() {
        const runIds = new Set();
        const stream = createReadStream(this.logPath, { encoding: 'utf-8' });
        const rl = createInterface({ input: stream, crlfDelay: Infinity });
        for await (const line of rl) {
            if (!line.trim())
                continue;
            try {
                const entry = JSON.parse(line);
                runIds.add(entry.runId);
            }
            catch {
                // Skip malformed lines
            }
        }
        return Array.from(runIds);
    }
    /**
     * Replay a specific run: returns entries in causality order (sorted by seq).
     */
    async replayRun(runId) {
        const entries = await this.queryByRunId(runId);
        return entries.sort((a, b) => a.seq - b.seq);
    }
    /**
     * Get the latest entry for a run (last step completed).
     */
    async getLatestEntry(runId) {
        const entries = await this.queryByRunId(runId);
        if (entries.length === 0)
            return null;
        return entries.reduce((latest, e) => (e.seq > latest.seq ? e : latest));
    }
    /**
     * Check if a runId already exists in the log.
     */
    async runExists(runId) {
        const stream = createReadStream(this.logPath, { encoding: 'utf-8' });
        const rl = createInterface({ input: stream, crlfDelay: Infinity });
        for await (const line of rl) {
            if (!line.trim())
                continue;
            try {
                const entry = JSON.parse(line);
                if (entry.runId === runId) {
                    stream.destroy();
                    return true;
                }
            }
            catch {
                // Skip malformed lines
            }
        }
        return false;
    }
    /** Path to the audit log file */
    get path() {
        return this.logPath;
    }
}
