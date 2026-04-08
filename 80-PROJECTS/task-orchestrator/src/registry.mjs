import { OpencliAdapter } from './adapters/opencli.mjs';
import { CliAnythingAdapter } from './adapters/cli-anything.mjs';
import { MultiAgentHubAdapter } from './adapters/multi-agent-hub.mjs';
import { ShellAdapter } from './adapters/shell.mjs';
import { WikipediaLoaderAdapter } from './adapters/wikipedia-loader.mjs';
import { loadRegistry } from './adapters/registry-loader.mjs';
export class Registry {
    adapters = new Map();
    registrations = [];
    options;
    constructor(options = {}) {
        this.options = options;
    }
    /** Load all available adapters */
    async load() {
        // 1. Always load opencli (assumed installed) + shell adapter
        const opencli = new OpencliAdapter();
        this.adapters.set('opencli', opencli);
        const shell = new ShellAdapter();
        this.adapters.set('shell', shell);
        // 2. Always load multi-agent-hub adapter
        const mhub = new MultiAgentHubAdapter();
        this.adapters.set('multi-agent-hub', mhub);
        // 3. Always load wikipedia knowledge base adapter
        const wiki = new WikipediaLoaderAdapter();
        this.adapters.set('wikipedia', wiki);
        // 4. Scan PATH for cli-anything-* harnesses
        await this.discoverCliAnything();
        // 4. Scan user-specified adapter directories
        await this.discoverFromDirs();
        // 5. Collect registrations from all adapters
        this.collectRegistrations();
    }
    collectRegistrations() {
        this.registrations = [];
        for (const adapter of this.adapters.values()) {
            if (adapter.register) {
                const reg = adapter.register();
                if (reg)
                    this.registrations.push(reg);
            }
        }
    }
    /** Return all dynamic adapter registrations for Planner */
    getRegistrations() {
        return [...this.registrations];
    }
    async discoverFromDirs() {
        if (!this.options.adapterDirs?.length)
            return;
        const { existsSync, readdirSync, readFileSync } = await import('fs');
        const { join, basename } = await import('path');
        const yaml = await import('yaml');
        for (const dir of this.options.adapterDirs) {
            if (!existsSync(dir))
                continue;
            try {
                for (const file of readdirSync(dir)) {
                    const filePath = join(dir, file);
                    const ext = file.replace(/^[^.]+/, '');
                    // Try dynamic import of .js/.ts/.mjs files
                    if (['.js', '.ts', '.mjs'].includes(ext)) {
                        try {
                            const mod = await import(filePath);
                            // Module-level register export
                            if (typeof mod.register === 'function') {
                                const reg = mod.register();
                                if (reg?.adapterId) {
                                    const adapter = new CliAnythingAdapter(reg.adapterId.replace('cli-anything-', ''));
                                    this.adapters.set(reg.adapterId, adapter);
                                }
                                continue;
                            }
                        }
                        catch {
                            // Fall through to harness name approach
                        }
                    }
                    // manifest.yaml approach: dir contains manifest.yaml
                    const manifestPath = join(filePath, 'manifest.yaml');
                    if (existsSync(manifestPath)) {
                        try {
                            const content = readFileSync(manifestPath, 'utf-8');
                            const manifest = yaml.parse(content);
                            if (manifest.adapterId) {
                                const name = manifest.adapterId.replace('cli-anything-', '');
                                const adapter = new CliAnythingAdapter(name);
                                if (await adapter.checkAvailable()) {
                                    this.adapters.set(manifest.adapterId, adapter);
                                }
                            }
                        }
                        catch {
                            // ignore
                        }
                        continue;
                    }
                    // Fallback: treat file/dir name as cli-anything harness
                    const name = file.replace(/\.(js|ts|mjs)$/, '');
                    const adapter = new CliAnythingAdapter(name);
                    if (await adapter.checkAvailable()) {
                        this.adapters.set(`cli-anything-${name}`, adapter);
                    }
                }
            }
            catch {
                // Ignore permission errors
            }
        }
    }
    async discoverCliAnything() {
        // 1. Load CLI-Anything registry to get keywords for all available CLIs
        const { entries, errors } = loadRegistry();
        if (errors.length > 0) {
            // Fall back to PATH scanning if registry not found
            await this.scanPathForCliAnything();
        }
        else {
            // Register all CLIs from registry, check availability in parallel
            const checks = entries.map(async (entry) => {
                const adapter = new CliAnythingAdapter(entry.name);
                const available = await adapter.checkAvailable();
                return { adapter, available, entry };
            });
            const results = await Promise.all(checks);
            for (const { adapter, available, entry } of results) {
                if (available) {
                    this.adapters.set(entry.entry_point, adapter);
                    // Also register keywords from registry for routing
                    if (entry.keywords && entry.keywords.length > 0) {
                        const reg = {
                            adapterId: entry.entry_point,
                            keywords: entry.keywords,
                            commands: [],
                            outputSlots: [],
                            priority: 0,
                        };
                        this.registrations.push(reg);
                    }
                }
            }
        }
        // 2. Scan ~/.opencli/clis/ for local adapters
        const { homedir } = await import('os');
        const { existsSync, readdirSync } = await import('fs');
        const { join } = await import('path');
        const localAdapterDir = join(homedir(), '.opencli', 'clis');
        if (existsSync(localAdapterDir)) {
            try {
                for (const file of readdirSync(localAdapterDir)) {
                    const adapter = new OpencliAdapter();
                    adapter.id = `opencli-${file}`;
                    this.adapters.set(adapter.id, adapter);
                }
            }
            catch {
                // Ignore permission errors
            }
        }
    }
    async scanPathForCliAnything() {
        // PATH scan as fallback: look for cli-anything-* binaries
        const { execaCommand } = await import('execa');
        try {
            const { stdout } = await execaCommand('which -a cli-anything-', { stderr: 'ignore', reject: false });
            const lines = stdout.split('\n').filter(Boolean);
            for (const line of lines) {
                const bin = line.trim();
                // Extract harness name: cli-anything-foo -> foo
                const match = bin.match(/cli-anything-(.+)$/);
                if (match) {
                    const name = match[1];
                    const adapter = new CliAnythingAdapter(name);
                    if (await adapter.checkAvailable()) {
                        this.adapters.set(`cli-anything-${name}`, adapter);
                    }
                }
            }
        }
        catch {
            // which not available on Windows, skip
        }
    }
    get(id) {
        return this.adapters.get(id);
    }
    list() {
        return Array.from(this.adapters.values());
    }
    /** Find all adapters that can handle this step, available ones first */
    async findAdapters(step) {
        const candidates = Array.from(this.adapters.values()).filter(a => a.canHandle(step));
        // Check availability in parallel, available adapters sort first
        const results = await Promise.all(candidates.map(async (a) => ({ adapter: a, available: await a.checkAvailable() })));
        results.sort((a, b) => {
            if (a.available && !b.available)
                return -1;
            if (!a.available && b.available)
                return 1;
            return 0;
        });
        return results.map(r => r.adapter);
    }
    /** Find the first available adapter that can handle this step */
    async findAdapter(step) {
        const candidates = await this.findAdapters(step);
        return candidates[0];
    }
}
