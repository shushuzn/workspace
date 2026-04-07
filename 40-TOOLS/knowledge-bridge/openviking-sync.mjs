#!/usr/bin/env node
/**
 * openviking-sync.mjs — Sync OpenViking sessions → Knowledge Bridge graph
 *
 * Bidirectional sync bridge:
 *   - Pulls sessions/messages from OpenViking MCP server
 *   - Converts to knowledge-bridge node/edge format
 *   - Appends to knowledge-bridge data/pla-knowledge-graph.json
 *   - Optionally creates relations (link sessions by shared topics)
 *
 * Usage:
 *   node openviking-sync.mjs [--limit 20] [--dry-run] [--clear]
 *
 * Env vars:
 *   VIKING_BASE_URL   — OpenViking server (default: http://127.0.0.1:1933)
 *   VIKING_API_KEY    — optional API key
 *   VIKING_ACCOUNT    — account ID (default: default)
 *   VIKING_USER       — user ID (default: default)
 */

import { readFileSync, existsSync, writeFileSync, appendFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ─── Args ─────────────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
function getArg(flag, fallback) {
  const idx = args.indexOf(flag);
  return idx >= 0 ? args[idx + 1] : fallback;
}
function hasArg(flag) { return args.includes(flag); }

const limit = parseInt(getArg('--limit', '50'));
const dryRun = hasArg('--dry-run');
const clear = hasArg('--clear');
const verbose = hasArg('--verbose');

// ─── Config ────────────────────────────────────────────────────────────────────

const VIKING_BASE = process.env.VIKING_BASE_URL || 'http://127.0.0.1:1933';
const VIKING_API_KEY = process.env.VIKING_API_KEY || '';
const VIKING_ACCOUNT = process.env.VIKING_ACCOUNT || 'default';
const VIKING_USER = process.env.VIKING_USER || 'default';

const GRAPH_PATH = join(__dirname, 'data', 'pla-knowledge-graph.json');
const SYNC_LOG_PATH = join(__dirname, 'data', 'openviking-sync.log');

// ─── HTTP helpers (curl via subprocess for reliability) ───────────────────────

import { spawn } from 'child_process';
import { once } from 'events';

function curlJSON(method, path, body = null) {
  return new Promise((resolve, reject) => {
    const cmd = ['curl', '-s', '--noproxy', '*', '-X', method, `${VIKING_BASE}${path}`,
      '-H', 'Content-Type: application/json'];
    if (VIKING_API_KEY) cmd.push('-H', `X-API-Key: ${VIKING_API_KEY}`);
    cmd.push('-H', `X-OpenViking-Account: ${VIKING_ACCOUNT}`);
    cmd.push('-H', `X-OpenViking-User: ${VIKING_USER}`);
    if (body) cmd.push('-d', JSON.stringify(body));

    const proc = spawn('curl', cmd);
    let stdout = '', stderr = '';
    proc.stdout.on('data', d => stdout += d);
    proc.stderr.on('data', d => stderr += d);
    proc.on('close', async (code) => {
      if (code !== 0) {
        reject(new Error(`curl exit ${code}: ${stderr.trim()}`));
      } else {
        try {
          resolve(stdout.trim() ? JSON.parse(stdout) : {});
        } catch (e) {
          resolve(stdout);
        }
      }
    });
  });
}

// ─── Fetch OpenViking data ────────────────────────────────────────────────────

async function fetchSessions(limit) {
  const resp = await curlJSON('GET', '/api/v1/sessions');
  const sessions = (resp.result || resp || []);
  return sessions.slice(0, limit);
}

async function fetchSessionMessages(sessionId) {
  const resp = await curlJSON('GET', `/api/v1/sessions/${sessionId}/messages`);
  return (resp.result || resp || []);
}

// ─── Graph transformation ─────────────────────────────────────────────────────

/**
 * Convert OpenViking session + messages into knowledge-bridge nodes/edges.
 * Returns { nodes: [...], edges: [...] }
 */
function sessionToGraph(session, messages) {
  const nodes = [];
  const edges = [];

  const sid = session.session_id || session.id || `session:${Date.now()}`;
  const sessionLabel = `Session ${sid.slice(0, 8)} (${session.project || 'default'})`;
  const sessionNodeId = `ov:session:${sid}`;

  // Session metadata node
  nodes.push({
    id: sessionNodeId,
    label: sessionLabel,
    domain: 'session',
    description: `OpenViking session • ${messages.length} messages • ${new Date(session.created_at || session.createdAt || Date.now()).toLocaleString()}`,
    type: 'openviking_session',
    session_id: sid,
    project: session.project || 'default',
    message_count: messages.length,
    createdAt: session.created_at || session.createdAt || new Date().toISOString(),
    tags: ['openviking', 'session']
  });

  // Create message nodes and connect them
  let prevMsgNodeId = sessionNodeId;
  messages.forEach((msg, idx) => {
    const msgId = `ov:msg:${sid}:${idx}`;
    const role = msg.role || 'unknown';
    const preview = (msg.content || '').slice(0, 100).replace(/\n/g, ' ');
    nodes.push({
      id: msgId,
      label: `${role === 'user' ? '👤' : '🤖'} ${role}`,
      domain: 'conversation',
      description: preview,
      type: 'openviking_message',
      role,
      content: msg.content || '',
      message_index: idx,
      session_id: sid,
      createdAt: msg.timestamp || msg.created_at || new Date().toISOString(),
      tags: ['openviking', 'message', role]
    });

    // Linear chain: session → msg1 → msg2 → ...
    edges.push({
      source: prevMsgNodeId,
      target: msgId,
      relation: 'contains',
      weight: 1.0
    });
    prevMsgNodeId = msgId;
  });

  // Extract topic keywords → link to keyword nodes
  const allText = messages.map(m => m.content || '').join(' ').toLowerCase();
  const stopWords = new Set(['the','a','an','and','or','but','in','on','at','to','for','of','with','by','from','as','is','was','are','were','be','have','has','had','this','that','these','those','which','what','who','when','where','how','not','all','each','every','some','any','no','than','then','more','most','also','very','just','only','own','same','so','too','can','will','would','could','should','may','might','must','shall','ll','re','ve','s']);
  const keywords = allText
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 4 && !stopWords.has(w))
    .slice(0, 8);

  keywords.forEach((kw, idx) => {
    const kwId = `kw:ov:${sid}:${kw}`;
    nodes.push({
      id: kwId,
      label: kw,
      domain: 'keyword',
      description: `Keyword from session ${sid.slice(0, 8)}`,
      type: 'keyword',
      tags: ['keyword', 'openviking']
    });
    edges.push({
      source: sessionNodeId,
      target: kwId,
      relation: 'has_keyword',
      weight: 0.5
    });
  });

  return { nodes, edges, meta: { sessionId: sid, messageCount: messages.length, keywords } };
}

