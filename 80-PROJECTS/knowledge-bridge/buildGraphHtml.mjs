/**
 * buildGraphHtml.mjs — Export knowledge graph as interactive D3 HTML
 *
 * Usage:
 *   node buildGraphHtml.mjs [graph.json] [--output <path>]
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const args = process.argv.slice(2);
const jsonPath = args[0] || join(__dirname, 'data', 'pla-knowledge-graph.json');
const outputIdx = args.indexOf('--output');
const outputPath = outputIdx >= 0 ? args[outputIdx + 1] : jsonPath.replace(/\.json$/, '.html');

let graphData;
try {
  const raw = JSON.parse(readFileSync(jsonPath, 'utf8'));
  graphData = raw;
} catch (e) {
  console.error('Failed to load graph:', e.message);
  console.error('Usage: node buildGraphHtml.mjs [graph.json] [--output <path>]');
  process.exit(1);
}

const graphNodes = graphData.nodes ? Object.values(graphData.nodes) : [];
const graphLinks = graphData.edges || [];
const analogies = graphData.analogyBank || [];

const nodesJson = JSON.stringify(graphNodes.map(n => ({
  id: n.id || n.label,
  label: n.label,
  domain: n.domain,
  description: (n.description || '').substring(0, 120)
})));

const linksJson = JSON.stringify(graphLinks.map(e => ({
  source: e.source,
  target: e.target,
  label: e.relation || e.label || ''
})));

const analogiesJson = JSON.stringify(analogies.map(a => {
  const src = graphNodes.find(n => n.id === a.source || n.label === a.source);
  const tgt = graphNodes.find(n => n.id === a.target || n.label === a.target);
  return {
    source: src?.label || String(a.source),
    target: tgt?.label || String(a.target),
    text: a.text || a.description || ''
  };
}));

const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>Knowledge Graph — ${graphData.name || 'Visualization'}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: ui-monospace, monospace; background: #0d1117; color: #e6edf3; overflow: hidden; }
  #graph { width: 100vw; height: 100vh; }
  .node circle { stroke: #30363d; stroke-width: 1.5px; cursor: pointer; }
  .node text { fill: #e6edf3; font-size: 11px; pointer-events: none; }
  .link { stroke: #30363d; stroke-opacity: 0.6; }
  #sidebar { position: fixed; top: 0; right: -360px; width: 360px; height: 100vh; background: #161b22; border-left: 1px solid #30363d; padding: 16px; overflow-y: auto; transition: right 0.25s; z-index: 10; display: flex; flex-direction: column; }
  #sidebar.open { right: 0; }
  #sidebar h3 { color: #22d3ee; font-size: 13px; margin-bottom: 8px; }
  #sidebar p { font-size: 12px; color: #8b949e; line-height: 1.5; margin-bottom: 12px; }
  #sidebar .close { float: right; cursor: pointer; color: #8b949e; font-size: 16px; }
  #chat-btn { margin-top: 8px; background: #238636; color: #fff; border: none; border-radius: 6px; padding: 8px 14px; font-size: 12px; cursor: pointer; width: 100%; }
  #chat-btn:hover { background: #2ea043; }
  #legend { position: fixed; bottom: 16px; left: 16px; background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 10px 14px; font-size: 11px; }
  .legend-item { display: flex; align-items: center; gap: 8px; margin-top: 4px; }
  .legend-dot { width: 10px; height: 10px; border-radius: 50%; }
  #stats { position: fixed; top: 16px; left: 16px; font-size: 12px; color: #8b949e; background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 8px 14px; }
  #analogy-panel { position: fixed; bottom: 16px; right: 16px; max-width: 400px; background: #161b22; border: 1px solid #a78bfa; border-radius: 8px; padding: 12px; font-size: 11px; display: none; }
  #analogy-panel.visible { display: block; }
  .analogy-source { color: #a78bfa; font-weight: 600; }
  .analogy-target { color: #22d3ee; font-weight: 600; }
  /* Chat panel */
  #chat-panel { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 680px; max-width: 95vw; background: #161b22; border: 1px solid #30363d; border-radius: 12px 12px 0 0; display: none; flex-direction: column; max-height: 60vh; z-index: 20; }
  #chat-panel.open { display: flex; }
  #chat-header { padding: 12px 16px; border-bottom: 1px solid #30363d; display: flex; align-items: center; justify-content: space-between; }
  #chat-header-title { font-size: 13px; color: #22d3ee; font-weight: 600; }
  #chat-close { background: none; border: none; color: #8b949e; cursor: pointer; font-size: 18px; }
  #chat-messages { flex: 1; overflow-y: auto; padding: 12px 16px; min-height: 200px; max-height: 40vh; }
  .chat-msg { margin-bottom: 10px; font-size: 12px; line-height: 1.5; }
  .chat-msg.user { color: #e6edf3; }
  .chat-msg.assistant { color: #7ee787; }
  .chat-msg.system { color: #f0883e; font-size: 11px; }
  .chat-msg pre { background: #0d1117; border-radius: 6px; padding: 8px; overflow-x: auto; margin-top: 4px; white-space: pre-wrap; }
  #chat-input-row { padding: 12px 16px; border-top: 1px solid #30363d; display: flex; gap: 8px; }
  #chat-input { flex: 1; background: #0d1117; border: 1px solid #30363d; border-radius: 6px; color: #e6edf3; font-size: 12px; font-family: inherit; padding: 8px 12px; resize: none; min-height: 38px; max-height: 120px; }
  #chat-input:focus { outline: none; border-color: #22d3ee; }
  #chat-send { background: #238636; color: #fff; border: none; border-radius: 6px; padding: 8px 16px; font-size: 12px; cursor: pointer; font-family: inherit; }
  #chat-send:hover { background: #2ea043; }
  #chat-send:disabled { background: #30363d; color: #6e7681; cursor: not-allowed; }
</style>
</head>
<body>
<div id="graph"></div>
<div id="stats">Loading...</div>
<div id="legend">
  <div style="color:#8b949e;margin-bottom:4px;">Domains</div>
  <div class="legend-item"><div class="legend-dot" style="background:#3fb950"></div>chemistry</div>
  <div class="legend-item"><div class="legend-dot" style="background:#58a6ff"></div>programming</div>
  <div class="legend-item"><div class="legend-dot" style="background:#f97316"></div>cooking</div>
  <div class="legend-item"><div class="legend-dot" style="background:#f85149"></div>medicine</div>
  <div class="legend-item"><div class="legend-dot" style="background:#e3b341"></div>engineering</div>
</div>
<div id="analogy-panel"></div>
<div id="sidebar">
  <span class="close" onclick="closeSidebar()">&#x2715;</span>
  <h3 id="sidebar-title">Node</h3>
  <p id="sidebar-desc"></p>
  <h3>Connections</h3>
  <div id="sidebar-edges"></div>
  <button id="chat-btn" onclick="openChat()">&#x2709; Chat about this node</button>
</div>
<div id="chat-panel">
  <div id="chat-header">
    <span id="chat-header-title">Chat</span>
    <button id="chat-close" onclick="closeChat()">&#x2715;</button>
  </div>
  <div id="chat-messages"></div>
  <div id="chat-input-row">
    <textarea id="chat-input" placeholder="Ask about this node... (Shift+Enter for newline, Enter to send)" rows="1"></textarea>
    <button id="chat-send" onclick="sendChat()">Send</button>
  </div>
</div>
<script>
const nodes = ${nodesJson};
const links = ${linksJson};
const analogies = ${analogiesJson};

const domainColors = {
  chemistry: '#3fb950',
  programming: '#58a6ff',
  cooking: '#f97316',
  medicine: '#f85149',
  engineering: '#e3b341'
};

document.getElementById('stats').textContent =
  nodes.length + ' nodes \xb7 ' + links.length + ' edges \xb7 ' + analogies.length + ' analogies';

const width = window.innerWidth;
const height = window.innerHeight;

const svg = d3.select('#graph').append('svg').attr('width', width).attr('height', height);
const g = svg.append('g');

svg.call(d3.zoom().scaleExtent([0.1, 4]).on('zoom', e => g.attr('transform', e.transform)));

const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).distance(100))
  .force('charge', d3.forceManyBody().strength(-300))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collision', d3.forceCollide(30));

const link = g.append('g').selectAll('line').data(links).join('line')
  .attr('class', 'link').attr('stroke-width', 1);

const node = g.append('g').selectAll('g').data(nodes).join('g')
  .attr('class', 'node')
  .call(d3.drag().on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
    .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
    .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }))
  .on('click', (e, d) => showSidebar(d));

