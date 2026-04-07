/**
 * Prometheus metrics for ai-roundtable observability.
 *
 * Exposes:
 *   - ai_roundtable_llm_calls_total (counter, labels: provider, cached)
 *   - ai_roundtable_llm_latency_seconds (histogram, labels: provider)
 *   - ai_roundtable_rounds_total (counter)
 *   - ai_roundtable_cache_hits_total (counter)
 *   - ai_roundtable_cache_misses_total (counter)
 *
 * Start the /metrics endpoint with: metrics.startServer(port)
 */
import client from 'prom-client';

const register = new client.Registry();

register.setDefaultLabels({ app: 'ai-roundtable' });

// LLM call counter
export const llmCallsTotal = new client.Counter({
  name: 'ai_roundtable_llm_calls_total',
  help: 'Total LLM API calls',
  labelNames: ['provider', 'cached'],
  registers: [register],
});

// LLM latency histogram
export const llmLatencySeconds = new client.Histogram({
  name: 'ai_roundtable_llm_latency_seconds',
  help: 'LLM API call latency in seconds',
  labelNames: ['provider'],
  buckets: [0.1, 0.25, 0.5, 1, 2, 5, 10],
  registers: [register],
});

// Discussion rounds counter
export const roundsTotal = new client.Counter({
  name: 'ai_roundtable_rounds_total',
  help: 'Total discussion rounds completed',
  registers: [register],
});

// Cache counters
export const cacheHitsTotal = new client.Counter({
  name: 'ai_roundtable_cache_hits_total',
  help: 'Total chat cache hits',
  registers: [register],
});

export const cacheMissesTotal = new client.Counter({
  name: 'ai_roundtable_cache_misses_total',
  help: 'Total chat cache misses',
  registers: [register],
});

/**
 * Time an async operation and record it to the given histogram.
 */
export async function timedOperation(provider, fn) {
  const end = llmLatencySeconds.startTimer({ provider });
  try {
    const result = await fn();
    return result;
  } finally {
    end();
  }
}

/**
 * Start an HTTP server exposing /metrics.
 * Call this once at startup.
 */
export async function startServer(port = 9090) {
  const http = await import('http');
  http
    .createServer(async (req, res) => {
      if (req.url === '/metrics') {
        res.setHeader('Content-Type', register.contentType);
        res.end(await register.metrics());
      } else {
        res.statusCode = 404;
        res.end('Not found');
      }
    })
    .listen(port, () => {
      console.log(
        `Metrics server listening on http://localhost:${port}/metrics`
      );
    });
}