// ─── Graph file handling ───────────────────────────────────────────────────────

function loadGraph() {
  if (!existsSync(GRAPH_PATH)) {
    return { nodes: {}, edges: [], analogyBank: [], _meta: { version: '1.0', syncedFrom: [] } };
  }
  try {
    const raw = JSON.parse(readFileSync(GRAPH_PATH, 'utf8'));
    // Normalize: nodes can be object or array-of-[id,obj]
    let nodesObj = raw.nodes;
    if (Array.isArray(nodesObj)) {
      // Convert [id,{...}] array to {id:{...}}
      const conv = {};
      for (const item of nodesObj) {
        if (Array.isArray(item) && item[1]) {
          conv[item[0]] = item[1];
        } else if (item && item.id) {
          conv[item.id] = item;
        }
      }
      nodesObj = conv;
    }
    return {
      nodes: nodesObj,
      edges: raw.edges || [],
      analogyBank: raw.analogyBank || [],
      _meta: raw._meta || { version: '1.0', syncedFrom: [] }
    };
  } catch (e) {
    console.error(`[WARN] Failed to parse graph, starting fresh: ${e.message}`);
    return { nodes: {}, edges: [], analogyBank: [], _meta: { version: '1.0', syncedFrom: [] } };
  }
}

function saveGraph(graph) {
  // Convert nodes object to array format for compatibility
  const nodesArray = Object.values(graph.nodes);
  const out = {
    nodes: nodesArray,
    edges: graph.edges,
    analogyBank: graph.analogyBank,
    _meta: graph._meta
  };
  writeFileSync(GRAPH_PATH, JSON.stringify(out, null, 2), 'utf-8');
}

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  appendFileSync(SYNC_LOG_PATH, line, 'utf-8');
  if (verbose) console.log(msg);
}

