/**
 * MCP Registry Store — in-memory registry of MCP servers and tools
 */

export interface MCPServer {
  id: string;
  name: string;
  version: string;
  description: string;
  endpoint: string;
  tools: MCPTool[];
  tags: string[];
  lastHeartbeat: number;
  healthy: boolean;
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  outputSchema?: Record<string, unknown>;
}

export class RegistryStore {
  private servers = new Map<string, MCPServer>();

  register(server: Omit<MCPServer, 'lastHeartbeat' | 'healthy'>): void {
    this.servers.set(server.id, {
      ...server,
      lastHeartbeat: Date.now(),
      healthy: true,
    });
  }

  unregister(id: string): boolean {
    return this.servers.delete(id);
  }

  heartbeat(id: string): boolean {
    const server = this.servers.get(id);
    if (!server) return false;
    server.lastHeartbeat = Date.now();
    server.healthy = true;
    return true;
  }

  get(id: string): MCPServer | undefined {
    return this.servers.get(id);
  }

  list(filter?: { tag?: string; toolName?: string }): MCPServer[] {
    let all = [...this.servers.values()];
    if (filter?.tag) {
      all = all.filter(s => s.tags.includes(filter.tag!));
    }
    if (filter?.toolName) {
      all = all.filter(s => s.tools.some(t => t.name.includes(filter.toolName!)));
    }
    return all;
  }

  discover(capability: string): MCPServer[] {
    return [...this.servers.values()].filter(s =>
      s.tags.includes(capability) ||
      s.tools.some(t => t.name.includes(capability) || t.description.includes(capability))
    );
  }

  pruneStale(ttlMs = 300_000): string[] {
    const cutoff = Date.now() - ttlMs;
    const removed: string[] = [];
    for (const [id, s] of this.servers) {
      if (s.lastHeartbeat < cutoff) {
        s.healthy = false;
        removed.push(id);
      }
    }
    return removed;
  }

  toJSON() {
    return Object.fromEntries(this.servers);
  }
}
