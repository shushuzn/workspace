/**
 * task-orchestrator/src/ui/stream.ts
 * SSE streaming server + Execution Visualizer UI
 * Serves a minimal web UI that streams real-time task chain execution via SSE.
 *
 * Usage:
 *   node --import tsx src/ui/stream.ts [task.yaml]
 *   node --import tsx src/ui/stream.ts --watch src/index.ts
 */
import { createServer } from 'node:http';
import { dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Executor } from '../executor.mjs';
import { Registry } from '../registry.mjs';
const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = 3737;
const HTML = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>Task Orchestrator — Execution Visualizer</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: ui-monospace, monospace; background: #0d1117; color: #e6edf3; padding: 16px; }
  h1 { font-size: 14px; color: #22d3ee; margin-bottom: 12px; }
  #status { font-size: 11px; color: #8b949e; margin-bottom: 12px; }
  #log { display: flex; flex-direction: column; gap: 4px; }
  .step { display: flex; align-items: start; gap: 8px; font-size: 11px; padding: 4px 8px; border-radius: 4px; background: #161b22; }
  .step.running { border-left: 3px solid #f0883e; }
  .step.ok { border-left: 3px solid #3fb950; }
  .step.fail { border-left: 3px solid #f85149; }
  .step.pending { border-left: 3px solid #30363d; opacity: 0.5; }
  .adapter { color: #58a6ff; min-width: 120px; }
  .cmd { color: #e3b341; flex: 1; word-break: break-all; }
  .duration { color: #6e7681; min-width: 60px; text-align: right; }
  .seq { color: #30363d; min-width: 24px; }
</style>
</head>
<body>
<h1>Task Orchestrator — Execution Visualizer</h1>
<div id="status">Connecting...</div>
<div id="log"></div>
<script>
const log = document.getElementById('log');
const status = document.getElementById('status');
const ev = new EventSource('http://localhost:${PORT}/events');
ev.onopen = () => { status.textContent = 'Connected — streaming execution events'; };
ev.onerror = () => { status.textContent = 'Disconnected'; };
ev.onmessage = e => {
  const d = JSON.parse(e.data);
  if (d.type === 'start') {
    status.textContent = 'Run: ' + d.runId + ' | Steps: ' + d.stepCount;
    log.innerHTML = '';
  }
  if (d.type === 'step') {
    const s = d.step;
    const cls = d.success ? 'ok' : d.fatal ? 'fail' : 'running';
    const div = document.createElement('div');
    div.className = 'step ' + (d.done ? cls : 'running');
    div.innerHTML = '<span class="seq">' + String(d.seq).padStart(2,'0') + '</span>' +
      '<span class="adapter">' + (s.adapterType||'') + '</span>' +
      '<span class="cmd">' + (s.command||'') + '</span>' +
      '<span class="duration">' + (d.durationMs != null ? d.durationMs+'ms' : '...') + '</span>';
    log.appendChild(div);
    log.scrollTop = 1e9;
  }
  if (d.type === 'done') {
    status.textContent = 'Done — ' + d.totalSteps + ' steps | ' + d.successCount + ' ok | ' + d.failCount + ' fail';
  }
};
</script>
</body>
</html>`;
const clients = new Set();
function broadcast(event, data) {
    const msg = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
    for (const c of clients) {
        try {
            c.write(msg);
        }
        catch { }
    }
}
function startServer(port) {
    const server = createServer((req, res) => {
        const url = new URL(req.url || '', `http://localhost:${port}`);
        if (url.pathname === '/') {
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(HTML);
            return;
        }
        if (url.pathname === '/events') {
            res.writeHead(200, {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            });
            const client = {
                write: (data) => { try {
                    res.write(data);
                }
                catch { } },
                end: () => { try {
                    res.end();
                }
                catch { } },
            };
            clients.add(client);
            req.on('close', () => clients.delete(client));
            return;
        }
        res.writeHead(404);
        res.end();
    });
    server.listen(port, () => {
        console.log(`Execution Visualizer: http://localhost:${port}`);
    });
    return server;
}
export async function runWithStream(steps, opts = {}) {
    const port = opts.port ?? PORT;
    const registry = opts.registry ?? new Registry();
    startServer(port);
    const executor = new Executor(registry, {
        ...opts,
        onStepResult: (step, result, durationMs) => {
            const entry = {
                type: 'step',
                seq: result.seq,
                step: {
                    adapterType: step.adapterType,
                    command: step.command,
                },
                success: result.success,
                fatal: result.fatal,
                durationMs,
                done: true,
            };
            broadcast('step', entry);
        },
    });
    const seq0 = { seq: 0 };
    broadcast('start', { type: 'start', runId: '', stepCount: steps.length, ...seq0 });
    const results = await executor.execute(steps, opts);
    const okCount = results.filter(r => r.success).length;
    const failCount = results.length - okCount;
    broadcast('done', { type: 'done', totalSteps: results.length, successCount: okCount, failCount, ...seq0 });
    return results;
}
