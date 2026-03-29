/**
 * PythonMCPClient - Spawns a Python MCP server as a child process
 * and exposes its tools as JavaScript methods via stdio JSON-RPC.
 */

import { spawn } from 'child_process';
import { EventEmitter } from 'events';

export class PythonMCPClient extends EventEmitter {
  /**
   * @param {Object} options
   * @param {string} options.command  - Python executable or path to server.py
   * @param {string[]} options.args - Command line arguments
   * @param {string} options.cwd   - Working directory
   */
  constructor(options = {}) {
    super();
    this.command = options.command || 'python';
    this.args = options.args || ['-m', 'src.server'];
    this.cwd = options.cwd || process.cwd();
    this._proc = null;
    this._reqId = 0;
    this._pending = new Map(); // reqId -> { resolve, reject }
    this._ready = false;
    this._readyPromise = null;
    this._tools = new Map();   // name -> toolDef
    this._requestQueue = [];
  }

  /** Start the Python subprocess and initialize MCP handshake */
  async start() {
    if (this._proc) return;

    this._readyPromise = this._waitForReady();

    this._proc = spawn(this.command, this.args, {
      cwd: this.cwd,
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true
    });

    this._proc.stdout.on('data', (data) => this._handleStdout(data.toString()));
    this._proc.stderr.on('data', (data) => {
      // Forward stderr to parent logger if present
      this.emit('error', data.toString().trim());
    });
    this._proc.on('exit', (code) => {
      this.emit('exit', code);
      this._proc = null;
    });

    // MCP handshake: initialize
    await this._send('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'a2a-router', version: '1.0.0' }
    });

    // Send initialized notification (no response expected)
    this._send('notifications/initialized', {});

    await this._readyPromise;
    this._ready = true;

    // Fetch tool list
    await this._listTools();

    return this;
  }

  /** Stop the subprocess */
  stop() {
    if (this._proc) {
      this._proc.kill();
      this._proc = null;
    }
    this._ready = false;
  }

  /** Call a tool by name with input arguments */
  async callTool(toolName, input = {}) {
    if (!this._ready) await this._readyPromise;

    return this._send('tools/call', {
      name: toolName,
      arguments: input
    });
  }

  /** Get list of all available tools */
  async _listTools() {
    const result = await this._send('tools/list', {});
    const tools = result.tools || [];
    this._tools.clear();
    for (const t of tools) {
      this._tools.set(t.name, t);
    }
    return this._tools;
  }

  get tools() {
    return Array.from(this._tools.values());
  }

  getTool(name) {
    return this._tools.get(name);
  }

  // ─── Private ────────────────────────────────────────────────

  _waitForReady() {
    return new Promise((resolve) => {
      if (this._ready) return resolve();
      this.once('ready', resolve);
    });
  }

  _send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const id = ++this._reqId;
      const payload = { jsonrpc: '2.0', id, method, params };
      this._pending.set(id, { resolve, reject });

      if (!this._proc || !this._proc.stdin) {
        reject(new Error('Process not running'));
        return;
      }

      this._proc.stdin.write(JSON.stringify(payload) + '\n');

      // Timeout: 60s
      const timeout = setTimeout(() => {
        if (this._pending.has(id)) {
          this._pending.delete(id);
          reject(new Error(`MCP request ${method} timed out`));
        }
      }, 60000);

      const entry = this._pending.get(id);
      entry.resolve = (val) => { clearTimeout(timeout); resolve(val); };
      entry.reject = (err) => { clearTimeout(timeout); reject(err); };
    });
  }

  _handleStdout(data) {
    // May receive multiple JSON lines concatenated
    const lines = data.split('\n').filter(l => l.trim());
    for (const line of lines) {
      try {
        const msg = JSON.parse(line);
        this._handleMessage(msg);
      } catch {
        // Ignore non-JSON lines (e.g., python print statements)
      }
    }
  }

  _handleMessage(msg) {
    // Handle responses (has id + result/error)
    if (msg.id !== undefined) {
      const pending = this._pending.get(msg.id);
      if (pending) {
        this._pending.delete(msg.id);
        if (msg.error) {
          pending.reject(new Error(msg.error.message || msg.error.code));
        } else {
          pending.resolve(msg.result);
        }
      }
      return;
    }

    // Handle notifications (no id)
    if (msg.method) {
      // Emitting raw events for extensibility
      this.emit(`notification:${msg.method}`, msg.params);

      // Check for initial connection ready
      if (msg.method === 'notifications/initialized') {
        this._ready = true;
        this.emit('ready');
      }

      // Tool list changed
      if (msg.method === 'notifications/tools/list_changed') {
        this._listTools().then(() => {
          this.emit('toolsChanged');
        });
      }
    }
  }
}

export default PythonMCPClient;
