#!/usr/bin/env node
/**
 * Dashboard HTTP Server
 * Serves dashboard.html with dashboard-data.json
 * Supports SSE real-time updates
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3847;
const PROJECT_DIR = __dirname;
const WORKSPACE = path.join(__dirname, '..', '..');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.json': 'application/json',
  '.js': 'application/javascript',
  '.css': 'text/css',
};

// SSE clients for real-time updates
const sseClients = new Set();

function serveFile(res, filePath, mimeType) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not Found: ' + filePath);
      return;
    }
    res.writeHead(200, { 'Content-Type': mimeType });
    res.end(data);
  });
}

// Broadcast to all SSE clients
function broadcast(data) {
  const message = `data: ${JSON.stringify(data)}\n\n`;
  for (const client of sseClients) {
    try {
      client.write(message);
    } catch (e) {
      sseClients.delete(client);
    }
  }
}

// SSE heartbeat to keep connections alive
setInterval(() => {
  for (const client of sseClients) {
    try {
      client.write(': heartbeat\n\n');
    } catch (e) {
      sseClients.delete(client);
    }
  }
}, 30000);

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  console.log('Request:', req.url);

  let filePath;
  const url = req.url.split('?')[0];

  if (url === '/' || url === '/dashboard') {
    filePath = path.join(PROJECT_DIR, 'dashboard.html');
  } else if (url === '/data') {
    require('./generate-dashboard-data.js');
    filePath = path.join(PROJECT_DIR, 'dashboard-data.json');
  } else if (url === '/api/refresh') {
    require('./generate-dashboard-data.js');
    filePath = path.join(PROJECT_DIR, 'dashboard-data.json');
  } else if (url.startsWith('/api/git-history') && req.method === 'GET') {
    const project = url.searchParams.get('project') || '';
    const safeProject = project.replace(/[^a-zA-Z0-9_-]/g, '');
    if (!safeProject) {
      res.writeHead(400);
      res.end(JSON.stringify({ error: 'project param required' }));
      return;
    }
    const projectPath = path.join(WORKSPACE, '80-PROJECTS', safeProject);
    try {
      const { execSync } = require('child_process');
      const log = execSync(`git log --oneline -30 --format="%H|%an|%ai|%s"`, { cwd: projectPath, encoding: 'utf8', timeout: 5000 });
      const branches = execSync(`git branch -a --format="%(refname:short)|%(objectname:short)" 2>nul`, { cwd: projectPath, encoding: 'utf8', timeout: 5000 });
      const commits = log.trim().split('\n').filter(Boolean).map(line => {
        const [hash, author, date, msg] = line.split('|');
        return { hash: hash.slice(0, 7), author, date, message: msg };
      });
      const branchList = branches.trim().split('\n').filter(Boolean).map(b => {
        const [name, sha] = b.split('|');
        return { name, sha };
      });
      res.end(JSON.stringify({ project: safeProject, commits, branches: branchList }));
    } catch (e) {
      res.writeHead(500);
      res.end(JSON.stringify({ error: e.message }));
    }
    return;
  } else if (url === '/api/events') {
    // SSE endpoint
    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*'
    });
    res.write('data: {"type":"connected"}\n\n');
    sseClients.add(res);
    req.on('close', () => {
      sseClients.delete(res);
    });
    return;
  } else {
    // Security: prevent path traversal
    const decodedUrl = decodeURIComponent(url);
    if (decodedUrl.includes('..') || decodedUrl.startsWith('/')) {
      res.writeHead(400);
      res.end('Bad Request');
      return;
    }
    filePath = path.join(PROJECT_DIR, decodedUrl);
  }

  const ext = path.extname(filePath).toLowerCase();
  const mimeType = MIME_TYPES[ext] || 'text/plain';

  serveFile(res, filePath, mimeType);
});

server.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════╗
║     OpenClaw Dashboard Server            ║
╠═══════════════════════════════════════════╣
║  Local:   http://localhost:${PORT}          ║
║  Full:    http://localhost:${PORT}/dashboard  ║
║  Data:    http://localhost:${PORT}/data      ║
║  Events:  http://localhost:${PORT}/api/events ║
╚═══════════════════════════════════════════╝
`);
});

// Auto-refresh data on startup
require('./generate-dashboard-data.js');

// Watch workspace for changes (auto-regenerate data and broadcast)
let watchTimeout = null;
const watcher = fs.watch(WORKSPACE, { recursive: true }, (eventType, filename) => {
  if (!filename) return;
  // Debounce: only regenerate after 2s of no changes
  if (watchTimeout) clearTimeout(watchTimeout);
  watchTimeout = setTimeout(() => {
    console.log('[watch] Change detected, regenerating data...');
    require('./generate-dashboard-data.js');
    // Broadcast update to all SSE clients
    try {
      const data = JSON.parse(fs.readFileSync(path.join(PROJECT_DIR, 'dashboard-data.json'), 'utf8'));
      broadcast({ type: 'update', data });
      console.log('[sse] Broadcasted update to', sseClients.size, 'clients');
    } catch (e) {
      console.error('[sse] Broadcast error:', e.message);
    }
  }, 2000);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('[shutdown] Closing watcher and server...');
  watcher.close();
  server.close();
  process.exit();
});

console.log('[watch] Monitoring workspace for changes...');
