/**
 * Shared metrics schema — Prometheus-compatible.
 * All 80-PROJECTS/* projects import from here for unified metrics collection.
 * @example
 * const { register, incr, gauge, prometheusFormat } = require('./metrics.js');
 * register('http_requests_total', 'counter', 'Total HTTP requests');
 * incr('http_requests_total', { method: 'GET', status: '200' });
 * gauge('active_workers', 4);
 */

/** @type {Map<string, {meta: object, value: number, labels: object}>} */
const store = new Map();

/** @param {string} name @param {'counter'|'gauge'|'histogram'} type @param {string} help @param {object} [labels] */
function register(name, type, help, labels = {}) {
  store.set(name, { meta: { name, type, help }, value: 0, labels });
}

/** @param {string} name @param {object} [labels] */
function incr(name, labels = {}) {
  let m = store.get(name);
  if (!m) { register(name, 'counter', ''); m = store.get(name); }
  m.value++;
  // Auto-create with labels if first time
  if (Object.keys(labels).length > 0) {
    const key = name + JSON.stringify(labels);
    let lm = store.get(key);
    if (!lm) {
      store.set(key, { meta: { name, type: m.meta.type, help: m.meta.help }, value: 1, labels });
    } else {
      lm.value++;
    }
  }
}

/** @param {string} name @param {number} value @param {object} [labels] */
function gauge(name, value, labels = {}) {
  let m = store.get(name);
  if (!m) { register(name, 'gauge', ''); m = store.get(name); }
  m.value = value;
}

/** @param {string} name @param {number} value @param {object} [labels] */
function observe(name, value, labels = {}) {
  let m = store.get(name);
  if (!m) { register(name, 'histogram', ''); m = store.get(name); }
  // Store sum and count as special keys
  const sumKey = `${name}_sum`;
  const countKey = `${name}_count`;
  const sum = store.get(sumKey)?.value ?? 0;
  store.set(sumKey, { meta: { name: sumKey, type: 'histogram', help: '' }, value: sum + value, labels });
  const count = store.get(countKey)?.value ?? 0;
  store.set(countKey, { meta: { name: countKey, type: 'histogram', help: '' }, value: count + 1, labels });
}

/** @returns {string} Prometheus text format */
function prometheusFormat() {
  const lines = [];
  const seen = new Set();
  for (const [key, m] of store) {
    // Skip histogram internal keys, expose _sum and _count only
    if (key.includes('_sum') || key.includes('_count')) {
      const baseName = key.replace('_sum', '').replace('_count', '');
      if (!seen.has(baseName)) {
        const s = store.get(`${baseName}_sum`);
        const c = store.get(`${baseName}_count`);
        if (s) lines.push(`${baseName}_sum ${s.value}`);
        if (c) lines.push(`${baseName}_count ${c.value}`);
        seen.add(baseName);
      }
      continue;
    }
    if (key.startsWith('_hist_')) continue;
    const labelStr = Object.keys(m.labels).length > 0
      ? `{${Object.entries(m.labels).map(([k, v]) => `${k}="${v}"`).join(',')}}`
      : '';
    lines.push(`${m.meta.name}${labelStr} ${m.value}`);
  }
  return lines.join('\n') + '\n';
}

const http = require('http');

/** @param {number} [port]
 * @returns {import('http').Server} */
function startMetricsServer(port = 9090) {
  const server = http.createServer((req, res) => {
    if (req.url === '/metrics') {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end(prometheusFormat());
    } else {
      res.writeHead(404);
      res.end();
    }
  });
  server.listen(port, () => {
    process.stderr.write(`[metrics] Prometheus server listening on port ${port}\n`);
  });
  return server;
}

module.exports = { register, incr, gauge, observe, prometheusFormat, startMetricsServer };