// ─── Main sync ─────────────────────────────────────────────────────────────────

async function main() {
  console.log('='.repeat(60));
  console.log('OpenViking → Knowledge Bridge Sync');
  console.log(`OpenViking: ${VIKING_BASE}`);
  console.log(`Graph: ${GRAPH_PATH}`);

  if (dryRun) console.log('[DRY-RUN] No changes will be written');
  if (clear) console.log('[CLEAR] Will remove all openviking nodes before sync');

  // Load existing graph
  const graph = loadGraph();
  console.log(`Loaded: ${Object.keys(graph.nodes).length} nodes, ${graph.edges.length} edges`);

  // Clear existing openviking nodes if requested
  if (clear) {
    const before = Object.keys(graph.nodes).length;
    let cleared = 0;
    for (const [id, node] of Object.entries(graph.nodes)) {
      if (node.tags?.includes('openviking')) {
        delete graph.nodes[id];
        cleared++;
      }
    }
    // Remove edges connected to cleared nodes
    graph.edges = graph.edges.filter(e =>
      graph.nodes[e.source as string] && graph.nodes[e.target as string]
    );
    console.log(`[CLEAR] Removed ${cleared} openviking nodes (${before} → ${Object.keys(graph.nodes).length})`);
  }

  // Fetch sessions
  console.log(`Fetching up to ${limit} sessions from OpenViking...`);
  const sessions = await fetchSessions(limit);
  console.log(`Got ${sessions.length} sessions`);

  if (sessions.length === 0) {
    console.log('No sessions found — nothing to sync');
    if (!dryRun) saveGraph(graph);
    return;
  }

  // Track existing openviking nodes to avoid duplicates
  const existingOvNodes = new Set();
  for (const [id, node] of Object.entries(graph.nodes)) {
    if (node.tags?.includes('openviking')) {
      existingOvNodes.add(node.session_id || node.id);
    }
  }
  console.log(`Existing openviking sessions in graph: ${existingOvNodes.size}`);

  // Process each session
  let newSessions = 0, skipped = 0;
  for (const sess of sessions) {
    const sid = sess.session_id || sess.id;
    if (!sid) {
      if (verbose) console.log('[SKIP] Session without ID');
      skipped++;
      continue;
    }

    if (existingOvNodes.has(sid)) {
      if (verbose) console.log(`[SKIP] Already synced: ${sid.slice(0,8)}...`);
      skipped++;
      continue;
    }

    try {
      const messages = await fetchSessionMessages(sid);
      const { nodes: newNodes, edges: newEdges } = sessionToGraph(sess, messages);

      // Add nodes
      for (const node of newNodes) {
        graph.nodes[node.id] = node;
      }
      // Add edges
      graph.edges.push(...newEdges);

      // Record sync metadata
      graph._meta.syncedFrom = graph._meta.syncedFrom || [];
      graph._meta.syncedFrom.push({
        source: 'openviking',
        session_id: sid,
        syncedAt: new Date().toISOString(),
        messages: messages.length,
        keywords: newNodes.filter(n => n.type === 'keyword').map(n => n.label)
      });

      newSessions++;
      log(`SYNC session ${sid.slice(0,8)}...  +${newNodes.length} nodes  +${newEdges.length} edges`);

    } catch (e) {
      console.error(`[ERROR] Session ${sid?.slice(0,8)}: ${e.message}`);
      log(`ERROR ${sid}: ${e.message}`);
      skipped++;
    }
  }

  // Save
  if (!dryRun) {
    saveGraph(graph);
    console.log(`Saved: ${GRAPH_PATH}`);
  }

  // Summary
  console.log('');
  console.log('Sync complete:');
  console.log(`  New sessions:  ${newSessions}`);
  console.log(`  Skipped:       ${skipped}`);
  console.log(`  Total nodes:   ${Object.keys(graph.nodes).length}`);
  console.log(`  Total edges:   ${graph.edges.length}`);
  console.log(`  Log:           ${SYNC_LOG_PATH}`);

  if (dryRun) console.log('  [DRY-RUN] No file written');
}

main().catch(e => {
  console.error('Fatal error:', e);
  process.exit(1);
});
