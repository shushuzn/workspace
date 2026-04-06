/**
 * openclaw-mcp-registry — HTTP API + Web UI for MCP server registry
 *
 * Port 3847: registry API
 * Port 3848: web UI
 */

import http from 'http';
import { RegistryStore, type MCPServer } from './registry-store.js';
import { BillingStore, PRICING_PLANS, type PricingTier } from './billing-store.js';

const STORE = new RegistryStore();
const BILLING = new BillingStore();
const PORT = 3847;
const UI_PORT = 3848;
const HEARTBEAT_TTL = 300_000;

// ─── JSON helper ─────────────────────────────────────────────────────────────

function json(res: http.ServerResponse, data: unknown, status = 200): void {
  res.writeHead(status, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
  res.end(JSON.stringify(data));
}

function readBody<T>(req: http.IncomingMessage): Promise<T> {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => { try { resolve(JSON.parse(body)); } catch { reject(new Error('Invalid JSON')); } });
    req.on('error', reject);
  });
}

// ─── Prune stale agents ─────────────────────────────────────────────────────

setInterval(() => {
  const removed = STORE.pruneStale(HEARTBEAT_TTL);
  if (removed.length) console.log(`[registry] pruned stale: ${removed.join(', ')}`);
}, HEARTBEAT_TTL);

// ─── API Server ─────────────────────────────────────────────────────────────

