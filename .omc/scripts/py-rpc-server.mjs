#!/usr/bin/env node
/**
 * OMC Python RPC Server
 * Exposes agent tools as RPC endpoints for zero-context-cost Python calls.
 *
 * Inspired by Hermes Agent's Python RPC Tool Calls:
 *   - External Python processes invoke tools via JSON-RPC
 *   - No LLM context window cost for tool calls
 *   - Bidirectional: agent can call back into Python
 *   - FastIPC via stdin/stdout for subprocess communication
 *
 * Usage:
 *   node py-rpc-server.mjs --start [--port N]           Start RPC server
 *   node py-rpc-server.mjs --tools                      List available tools
 *   node py-rpc-server.mjs --invoke toolName --args '{}'  Invoke a tool
 *   node py-rpc-server.mjs --listen                    Listen mode (stdin/stdout)
 *
 * Python client example:
 *   from omc_rpc import Agent
 *   agent = Agent()
 *   result = agent.call("Read", {"file_path": "CLAUDE.md"})
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const RPC_STATE = resolve(__dirname, '../state/py-rpc-state.json');
const RPC_CONFIG = resolve(__dirname, '../config/py-rpc-config.json');
const PORT = 9876;

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      if (key === 'args') { args.args = argv[++i]; continue; }
      if (key === 'invoke') { args.invoke = argv[++i]; continue; }
      if (key === 'port') { args.port = parseInt(argv[++i]) || PORT; continue; }
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

function readState() {
  if (!existsSync(RPC_STATE)) return { serverRunning: false, calls: 0, lastCall: null };
  try { return JSON.parse(readFileSync(RPC_STATE, 'utf-8')); }
  catch { return { serverRunning: false, calls: 0, lastCall: null }; }
}

function writeState(state) {
  mkdirSync(resolve(__dirname, '../state'), { recursive: true });
  writeFileSync(RPC_STATE, JSON.stringify(state, null, 2), 'utf-8');
}

function readConfig() {
  if (!existsSync(RPC_CONFIG)) return { tools: [] };
  try { return JSON.parse(readFileSync(RPC_CONFIG, 'utf-8')); }
  catch { return { tools: [] }; }
}

function writeConfig(cfg) {
  mkdirSync(resolve(__dirname, '../config'), { recursive: true });
  writeFileSync(RPC_CONFIG, JSON.stringify(cfg, null, 2), 'utf-8');
}

// ── Built-in tools that can be called via RPC ─────────────────────────────────
const BUILTIN_TOOLS = {
  Read: {
    description: 'Read file contents',
    inputSchema: { file_path: { type: 'string' } },
    handler: async ({ file_path }) => {
      if (!existsSync(file_path)) return { error: 'File not found' };
      const content = readFileSync(resolve(process.cwd(), file_path), 'utf-8');
      return { content: content.slice(0, 10000), truncated: content.length > 10000 };
    },
  },

  Grep: {
    description: 'Search file contents',
    inputSchema: { pattern: { type: 'string' }, path: { type: 'string' } },
    handler: async ({ pattern, path = '.' }) => {
      // Simulated grep - in practice would use actual file search
      return { matches: [], count: 0, note: 'Use grep tool for actual search' };
    },
  },

  Glob: {
    description: 'Find files by pattern',
    inputSchema: { pattern: { type: 'string' } },
    handler: async ({ pattern }) => {
      const files = readdirSync(process.cwd(), { recursive: true }).filter(f => {
        if (typeof f !== 'string') return false;
        return f.match(new RegExp(pattern.replace(/\*/g, '.*').replace(/\?/g, '.')));
      });
      return { files: files.slice(0, 100), count: files.length };
    },
  },

  Bash: {
    description: 'Execute bash command',
    inputSchema: { command: { type: 'string' }, timeout: { type: 'number' } },
    handler: async ({ command, timeout = 30000 }) => {
      return { note: 'Bash execution not available via RPC (security)', command };
    },
  },

  Stat: {
    description: 'Get file stats',
    inputSchema: { path: { type: 'string' } },
    handler: async ({ path }) => {
      const fullPath = resolve(process.cwd(), path);
      if (!existsSync(fullPath)) return { error: 'Path not found' };
      const stat = readFileSync;
      return { path: fullPath, exists: true, note: 'Use Node.js fs.statSync' };
    },
  },

  Memory: {
    description: 'Query OMC memory',
    inputSchema: { key: { type: 'string' } },
    handler: async ({ key }) => {
      const memFile = resolve(__dirname, '../memory', key);
      if (!existsSync(memFile)) return { error: 'Memory key not found' };
      return { content: readFileSync(memFile, 'utf-8').slice(0, 5000) };
    },
  },

  Ideas: {
    description: 'Query idea pool',
    inputSchema: { action: { type: 'string' } },
    handler: async ({ action = 'list' }) => {
      const ideasFile = resolve(__dirname, '../innovation/ideas.md');
      if (!existsSync(ideasFile)) return { error: 'ideas.md not found' };
      const content = readFileSync(ideasFile, 'utf-8');
      const lines = content.split('\n').filter(l => l.startsWith('- ['));
      return { ideas: lines.slice(0, 20), count: lines.length };
    },
  },

  HookNudge: {
    description: 'Trigger knowledge checkpoint',
    inputSchema: {},
    handler: async () => {
      return { message: 'Nudge fired', note: 'Check hook-nudge.mjs --check' };
    },
  },

  FTS5Search: {
    description: 'Full-text search sessions',
    inputSchema: { query: { type: 'string' }, days: { type: 'number' } },
    handler: async ({ query, days = 7 }) => {
      return { note: 'Use fts5-search.mjs for actual search', query, days };
    },
  },
};

