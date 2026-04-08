#!/usr/bin/env node
/**
 * OMC MCP Wrapper & Client
 * Unified interface for MCP server discovery, connection, and tool invocation.
 *
 * Inspired by Hermes Agent's Native MCP Client:
 *   - Stdio + HTTP transport support
 *   - Reconnection logic
 *   - Tool/prompt/resource discovery
 *   - Server-initiated sampling (bidirectional)
 *
 * Usage:
 *   node mcp-wrapper.mjs --discover              # discover available MCP servers
 *   node mcp-wrapper.mjs --connect server-id     # connect to a server
 *   node mcp-wrapper.mjs --list                  # list connected servers + tools
 *   node mcp-wrapper.mjs --invoke server-id tool --args '{}'  # call a tool
 *   node mcp-wrapper.mjs --servers-config        # show config file
 *
 * Architecture:
 *   - MCP servers configured in .omc/config/mcp-servers.json
 *   - State in .omc/state/mcp-client.json
 *   - Wraps npx/stdenv MCP CLI for stdio communication
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync } from 'fs';
import { spawn } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONFIG_DIR = resolve(__dirname, '../../.omc/config');
const CONFIG_FILE = resolve(CONFIG_DIR, 'mcp-servers.json');
const STATE_FILE = resolve(__dirname, '../state/mcp-client.json');

function parseArgs(argv) {
  const args = {};
  args._ = [];
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      if (key === 'args') { args[key] = argv[++i] || '{}'; continue; }
      if (key === 'invoke') { args.invoke = argv[++i]; continue; }
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    } else {
      args._.push(argv[i]);
    }
  }
  return args;
}

function readConfig() {
  if (!existsSync(CONFIG_FILE)) return { servers: [] };
  try { return JSON.parse(readFileSync(CONFIG_FILE, 'utf-8')); }
  catch { return { servers: [] }; }
}

function writeConfig(cfg) {
  if (!existsSync(CONFIG_DIR)) mkdirSync(CONFIG_DIR, { recursive: true });
  writeFileSync(CONFIG_FILE, JSON.stringify(cfg, null, 2), 'utf-8');
}

function readState() {
  if (!existsSync(STATE_FILE)) return { connected: {}, lastDiscover: null };
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return { connected: {}, lastDiscover: null }; }
}

function writeState(state) {
  if (!existsSync(dirname(STATE_FILE))) mkdirSync(dirname(STATE_FILE), { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

// ── Discover MCP servers ────────────────────────────────────────────────────
function discoverServers() {
  const config = readConfig();
  const servers = [];

  // From config
  for (const s of config.servers || []) {
    servers.push({
      id: s.id || s.name,
      name: s.name,
      command: s.cmd || s.command,
      args: s.args || s.args || [],
      env: s.env || {},
      type: 'configured',
      status: 'configured',
    });
  }

  // Auto-discover: check common locations
  const autoDiscover = [
    { name: 'Filesystem', cmd: 'npx', args: ['-y', '@modelcontextprotocol/server-filesystem', '.'] },
    { name: 'Git', cmd: 'npx', args: ['-y', '@modelcontextprotocol/server-git', '--repository', '.'] },
    { name: 'Memory', cmd: 'npx', args: ['-y', '@modelcontextprotocol/server-memory'] },
    { name: 'Slack', cmd: 'npx', args: ['-y', '@modelcontextprotocol/server-slack'] },
    { name: 'Brave Search', cmd: 'npx', args: ['-y', '@modelcontextprotocol/server-brave-search'] },
  ];

  for (const a of autoDiscover) {
    if (!servers.find(s => s.name === a.name)) {
      servers.push({ ...a, id: a.name.toLowerCase(), type: 'auto-discover', status: 'not-tested' });
    }
  }

  return servers;
}

// ── List connected servers ──────────────────────────────────────────────────
function listConnected() {
  const state = readState();
  const config = readConfig();
  const connected = [];

  for (const server of config.servers || []) {
    const id = server.id || server.name;
    const info = state.connected[id] || {};
    connected.push({
      id,
      name: server.name,
      command: server.command,
      tools: info.tools || [],
      prompts: info.prompts || [],
      resources: info.resources || [],
      connected: !!info.connected,
      lastConnected: info.lastConnected || null,
    });
  }

  return connected;
}

// ── Build MCP protocol message ──────────────────────────────────────────────
function buildRequest(method, params = {}) {
  return {
    jsonrpc: '2.0',
    id: Date.now(),
    method,
    params,
  };
}

// ── Connect to server (stdio) ────────────────────────────────────────────────
async function connectToServer(server) {
  return new Promise((resolve, reject) => {
    const env = { ...process.env, ...server.env };
    const proc = spawn(server.command, server.args || [], { env, stdio: ['pipe', 'pipe', 'pipe'] });

    let buffer = '';
    const tools = [];
    const prompts = [];
    const resources = [];

    proc.stdout.on('data', (data) => {
      buffer += data.toString();
      // Parse JSON-RPC responses
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (!line.trim()) continue;
        try {
          const msg = JSON.parse(line);
          if (msg.result?.tools) {
            for (const t of msg.result.tools) {
              tools.push({ name: t.name, description: t.description || '', inputSchema: t.inputSchema });
            }
          }
          if (msg.result?.prompts) prompts.push(...msg.result.prompts);
          if (msg.result?.resources) resources.push(...msg.result.resources);
        } catch { /* skip non-JSON */ }
      }
    });

    proc.stderr.on('data', (data) => {
      // Ignore stderr noise
    });

    proc.on('error', reject);
    proc.on('close', () => {
      resolve({ tools, prompts, resources });
    });

    // Send initialize
    const init = buildRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: { sampling: {} },
      clientInfo: { name: 'omc-mcp-wrapper', version: '1.0.0' },
    });
    proc.stdin.write(JSON.stringify(init) + '\n');

    // Send tools/list
    setTimeout(() => {
      const req = buildRequest('tools/list');
      proc.stdin.write(JSON.stringify(req) + '\n');
    }, 500);

    // Timeout
    setTimeout(() => {
      proc.kill();
      resolve({ tools, prompts, resources });
    }, 5000);
  });
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.discover) {
    const servers = discoverServers();
    console.log(`\n🔍 OMC MCP Server Discovery`);
    console.log(`  Found ${servers.length} servers\n`);
    for (const s of servers) {
      console.log(`  [${s.id}] ${s.name} (${s.type})`);
      console.log(`    Command: ${s.command} ${(s.args || []).join(' ')}`);
      if (s.status) console.log(`    Status: ${s.status}`);
    }
    console.log();
    return;
  }

  if (args.connect) {
    const config = readConfig();
    const server = (config.servers || []).find(s => (s.id || s.name) === args.connect);
    if (!server) {
      console.error(`Server not found: ${args.connect}`);
      console.error(`Available: ${(config.servers || []).map(s => s.id || s.name).join(', ')}`);
      return;
    }

    console.log(`Connecting to ${server.name}...`);
    const result = await connectToServer(server);

    // Update state
    const state = readState();
    state.connected[args.connect] = {
      ...result,
      connected: true,
      lastConnected: new Date().toISOString(),
    };
    writeState(state);

    console.log(`✅ Connected to ${server.name}`);
    console.log(`   Tools: ${result.tools.length}`);
    console.log(`   Prompts: ${result.prompts.length}`);
    console.log(`   Resources: ${result.resources.length}`);
    console.log();
    return;
  }

  if (args.list) {
    const connected = listConnected();
    const state = readState();
    console.log(`\n📡 OMC MCP Client`);
    console.log(`  Connected: ${connected.filter(c => c.connected).length}`);
    console.log(`  Total configured: ${connected.length}`);
    console.log(`  Last discover: ${state.lastDiscover || 'never'}\n`);

    for (const c of connected) {
      const status = c.connected ? '🟢' : '⚪️';
      console.log(`  ${status} ${c.name} (${c.id})`);
      console.log(`    Tools: ${c.tools.length} | Prompts: ${c.prompts.length} | Resources: ${c.resources.length}`);
      if (c.lastConnected) console.log(`    Last: ${c.lastConnected}`);
    }
    console.log();
    return;
  }

  if (args.invoke) {
    const [serverId, toolName] = args.invoke.split('/');
    console.log(`Invoking ${serverId}/${toolName}...`);
    console.log(`(Note: Full MCP invocation requires running server process)\n`);
    console.log(`Use --connect first to establish connection, then invoke via MCP protocol.`);
    return;
  }

  if (args['servers-config']) {
    const config = readConfig();
    console.log(`\n📋 MCP Servers Config`);
    console.log(`  File: ${CONFIG_FILE}`);
    console.log(`  Servers: ${config.servers?.length || 0}\n`);
    console.log(JSON.stringify(config, null, 2));
    console.log();
    return;
  }

  // Default: help
  console.log(`OMC MCP Wrapper & Client`);
  console.log(`Usage:`);
  console.log(`  --discover             Discover available MCP servers`);
  console.log(`  --connect server-id    Connect to a server`);
  console.log(`  --list                 List connected servers + tools`);
  console.log(`  --invoke server/tool   Invoke a tool`);
  console.log(`  --servers-config       Show servers config`);
  console.log(`\nConfig file: ${CONFIG_FILE}`);
  console.log(`Add servers with: node mcp-wrapper.mjs --add-server config.json`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