node.append('circle').attr('r', 14).attr('fill', d => domainColors[d.domain] || '#8b949e');
node.append('text').attr('dy', 24).attr('text-anchor', 'middle').text(d => d.label.substring(0, 16));

simulation.on('tick', () => {
  link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
  node.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
});

function showSidebar(d) {
  const panel = document.getElementById('sidebar');
  document.getElementById('sidebar-title').textContent = d.label + ' (' + d.domain + ')';
  document.getElementById('sidebar-desc').textContent = d.description || '(no description)';
  const related = links.filter(l => l.source.id === d.id || l.target.id === d.id);
  document.getElementById('sidebar-edges').innerHTML = related.map(l => {
    const other = l.source.id === d.id ? l.target : l.source;
    return '<div style="margin-top:6px;font-size:11px;"><span style="color:#58a6ff">' + (l.label||'related') + '</span>: ' + other.label + '</div>';
  }).join('') || '<div style="color:#6e7681;font-size:11px;">No connections</div>';
  panel.classList.add('open');
  const analogy = analogies.find(a => a.source === d.label || a.target === d.label);
  const ap = document.getElementById('analogy-panel');
  if (analogy) {
    ap.innerHTML = '<span class="analogy-source">' + analogy.source + '</span> \u2248 <span class="analogy-target">' + analogy.target + '</span><br><br>' + analogy.text.substring(0,200);
    ap.classList.add('visible');
  } else { ap.classList.remove('visible'); }
}
function closeSidebar() { document.getElementById('sidebar').classList.remove('open'); }