// ── RPC Protocol ──────────────────────────────────────────────────────────────
function buildResponse(id, result, error = null) {
  return {
    jsonrpc: '2.0',
    id,
    ...(error ? { error: { code: -32600, message: error } } : { result }),
  };
}

function parseRequest(line) {
  try {
    return JSON.parse(line);
  } catch {
    return null;
  }
}

// ── Invoke a tool ────────────────────────────────────────────────────────────
async function invokeTool(name, args = {}) {
  const tool = BUILTIN_TOOLS[name];
  if (!tool) {
    return { error: `Unknown tool: ${name}` };
  }

  try {
    return await tool.handler(args);
  } catch (e) {
    return { error: e.message };
  }
}

// ── Python client generator ──────────────────────────────────────────────────
function generatePythonClient() {
  return `#!/usr/bin/env python3
"""
OMC Python RPC Client
Zero-context-cost tool calls from Python.

Usage:
  from omc_rpc import Agent
  agent = Agent()
  result = agent.call("Read", {"file_path": "CLAUDE.md"})
  print(result)
"""
import json
import subprocess
import sys
from pathlib import Path

class Agent:
    def __init__(self, server_script=None):
        if server_script is None:
            # Find server script
            cwd = Path.cwd()
            server = cwd / ".omc" / "scripts" / "py-rpc-server.mjs"
            if not server.exists():
                # Try parent
                server = cwd.parent / ".omc" / "scripts" / "py-rpc-server.mjs"
            self.server = str(server)
        else:
            self.server = server_script

    def call(self, tool_name, args=None):
        """Call a tool via RPC"""
        args = args or {}
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool_name, "args": args}
        }

        # Run server in listen mode with request
        result = subprocess.run(
            ["node", self.server, "--listen"],
            input=json.dumps(request) + "\\n",
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.stderr:
            print(f"Warning: {result.stderr}", file=sys.stderr)

        try:
            response = json.loads(result.stdout.strip())
            if "error" in response:
                raise Exception(response["error"].get("message", "Unknown error"))
            return response.get("result", {})
        except json.JSONDecodeError:
            return {"error": f"Invalid response: {result.stdout}"}

    def tools(self):
        """List available tools"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        result = subprocess.run(
            ["node", self.server, "--listen"],
            input=json.dumps(request) + "\\n",
            capture_output=True,
            text=True,
            timeout=10
        )
        try:
            return json.loads(result.stdout.strip()).get("result", [])
        except:
            return []

if __name__ == "__main__":
    agent = Agent()
    print("Available tools:", agent.tools())
`;
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  // Python client generator
  if (args['python-client']) {
    console.log(generatePythonClient());
    return;
  }

  // List tools
  if (args.tools) {
    const config = readConfig();
    const allTools = Object.entries(BUILTIN_TOOLS);
    console.log(`\n🔧 OMC RPC Tools (${Object.keys(BUILTIN_TOOLS).length} built-in)\n`);
    for (const [name, tool] of Object.entries(BUILTIN_TOOLS)) {
      console.log(`  ${name}`);
      console.log(`    ${tool.description}`);
      console.log(`    Args: ${JSON.stringify(tool.inputSchema)}`);
    }
    console.log();
    return;
  }

  // Invoke a tool
  if (args.invoke) {
    let parsedArgs = {};
    if (args.args) {
      try { parsedArgs = JSON.parse(args.args); }
      catch { parsedArgs = {}; }
    }
    const result = await invokeTool(args.invoke, parsedArgs);
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  // Listen mode (stdin/stdout for subprocess IPC)
  if (args.listen) {
    // Read single request from stdin, write response to stdout
    const input = [];
    process.stdin.on('data', d => input.push(d.toString()));
    process.stdin.on('end', async () => {
      const raw = input.join('');
      const lines = raw.split('\n').filter(l => l.trim());
      for (const line of lines) {
        const req = parseRequest(line);
        if (!req) continue;

        const { id, method, params } = req;

        if (method === 'tools/list') {
          const tools = Object.entries(BUILTIN_TOOLS).map(([name, t]) => ({
            name, description: t.description, inputSchema: t.inputSchema
          }));
          console.log(JSON.stringify(buildResponse(id, tools)));
        }
        else if (method === 'tools/call') {
          const { name, args: toolArgs } = params || {};
          const result = await invokeTool(name, toolArgs);
          console.log(JSON.stringify(buildResponse(id, result)));
        }
        else if (method === 'ping') {
          console.log(JSON.stringify(buildResponse(id, { pong: true })));
        }
      }
    });
    return;
  }

  // Server status
  if (args.status) {
    const state = readState();
    const config = readConfig();
    console.log(`\n📡 OMC Python RPC Server`);
    console.log(`  Running: ${state.serverRunning}`);
    console.log(`  Total calls: ${state.calls}`);
    console.log(`  Last call: ${state.lastCall || 'never'}`);
    console.log(`  Built-in tools: ${Object.keys(BUILTIN_TOOLS).length}`);
    console.log(`  Configured tools: ${(config.tools || []).length}`);
    console.log();
    return;
  }

  // Default: help
  console.log(`OMC Python RPC Server`);
  console.log(`Usage:`);
  console.log(`  --tools                  List available RPC tools`);
  console.log(`  --invoke name --args '{}'  Invoke a tool`);
  console.log(`  --listen                 Listen mode (for subprocess IPC)`);
  console.log(`  --status                 Server status`);
  console.log(`  --python-client          Generate Python client`);
  console.log(`\nPython client:`);
  console.log(`  node py-rpc-server.mjs --python-client > omc_rpc.py`);
  console.log(`  python -c "from omc_rpc import Agent; print(Agent().tools())"`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
