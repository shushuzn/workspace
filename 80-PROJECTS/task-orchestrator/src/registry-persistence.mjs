/**
 * registry-persistence.ts
 * Adds JSON file persistence to the Registry class.
 * Adapter registrations are saved to a JSON file and loaded on startup
 * to avoid re-discovering adapters on every run.
 */
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import { Registry } from './registry.mjs';
export class PersistedRegistry extends Registry {
    registryFile;
    constructor(options = {}) {
        super(options);
        this.registryFile = options.registryFile ?? join('.task-orchestrator', 'registry.json');
    }
    /**
     * Save current registrations to the registry file.
     * Call this after load() if adapters were updated.
     */
    save(path) {
        const file = path ?? this.registryFile;
        const registrations = this.registrations;
        writeFileSync(file, JSON.stringify({ version: 1, registrations }, null, 2), 'utf-8');
    }
    /**
     * Load registrations from the registry file.
     * If the file doesn't exist, silently returns false.
     * Returns true if a file was loaded, false otherwise.
     */
    loadFromFile(path) {
        const file = path ?? this.registryFile;
        if (!existsSync(file))
            return false;
        try {
            const raw = JSON.parse(readFileSync(file, 'utf-8'));
            if (!raw?.registrations || !Array.isArray(raw.registrations)) {
                console.warn(`[registry-persistence] Invalid registry file: ${file}`);
                return false;
            }
            this.registrations = raw.registrations;
            return true;
        }
        catch (err) {
            console.warn(`[registry-persistence] Failed to load registry from ${file}: ${err instanceof Error ? err.message : err}`);
            return false;
        }
    }
}