const server = http.createServer(async (req: http.IncomingMessage, res: http.ServerResponse) => {
  const url = new URL(req.url ?? '/', `http://localhost:${PORT}`);
  const path = url.pathname;

  try {
    // GET /servers — list all servers
    if (path === '/servers' && req.method === 'GET') {
      const tag = url.searchParams.get('tag') ?? undefined;
      const toolName = url.searchParams.get('tool') ?? undefined;
      const servers = STORE.list({ tag, toolName });
      json(res, { count: servers.length, servers });
      return;
    }

    // GET /servers/:id — get server details
    const serverMatch = path.match(/^\/servers\/([^/]+)$/);
    if (serverMatch && req.method === 'GET') {
      const s = STORE.get(serverMatch[1]);
      if (!s) { json(res, { error: 'Not found' }, 404); return; }
      json(res, s);
      return;
    }

    // POST /servers — register a new MCP server
    if (path === '/servers' && req.method === 'POST') {
      const body = await readBody<Partial<MCPServer>>(req);
      if (!body.id || !body.name) { json(res, { error: 'id and name required' }, 400); return; }
      STORE.register(body as Omit<MCPServer, 'lastHeartbeat' | 'healthy'>);
      console.log(`[registry] registered: ${body.name} (${body.id})`);
      json(res, { ok: true, id: body.id });
      return;
    }

    // DELETE /servers/:id — unregister
    if (serverMatch && req.method === 'DELETE') {
      const ok = STORE.unregister(serverMatch[1]);
      json(res, { ok });
      return;
    }

    // POST /servers/:id/heartbeat — keep alive
    if (path.match(/^\/servers\/([^/]+)\/heartbeat$/) && req.method === 'POST') {
      const id = path.split('/')[2];
      const ok = STORE.heartbeat(id);
      json(res, { ok });
      return;
    }

    // GET /discover?capability=X — find servers by capability
    if (path === '/discover' && req.method === 'GET') {
      const cap = url.searchParams.get('capability');
      if (!cap) { json(res, { error: 'capability required' }, 400); return; }
      const servers = STORE.discover(cap);
      json(res, { count: servers.length, servers });
      return;
    }

    // GET /health
    if (path === '/health' && req.method === 'GET') {
      const all = STORE.list();
      json(res, {
        status: 'ok',
        total: all.length,
        healthy: all.filter(s => s.healthy).length,
      });
      return;
    }

    // POST /api/v1/call — forward an MCP tool call to a registered server
    if (path === '/api/v1/call' && req.method === 'POST') {
      const body = await readBody<{ serverId: string; tool: string; arguments?: Record<string, unknown> }>(req);
      if (!body.serverId || !body.tool) { json(res, { error: 'serverId and tool required' }, 400); return; }
      const srv = STORE.get(body.serverId);
      if (!srv) { json(res, { error: 'Server not found' }, 404); return; }
      // Forward JSON-RPC 2.0 request to the MCP server
      const rpcReq = {
        jsonrpc: '2.0',
        id: Date.now(),
        method: `tools/${body.tool}`,
        params: { arguments: body.arguments ?? {} },
      };
      let rpcResp: unknown;
      try {
        const forwardRes = await fetch(srv.endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(rpcReq),
        });
        rpcResp = await forwardRes.json();
      } catch (e: any) {
        json(res, { error: `Forward failed: ${e.message}` }, 502); return;
      }
      json(res, rpcResp);
      return;
    }

    // GET /plans — list all pricing plans
    if (path === '/plans' && req.method === 'GET') {
      json(res, { plans: PRICING_PLANS });
      return;
    }

    // GET /servers/:id/plan — get server's current plan
    const planMatch = path.match(/^\/servers\/([^/]+)\/plan$/);
    if (planMatch && req.method === 'GET') {
      const serverId = planMatch[1];
      const tier = BILLING.getTier(serverId);
      const plan = BILLING.getPlan(serverId);
      const usage = BILLING.getUsage(serverId);
      json(res, { serverId, tier, plan, usage });
      return;
    }

    // PUT /servers/:id/plan — update server's plan tier
    if (planMatch && req.method === 'PUT') {
      const serverId = planMatch[1];
      const body = await readBody<{ tier: PricingTier }>(req);
      if (!body.tier) { json(res, { error: 'tier required' }, 400); return; }
      BILLING.setTier(serverId, body.tier);
      json(res, { ok: true, tier: body.tier });
      return;
    }

    // GET /servers/:id/usage — get usage stats for server
    if (path.match(/^\/servers\/([^/]+)\/usage$/) && req.method === 'GET') {
      const serverId = path.split('/')[2];
      const usage = BILLING.getUsage(serverId);
      const canUse = BILLING.canUse(serverId);
      json(res, { serverId, ...usage, canUse });
      return;
    }

    // POST /servers/:id/usage/record — record an API call (for metering)
    if (path.match(/^\/servers\/([^/]+)\/usage\/record$/) && req.method === 'POST') {
      const serverId = path.split('/')[2];
      const body = await readBody<{ endpoint: string; method: string; statusCode: number; callerIp?: string }>(req);
      BILLING.recordCall(serverId, body.endpoint || '/', body.method || 'GET', body.statusCode || 200, body.callerIp || '0.0.0.0');
      json(res, { ok: true });
      return;
    }

    // GET /billing/usage — top usage stats (admin)
    if (path === '/billing/usage' && req.method === 'GET') {
      const top = BILLING.getTopUsage(20);
      json(res, { top });
      return;
    }

    // POST /billing/stripe-webhook — Stripe webhook receiver
    if (path === '/billing/stripe-webhook' && req.method === 'POST') {
      const sig = req.headers['stripe-signature'];
      const rawBody = await readBody<{ type: string; data: { object: { customer?: string; subscription?: string; status?: string; metadata?: { serverId?: string } } } }>(req);
      // Basic event routing — in production verify webhook signature
      if (rawBody.type === 'customer.subscription.created' || rawBody.type === 'customer.subscription.updated') {
        const { customer, subscription, metadata } = rawBody.data.object;
        const serverId = metadata?.serverId;
        if (serverId && customer) {
          const tier = rawBody.type === 'customer.subscription.created' ? 'starter' : BILLING.getTier(serverId);
          BILLING.setStripeIds(serverId, customer, subscription ?? '');
          BILLING.setTier(serverId, tier);
          console.log(`[billing] Stripe webhook: server=${serverId} customer=${customer} sub=${subscription}`);
        }
      }
      if (rawBody.type === 'customer.subscription.deleted') {
        const { metadata } = rawBody.data.object;
        const serverId = metadata?.serverId;
        if (serverId) {
          BILLING.setTier(serverId, 'free');
          console.log(`[billing] Subscription cancelled for server=${serverId}, reverted to free`);
        }
      }
      json(res, { received: true });
      return;
    }

    json(res, { error: 'Not found' }, 404);
  } catch (err: any) {
    json(res, { error: err.message }, 500);
  }
});

server.listen(PORT, () => {
  console.log(`🔌 MCP Registry API: http://localhost:${PORT}`);
  console.log(`   GET  /servers              — list all servers`);
  console.log(`   GET  /servers/:id        — server details`);
  console.log(`   POST /servers             — register server`);
  console.log(`   DELETE /servers/:id       — unregister`);
  console.log(`   POST /servers/:id/heartbeat — keep alive`);
  console.log(`   GET  /discover?capability=X — discover`);
  console.log(`   GET  /health              — health check`);
});

// ─── Web UI Server (port 3848) ─────────────────────────────────────────────

