/**
 * shared-test-fixtures — Reusable test mocks for OpenClaw workspace projects
 */

export class MockMemoryStore {
  private store = new Map<string, unknown>();
  get(key: string) { return this.store.get(key); }
  set(key: string, val: unknown) { this.store.set(key, val); }
  delete(key: string) { this.store.delete(key); }
  clear() { this.store.clear(); }
  has(key: string) { return this.store.has(key); }
}

export class MockLogger {
  logs: Array<{ level: string; msg: string; meta?: unknown }> = [];
  info(msg: string, meta?: unknown) { this.logs.push({ level: 'info', msg, meta }); }
  warn(msg: string, meta?: unknown) { this.logs.push({ level: 'warn', msg, meta }); }
  error(msg: string, meta?: unknown) { this.logs.push({ level: 'error', msg, meta }); }
  debug(msg: string, meta?: unknown) { this.logs.push({ level: 'debug', msg, meta }); }
  clear() { this.logs = []; }
}

export class MockBridgeDiscovery {
  private bridges = new Map<string, object>();
  register(id: string, bridge: object) { this.bridges.set(id, bridge); }
  get(id: string) { return this.bridges.get(id); }
  list() { return [...this.bridges.keys()]; }
  remove(id: string) { this.bridges.delete(id); }
}
