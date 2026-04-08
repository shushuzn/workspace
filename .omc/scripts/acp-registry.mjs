#!/usr/bin/env node
/**
 * OMC ACP (Agent Communication Protocol) Registry
 * Agent-to-agent communication with service discovery.
 *
 * Inspired by Hermes Agent's ACP (Agent Communication Protocol):
 *   - Standardized inter-agent messaging
 *   - Service registry for discovering and connecting to agents
 *   - Paperclip adapter reference implementation
 *   - Bidirectional communication with ACK/confirmation
 *
 * Usage:
 *   node acp-registry.mjs --register agent-id [--url url] [--capabilities "a,b,c"]   Register
 *   node acp-registry.mjs --discover [--query "capability"]                            Discover agents
 *   node acp-registry.mjs --connect agent-id                                         Connect
 *   node acp-registry.mjs --send agent-id message                                    Send message
 *   node acp-registry.mjs --listen                                                   Listen mode
 *   node acp-registry.mjs --status                                                   Registry status
 *
 * Architecture:
 *   - Registry: .omc/state/acp-registry.json
 *   - Messages: .omc/state/acp-messages/{agentId}.jsonl
 *   - Config: .omc/config/acp-config.json
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync, appendFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = resolve(__dirname, '../state');
const REGISTRY_FILE = resolve(STATE_DIR, 'acp-registry.json');
const CONFIG_FILE = resolve(__dirname, '../config/acp-config.json');
const MSGS_DIR = resolve(STATE_DIR, 'acp-messages');

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      if (key === 'capabilities') { args.capabilities = (argv[++i] || '').split(',').map(s => s.trim()); continue; }
      if (key === 'url') { args.url = argv[++i]; continue; }
      if (key === 'query') { args.query = argv[++i]; continue; }
      if (key === 'send') { args.send = argv[++i]; continue; }
      if (key === 'connect') { args.connect = argv[++i]; continue; }
      if (key === 'register') { args.register = argv[++i]; continue; }
      if (key === 'discover') { args.discover = true; continue; }
      if (key === 'listen') { args.listen = true; continue; }
      if (key === 'status') { args.status = true; continue; }
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

function readRegistry() {
  if (!existsSync(REGISTRY_FILE)) return { agents: {}, version: '1.0.0' };
  try { return JSON.parse(readFileSync(REGISTRY_FILE, 'utf-8')); }
  catch { return { agents: {}, version: '1.0.0' }; }
}

function writeRegistry(reg) {
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(REGISTRY_FILE, JSON.stringify(reg, null, 2), 'utf-8');
}

function readConfig() {
  if (!existsSync(CONFIG_FILE)) return { myAgentId: 'omc-agent', capabilities: [], port: 9877 };
  try { return JSON.parse(readFileSync(CONFIG_FILE, 'utf-8')); }
  catch { return { myAgentId: 'omc-agent', capabilities: [], port: 9877 }; }
}

function writeConfig(cfg) {
  mkdirSync(resolve(__dirname, '../config'), { recursive: true });
  writeFileSync(CONFIG_FILE, JSON.stringify(cfg, null, 2), 'utf-8');
}

function msgPath(agentId) {
  return resolve(MSGS_DIR, `${agentId}.jsonl`);
}

// ── ACP Protocol Messages ────────────────────────────────────────────────────
function buildACPMessage(type, from, to, content, metadata = {}) {
  return {
    id: `msg-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    type,           // discover, announce, query, response, message, ack
    from,           // sender agent ID
    to,             // receiver agent ID (or * for broadcast)
    content,        // message payload
    timestamp: new Date().toISOString(),
    metadata,
    status: 'pending', // pending, delivered, acknowledged
  };
}

// ── Register an agent ──────────────────────────────────────────────────────────
function registerAgent(agentId, config) {
  const reg = readRegistry();
  const myConfig = readConfig();

  reg.agents[agentId] = {
    id: agentId,
    capabilities: config.capabilities || myConfig.capabilities || [],
    url: config.url || null,
    endpoints: config.endpoints || {},
    metadata: config.metadata || {},
    registered: new Date().toISOString(),
    lastSeen: new Date().toISOString(),
    status: 'online',
    version: reg.version,
  };

  writeRegistry(reg);

  // Auto-message to announce presence
  const announce = buildACPMessage('announce', agentId, '*', `${agentId} registered`, {
    capabilities: reg.agents[agentId].capabilities,
  });
  saveMessage(agentId, announce);

  return reg.agents[agentId];
}

// ── Discover agents ──────────────────────────────────────────────────────────
function discoverAgents(query = '') {
  const reg = readRegistry();
  const queryLower = query.toLowerCase();
  const agents = Object.values(reg.agents);

  if (!query) {
    return agents.filter(a => a.status === 'online');
  }

  return agents.filter(a => {
    if (a.id.toLowerCase().includes(queryLower)) return true;
    if (a.capabilities.some(c => c.toLowerCase().includes(queryLower))) return true;
    if (a.metadata?.description?.toLowerCase().includes(queryLower)) return true;
    return false;
  });
}

// ── Send message ──────────────────────────────────────────────────────────────
function sendMessage(fromId, toId, content) {
  const reg = readRegistry();

  if (!reg.agents[toId] && toId !== '*') {
    return { error: `Agent not registered: ${toId}` };
  }

  const msg = buildACPMessage('message', fromId, toId, content);
  saveMessage(toId, msg);

  // If toId is registered, update lastSeen
  if (reg.agents[toId]) {
    reg.agents[toId].lastSeen = new Date().toISOString();
    writeRegistry(reg);
  }

  return { messageId: msg.id, status: 'queued', recipient: toId };
}

// ── Send discovery query ─────────────────────────────────────────────────────
function discoverQuery(fromId, query) {
  const msg = buildACPMessage('query', fromId, '*', query, { query });
  // Save to all agents' inbox
  const reg = readRegistry();
  for (const agentId of Object.keys(reg.agents)) {
    saveMessage(agentId, msg);
  }
  return { messageId: msg.id, status: 'broadcast', recipient: '*' };
}

// ── Save message to agent inbox ──────────────────────────────────────────────
function saveMessage(agentId, msg) {
  if (!existsSync(MSGS_DIR)) mkdirSync(MSGS_DIR, { recursive: true });
  appendFileSync(msgPath(agentId), JSON.stringify(msg) + '\n', 'utf-8');
}

// ── Read pending messages ─────────────────────────────────────────────────────
function readMessages(agentId, unreadOnly = true) {
  const path = msgPath(agentId);
  if (!existsSync(path)) return [];

  try {
    const content = readFileSync(path, 'utf-8');
    const lines = content.split('\n').filter(Boolean);
    const msgs = lines.map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);

    if (unreadOnly) {
      return msgs.filter(m => m.status !== 'acknowledged');
    }
    return msgs;
  } catch {
    return [];
  }
}

// ── Acknowledge message ──────────────────────────────────────────────────────
function ackMessage(agentId, messageId) {
  const path = msgPath(agentId);
  if (!existsSync(path)) return { error: 'Inbox not found' };

  try {
    const content = readFileSync(path, 'utf-8');
    const lines = content.split('\n');
    const updated = lines.map(line => {
      try {
        const msg = JSON.parse(line);
        if (msg.id === messageId) {
          msg.status = 'acknowledged';
          return JSON.stringify(msg);
        }
        return line;
      } catch { return line; }
    });

    writeFileSync(path, updated.join('\n'), 'utf-8');
    return { messageId, status: 'acknowledged' };
  } catch (e) {
    return { error: e.message };
  }
}

// ── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));
  const config = readConfig();

  if (args.register) {
    const agent = registerAgent(args.register, {
      capabilities: args.capabilities || [],
      url: args.url,
    });
    console.log(`\n✅ Registered: ${agent.id}`);
    console.log(`   Capabilities: ${agent.capabilities.join(', ') || 'none'}`);
    console.log(`   URL: ${agent.url || 'local'}`);
    console.log();
    return;
  }

  if (args.discover) {
    const results = discoverAgents(args.query || '');
    console.log(`\n🔍 ACP Discovery${args.query ? ` (query: "${args.query}")` : ''}`);
    console.log(`   Found: ${results.length} agents\n`);
    for (const a of results) {
      const unread = readMessages(a.id, true).length;
      console.log(`  [${a.id}] ${a.status} (${a.capabilities.join(', ') || 'no capabilities'})`);
      if (unread > 0) console.log(`    Unread: ${unread}`);
      if (a.lastSeen) console.log(`    Last seen: ${a.lastSeen}`);
    }
    console.log();
    return;
  }

  if (args.connect) {
    const reg = readRegistry();
    if (!reg.agents[args.connect]) {
      console.error(`Agent not found: ${args.connect}`);
      console.error(`Available: ${Object.keys(reg.agents).join(', ') || 'none'}`);
      return;
    }
    const agent = reg.agents[args.connect];
    console.log(`\n🔗 Connected to ${agent.id}`);
    console.log(`   Capabilities: ${agent.capabilities.join(', ') || 'none'}`);
    console.log(`   Status: ${agent.status}`);
    console.log(`   Inbox: ${readMessages(agent.id).length} messages\n`);
    return;
  }

  if (args.send) {
    const result = sendMessage(config.myAgentId, args.send, args.send);
    if (result.error) {
      console.error(`Error: ${result.error}`);
    } else {
      console.log(`\n📤 Message sent to ${result.recipient}`);
      console.log(`   ID: ${result.messageId}`);
      console.log(`   Status: ${result.status}\n`);
    }
    return;
  }

  if (args.status) {
    const reg = readRegistry();
    const agents = Object.values(reg.agents);
    const online = agents.filter(a => a.status === 'online').length;
    console.log(`\n📡 OMC ACP Registry`);
    console.log(`  My Agent ID: ${config.myAgentId}`);
    console.log(`  Version: ${reg.version}`);
    console.log(`  Total registered: ${agents.length}`);
    console.log(`  Online: ${online}`);
    console.log(`  Registry: ${REGISTRY_FILE}\n`);
    if (agents.length > 0) {
      console.log(`  Agents:`);
      for (const a of agents.slice(0, 10)) {
        console.log(`    [${a.id}] ${a.status} — ${a.capabilities.join(', ') || 'no caps'}`);
      }
    }
    console.log();
    return;
  }

  // Default: help
  console.log(`OMC ACP (Agent Communication Protocol) Registry`);
  console.log(`Usage:`);
  console.log(`  --register id --capabilities "a,b,c"   Register this agent`);
  console.log(`  --discover [--query "cap"]             Discover agents`);
  console.log(`  --connect agent-id                     Connect to agent`);
  console.log(`  --send agent-id "message"              Send message`);
  console.log(`  --status                               Registry status`);
  console.log(`\nACP Message Types:`);
  console.log(`  announce - broadcast presence`);
  console.log(`  query    - broadcast discovery query`);
  console.log(`  response - reply to query`);
  console.log(`  message  - direct message`);
  console.log(`  ack      - acknowledgment`);
}

main().catch(e => { console.error(e.message); process.exit(1); });