const uiServer = http.createServer((req: http.IncomingMessage, res: http.ServerResponse) => {
  const url = new URL(req.url ?? '/', `http://localhost:${UI_PORT}`);
  const path = url.pathname;

  if (path === '/' && req.method === 'GET') {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>MCP Registry</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: ui-monospace, monospace; background: #0d1117; color: #e6edf3; min-height: 100vh; }
  header { background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 24px; display: flex; align-items: center; gap: 16px; }
  h1 { font-size: 18px; font-weight: 600; color: #22d3ee; }
  .badge { background: #21262d; color: #8b949e; font-size: 12px; padding: 2px 8px; border-radius: 12px; }
  #stats { padding: 16px 24px; font-size: 13px; color: #8b949e; border-bottom: 1px solid #21262d; }
  #grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; padding: 16px 24px; }
  .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; transition: border-color 0.2s; }
  .card:hover { border-color: #22d3ee; }
  .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
  .card-name { font-size: 15px; font-weight: 600; color: #e6edf3; }
  .card-version { font-size: 11px; color: #8b949e; background: #21262d; padding: 1px 6px; border-radius: 4px; margin-left: 8px; }
  .card-desc { font-size: 12px; color: #8b949e; margin-bottom: 12px; line-height: 1.5; }
  .card-meta { font-size: 11px; color: #6e7681; margin-bottom: 10px; }
  .card-endpoint { font-size: 11px; color: #22d3ee; word-break: break-all; margin-bottom: 10px; }
  .tags { display: flex; flex-wrap: wrap; gap: 4px; }
  .tag { background: #1f3a5f; color: #58a6ff; font-size: 10px; padding: 2px 6px; border-radius: 4px; }
  .tools { margin-top: 10px; }
  .tool { background: #21262d; border: 1px solid #30363d; border-radius: 4px; padding: 6px 8px; margin-top: 6px; font-size: 11px; }
  .tool-name { color: #7ee787; font-weight: 600; }
  .tool-desc { color: #8b949e; margin-top: 2px; }
  .status-dot { width: 8px; height: 8px; border-radius: 50%; background: #6e7681; display: inline-block; margin-right: 6px; }
  .status-dot.healthy { background: #3fb950; box-shadow: 0 0 6px #3fb950; }
  .status-dot.stale { background: #f85149; }
  .empty { text-align: center; padding: 64px; color: #6e7681; font-size: 14px; }
  #refresh { background: #21262d; border: 1px solid #30363d; color: #e6edf3; font-size: 12px; padding: 6px 14px; border-radius: 6px; cursor: pointer; }
  #refresh:hover { border-color: #22d3ee; }
</style>
</head>
<body>
<header>
  <h1>🔌 MCP Registry</h1>
  <span class="badge" id="version">v0.1.0</span>
  <button id="refresh">↻ Refresh</button>
</header>
<div id="stats">Loading...</div>
<div id="grid"><div class="empty">No servers registered yet</div></div>
<script>
async function load() {
  const res = await fetch('/servers');
  const data = await res.json();
  document.getElementById('stats').textContent =
    data.count + ' server(s) registered · ' + data.servers.filter(s => s.healthy).length + ' healthy';
  const grid = document.getElementById('grid');
  if (!data.servers.length) {
    grid.innerHTML = '<div class="empty">No servers registered yet.<br><br>POST to /servers to register.</div>';
    return;
  }
  grid.innerHTML = data.servers.map(s => \`
    <div class="card">
      <div class="card-header">
        <span class="card-name">\${s.name} <span class="card-version">\${s.version}</span></span>
        <span><span class="status-dot \${s.healthy ? 'healthy' : 'stale'}"></span></span>
      </div>
      <div class="card-desc">\${s.description || '(no description)'}</div>
      <div class="card-meta">ID: \${s.id}</div>
      <div class="card-endpoint">\${s.endpoint}</div>
      \${s.tags.length ? '<div class="tags">' + s.tags.map(t => '<span class="tag">' + t + '</span>').join('') + '</div>' : ''}
      \${s.tools.length ? '<div class="tools">' + s.tools.map(t => \`
        <div class="tool">
          <div class="tool-name">\${t.name}</div>
          <div class="tool-desc">\${t.description}</div>
        </div>\`).join('') + '</div>' : ''}
    </div>\`).join('');
}
document.getElementById('refresh').onclick = load;
load();
setInterval(load, 15000);
</script>
</body>
</html>`);
  return;
}

if (path === '/inspector' && req.method === 'GET') {
  res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
  res.end(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>MCP Inspector</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: ui-monospace, monospace; background: #0d1117; color: #e6edf3; min-height: 100vh; display: flex; flex-direction: column; }
  header { background: #161b22; border-bottom: 1px solid #30363d; padding: 12px 20px; display: flex; align-items: center; gap: 16px; }
  h1 { font-size: 16px; font-weight: 600; color: #22d3ee; }
  .badge { background: #21262d; color: #8b949e; font-size: 11px; padding: 2px 8px; border-radius: 12px; }
  .back { background: #21262d; border: 1px solid #30363d; color: #e6edf3; font-size: 12px; padding: 4px 12px; border-radius: 6px; cursor: pointer; text-decoration: none; }
  .back:hover { border-color: #22d3ee; }
  .layout { display: flex; flex: 1; overflow: hidden; }
  .sidebar { width: 280px; border-right: 1px solid #21262d; overflow-y: auto; padding: 12px; }
  .sidebar h3 { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
  .server-item { background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 10px; margin-bottom: 6px; cursor: pointer; transition: border-color 0.2s; }
  .server-item:hover { border-color: #22d3ee; }
  .server-item.active { border-color: #22d3ee; background: #1c2a3a; }
  .server-name { font-size: 13px; font-weight: 600; }
  .server-endpoint { font-size: 10px; color: #6e7681; margin-top: 2px; word-break: break-all; }
  .tool-item { background: #21262d; border-radius: 4px; padding: 6px 8px; margin-bottom: 4px; cursor: pointer; font-size: 12px; color: #7ee787; }
  .tool-item:hover { background: #2d333b; }
  .tool-item.selected { background: #1f3a5f; }
  .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
  .tool-header { padding: 12px 16px; border-bottom: 1px solid #21262d; }
  .tool-title { font-size: 15px; font-weight: 600; color: #7ee787; }
  .tool-desc { font-size: 11px; color: #8b949e; margin-top: 2px; }
  .schema-box { background: #0d1117; border: 1px solid #21262d; border-radius: 4px; padding: 8px; margin: 8px 16px; font-size: 11px; color: #8b949e; overflow-x: auto; }
  .schema-box pre { margin: 0; white-space: pre-wrap; }
  .req-res { flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 12px 16px; gap: 8px; }
  .section-label { font-size: 11px; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; }
  textarea { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #e6edf3; font-family: ui-monospace, monospace; font-size: 12px; padding: 10px; resize: none; }
  textarea:focus { outline: none; border-color: #22d3ee; }
  textarea.args { height: 120px; }
  textarea.response { flex: 1; background: #0d1117; color: #8b949e; min-height: 100px; }
  .btn-row { display: flex; gap: 8px; align-items: center; }
  button { background: #238636; border: none; color: #fff; font-size: 12px; padding: 7px 16px; border-radius: 6px; cursor: pointer; }
  button:hover { background: #2ea043; }
  button:disabled { background: #21262d; color: #6e7681; cursor: not-allowed; }
  .response-area { flex: 1; display: flex; flex-direction: column; }
  .response-meta { font-size: 11px; color: #8b949e; padding: 4px 0; }
  .empty-state { flex: 1; display: flex; align-items: center; justify-content: center; color: #6e7681; font-size: 13px; }
  .status-ok { color: #3fb950; }
  .status-err { color: #f85149; }
</style>
</head>
<body>
<header>
  <h1>🔍 MCP Inspector</h1>
  <span class="badge">Postman for MCP</span>
  <a href="/" class="back">← Registry</a>
</header>
<div class="layout">
  <div class="sidebar">
    <h3>Servers</h3>
    <div id="servers">Loading...</div>
  </div>
  <div class="main">
    <div class="empty-state" id="empty">Select a server and tool to start</div>
    <div id="panel" style="display:none; flex-direction:column; flex:1; overflow:hidden;">
      <div class="tool-header">
        <div class="tool-title" id="toolName">—</div>
        <div class="tool-desc" id="toolDesc">—</div>
      </div>
      <div class="schema-box"><pre id="inputSchema"></pre></div>
      <div class="req-res">
        <div class="section-label">Arguments (JSON)</div>
        <textarea class="args" id="args" placeholder="{}">{}</textarea>
        <div class="btn-row">
          <button id="sendBtn" disabled>Send Request</button>
          <span class="response-meta" id="statusMeta"></span>
        </div>
        <div class="response-area">
          <div class="section-label">Response</div>
          <textarea class="response" id="response" readonly placeholder="Response will appear here..."></textarea>
        </div>
      </div>
    </div>
  </div>
</div>
<script>
let servers = [];
let selectedServer = null;
let selectedTool = null;

async function loadServers() {
  const res = await fetch('/servers');
  const data = await res.json();
  servers = data.servers;
  const el = document.getElementById('servers');
  if (!servers.length) { el.innerHTML = '<div style="font-size:12px;color:#6e7681">No servers</div>'; return; }
  el.innerHTML = servers.map(s => \`
    <div class="server-item" data-id="\${s.id}">
      <div class="server-name">\${s.name}</div>
      <div class="server-endpoint">\${s.endpoint}</div>
    </div>\`).join('');
  el.querySelectorAll('.server-item').forEach(item => {
    item.onclick = () => selectServer(item.dataset.id);
  });
}

function selectServer(id) {
  selectedServer = servers.find(s => s.id === id);
  selectedTool = null;
  document.querySelectorAll('.server-item').forEach(el => el.classList.remove('active'));
  document.querySelector('.server-item[data-id="'+id+'"]').classList.add('active');
  // Rebuild tools list
  const parent = document.getElementById('servers');
  const existing = parent.querySelectorAll('h3');
  existing.forEach(el => { if (el.textContent !== 'Servers') el.remove(); });
  if (selectedServer && selectedServer.tools.length) {
    const toolsHtml = '<h3 style="margin-top:12px">Tools</h3>' + selectedServer.tools.map(t =>
      '<div class="tool-item" data-name="'+t.name+'">'+t.name+'</div>'
    ).join('');
    parent.insertAdjacentHTML('beforeend', toolsHtml);
    parent.querySelectorAll('.tool-item').forEach(item => {
      item.onclick = (e) => { e.stopPropagation(); selectTool(item.dataset.name); };
    });
  }
  showEmpty();
}

function selectTool(name) {
  if (!selectedServer) return;
  selectedTool = selectedServer.tools.find(t => t.name === name);
  document.querySelectorAll('.tool-item').forEach(el => el.classList.remove('selected'));
  document.querySelector('.tool-item[data-name="'+name+'"]').classList.add('selected');
  document.getElementById('toolName').textContent = selectedTool.name;
  document.getElementById('toolDesc').textContent = selectedTool.description || '';
  document.getElementById('inputSchema').textContent = JSON.stringify(selectedTool.inputSchema || {}, null, 2);
  document.getElementById('args').value = '{}';
  document.getElementById('sendBtn').disabled = false;
  document.getElementById('empty').style.display = 'none';
  document.getElementById('panel').style.display = 'flex';
  document.getElementById('response').value = '';
  document.getElementById('statusMeta').textContent = '';
}

function showEmpty() {
  document.getElementById('empty').style.display = 'flex';
  document.getElementById('panel').style.display = 'none';
}

document.getElementById('sendBtn').onclick = async () => {
  if (!selectedServer || !selectedTool) return;
  const btn = document.getElementById('sendBtn');
  btn.disabled = true;
  btn.textContent = 'Sending...';
  let args = {};
  try { args = JSON.parse(document.getElementById('args').value); } catch { args = {}; }
  const start = Date.now();
  try {
    const res = await fetch('/api/v1/call', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ serverId: selectedServer.id, tool: selectedTool.name, arguments: args }),
    });
    const elapsed = Date.now() - start;
    const data = await res.json();
    document.getElementById('response').value = JSON.stringify(data, null, 2);
    document.getElementById('statusMeta').innerHTML = res.ok
      ? '<span class="status-ok">✓ ' + res.status + ' in ' + elapsed + 'ms</span>'
      : '<span class="status-err">✗ ' + res.status + ' in ' + elapsed + 'ms</span>';
  } catch (e) {
    document.getElementById('response').value = 'Error: ' + e.message;
    document.getElementById('statusMeta').innerHTML = '<span class="status-err">✗ Network error</span>';
  }
  btn.disabled = false;
  btn.textContent = 'Send Request';
};

loadServers();
</script>
</body>
</html>`);
  return;
}

res.writeHead(404); res.end();
});

uiServer.listen(UI_PORT, () => {
  console.log(`🌐 MCP Registry UI: http://localhost:${UI_PORT}`);
});

// ─── Auto-register task-orchestrator if its OAP dispatcher is running ───────

setTimeout(async () => {
  try {
    const res = await fetch('http://localhost:3848/agents', { method: 'GET' });
    if (res.ok) {
      const agents = await res.json();
      for (const a of agents) {
        STORE.register({
          id: a.agentId,
          name: a.name || a.agentId,
          version: a.version || '0.1.0',
          description: `OAP agent: ${a.intent}`,
          endpoint: a.endpoint || `http://localhost:3848/agent/${a.agentId}`,
          tools: [],
          tags: [a.intent, 'oap', 'task-orchestrator'],
        });
      }
      console.log(`[registry] auto-registered ${agents.length} task-orchestrator agents`);
    }
  } catch { /* task-orchestrator not running */ }
}, 5000);