// Chat
let chatNode = null;
let chatHistory = [];

function openChat() {
  const title = document.getElementById('sidebar-title').textContent;
  chatNode = nodes.find(n => title.startsWith(n.label)) || null;
  chatHistory = [];
  document.getElementById('chat-messages').innerHTML = '';
  if (!chatNode) {
    addMsg('system', 'Select a node first by clicking on it in the graph.');
    return;
  }
  addMsg('system', 'Context loaded for: ' + chatNode.label + '. Ask anything about this node!');
  document.getElementById('chat-panel').classList.add('open');
  document.getElementById('chat-input').focus();
}

function closeChat() { document.getElementById('chat-panel').classList.remove('open'); }

function buildNodeContext(n) {
  const related = links.filter(l => l.source.id === n.id || l.target.id === n.id);
  const connNodes = related.map(l => l.source.id === n.id ? l.target.label : l.source.label);
  const analogy = analogies.find(a => a.source === n.label || a.target === n.label);
  let ctx = 'Node: ' + n.label + ' (domain: ' + (n.domain||'unknown') + ')\n';
  if (n.description) ctx += 'Description: ' + n.description + '\n';
  if (connNodes.length) ctx += 'Connected to: ' + connNodes.join(', ') + '\n';
  if (analogy) ctx += 'Analogy: ' + analogy.source + ' \u2248 ' + analogy.target + ' \u2014 ' + analogy.text.substring(0,200) + '\n';
  return ctx;
}

function addMsg(role, text) {
  const div = document.createElement('div');
  div.className = 'chat-msg ' + role;
  if (role === 'user') div.textContent = 'You: ' + text;
  else if (role === 'assistant') div.innerHTML = 'Assistant: ' + text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
  else div.textContent = text;
  document.getElementById('chat-messages').appendChild(div);
  document.getElementById('chat-messages').scrollTop = 1e9;
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg || !chatNode) return;
  input.value = '';
  addMsg('user', msg);
  chatHistory.push({ role: 'user', content: msg });
  const sendBtn = document.getElementById('chat-send');
  sendBtn.disabled = true;
  try {
    const context = buildNodeContext(chatNode);
    const systemMsg = 'You are a helpful assistant discussing a knowledge graph node. Answer based ONLY on the provided context.\n\nContext:\n' + context;
    const conversation = systemMsg + '\n\n' + chatHistory.map(m => m.role + ': ' + m.content).join('\n');
    const body = JSON.stringify({ model: 'gemma4:e2b', prompt: conversation, stream: false });
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 60000);
    const resp = await fetch('http://localhost:11434/api/generate', { method: 'POST', headers: {'Content-Type':'application/json'}, body, signal: controller.signal });
    clearTimeout(timer);
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = JSON.parse(await resp.text());
    const reply = (data.response || '').trim() || '(no response)';
    chatHistory.push({ role: 'assistant', content: reply });
    addMsg('assistant', reply);
  } catch (e) {
    addMsg('system', 'Ollama error: ' + e.message + ' \u2014 Is Ollama running at localhost:11434?');
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
}

document.getElementById('chat-input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
});
</script>
</body>
</html>`;

writeFileSync(outputPath, html, 'utf8');
console.log('Saved: ' + outputPath);
console.log('Nodes: ' + graphNodes.length + ', Edges: ' + graphLinks.length + ', Analogies: ' + analogies.length);
