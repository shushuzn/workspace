import { existsSync, readFileSync } from 'fs';
import { homedir } from 'os';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
/** Find the CLI-Anything registry.json */
function findRegistryJson() {
    // 1. CLI_ANYTHING_REGISTRY env var
    if (process.env.CLI_ANYTHING_REGISTRY) {
        if (existsSync(process.env.CLI_ANYTHING_REGISTRY)) {
            return process.env.CLI_ANYTHING_REGISTRY;
        }
    }
    // 2. Check common install locations
    const candidates = [
        // Local dev / clone
        join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..', 'CLI-Anything', 'registry.json'),
        join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..', '..', 'cli-anything', 'registry.json'),
        // Global opencli install
        join(homedir(), '.opencli', 'clis', 'CLI-Anything', 'registry.json'),
        join(homedir(), '.openclaw', 'skills', 'cli-anything', 'registry.json'),
        // npm global
        join(homedir(), '.npm', 'cli-anything', 'registry.json'),
    ];
    for (const p of candidates) {
        if (existsSync(p))
            return p;
    }
    return null;
}
/** Extract routing keywords from a CLI description */
function extractKeywords(entry) {
    const keywords = [];
    // Software name variants
    keywords.push(entry.name);
    keywords.push(entry.display_name);
    keywords.push(entry.display_name.toLowerCase());
    // Category as keyword
    if (entry.category) {
        keywords.push(entry.category);
    }
    // Extract meaningful words from description
    const descWords = entry.description
        .toLowerCase()
        .replace(/[^\w\s]/g, ' ')
        .split(/\s+/)
        .filter(w => w.length > 3)
        .filter(w => !['via', 'with', 'from', 'that', 'this', 'used', 'using', 'your', 'manage'].includes(w));
    // Add top 5 most meaningful words
    keywords.push(...descWords.slice(0, 5));
    return [...new Set(keywords)];
}
/** Load and parse the CLI-Anything registry.json */
export function loadRegistry() {
    const errors = [];
    const entries = [];
    const registryPath = findRegistryJson();
    if (!registryPath) {
        errors.push('CLI-Anything registry.json not found. Set CLI_ANYTHING_REGISTRY or install CLI-Anything.');
        return { entries, errors };
    }
    try {
        const content = readFileSync(registryPath, 'utf-8');
        const parsed = JSON.parse(content);
        if (!parsed.clis || !Array.isArray(parsed.clis)) {
            errors.push(`registry.json: expected .clis array, got ${typeof parsed.clis}`);
            return { entries, errors };
        }
        for (let i = 0; i < parsed.clis.length; i++) {
            const raw = parsed.clis[i];
            if (!raw.name || !raw.entry_point) {
                errors.push(`registry.json[${i}]: missing required field (name or entry_point)`);
                continue;
            }
            const entry = {
                name: String(raw.name),
                display_name: String(raw.display_name ?? raw.name),
                description: String(raw.description ?? ''),
                install_cmd: String(raw.install_cmd ?? ''),
                entry_point: String(raw.entry_point),
                skill_md: raw.skill_md ? String(raw.skill_md) : null,
                category: String(raw.category ?? 'general'),
            };
            entry.keywords = extractKeywords(entry);
            entries.push(entry);
        }
    }
    catch (err) {
        errors.push(`Failed to load registry.json: ${err instanceof Error ? err.message : String(err)}`);
    }
    return { entries, errors };
}
/** Convert registry entries to AdapterRegistration objects */
export function entriesToRegistrations(entries) {
    return entries.map(entry => ({
        adapterId: entry.entry_point,
        keywords: entry.keywords ?? [],
        commands: [], // filled in by adapter self-description
        outputSlots: [],
        priority: 0,
    }));
}
