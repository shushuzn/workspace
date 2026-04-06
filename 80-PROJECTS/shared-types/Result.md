# shared-types — Type Reference

> Auto-generated — run `node generate-result-md.mjs` to update

## Exports

| Name | Type | Fields |
|------|------|--------|
| `Artifact` | interface | type: 'screenshot' | 'video' | 'file' | 'text', path: string, metadata: Record<string, unknown> |
| `TaskContext` | interface | artifactRef: string]: Artifact |
| `Context` | interface | taskContext: TaskContext, workingDir: string, env: NodeJS.ProcessEnv, interactive: boolean... |
| `Step` | interface | adapterId: string, adapterType: 'opencli' | 'cli-anything' | 'multi-agent-hub' | 'swarm', command: string, args: string[]... |
| `ErrorCode` | type | (complex) |
| `Result` | interface | success: boolean, output: string, logs: string, artifacts: Artifact[]... |
| `Adapter` | interface | id: string, type: 'opencli' | 'cli-anything' | 'multi-agent-hub', step: Step): boolean, step: Step, ctx: Context): Promise<Result> |
| `AdapterRegistration` | interface | adapterId: string, keywords: string[], commands: string[], outputSlots: string[]... |
| `PlannerOutput` | interface | steps: Step[], errors: string[], warnings: string[], matchedKeywords: string[]... |
| `HttpRequest` | interface | method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS', url: string, headers: Record<string, string>, queryParams: Record<string, string | number | boolean>... |
| `HttpResponse` | interface | status: number, statusText: string, headers: Record<string, string>, body: unknown... |
| `HttpAdapterResult` | interface | response: HttpResponse, error: string, code: ErrorCode, attempts: number... |
| `HTTP_REQUEST_SCHEMA` | type | type: 'object',, properties: {, method: { type: 'string', enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'] },, url: { type: 'string', format: 'uri' },... |
| `HTTP_RESPONSE_SCHEMA` | type | type: 'object',, properties: {, status: { type: 'number', minimum: 100, maximum: 599 },, statusText: { type: 'string' },... |

---

## Full Source

```typescript
/**
 * Shared TypeScript types for 80-PROJECTS orchestration packages.
 *
 * Re-exported by: task-orchestrator, multi-agent-hub, opencli
 */
export interface Artifact {
  type: 'screenshot' | 'video' | 'file' | 'text';
  path: string;
  metadata?: Record<string, unknown>;
}

export interface TaskContext {
  [artifactRef: string]: Artifact;
}

export interface Context {
  taskContext: TaskContext;
  workingDir: string;
  env: NodeJS.ProcessEnv;
  interactive: boolean;
  prompt?: string;
}

export interface Step {
  adapterId: string;
  adapterType: 'opencli' | 'cli-anything' | 'multi-agent-hub' | 'swarm';
  command: string;
  args: string[];
  inputSlots: string[];
  outputSlots: string[];
  timeoutMs?: number;
  maxRetries?: number;
}

export type ErrorCode =
  | 'E001'   // Adapter not found
  | 'E002'   // Validation failed
  | 'E003'   // Step timed out
  | 'E004'   // Execution error
  | 'E005'   // Recoverable error
  | 'E006'   // Skipped due to cascade
  | 'ADAPTER_NOT_FOUND'
  | 'ADAPTER_NOT_AVAILABLE'
  | 'STEP_TIMEOUT'
  | 'EXECUTION_ERROR'
  | 'CASCADE_STOP'
  | 'INPUT_SLOT_MISSING'
  | 'OUTPUT_SLOT_MISSING'
  | 'RETRY_EXHAUSTED'
  | 'STRATEGY_SKIP'
  | 'STRATEGY_FALLBACK_FAILED'
  | 'NETWORK_ERROR'
  | 'AUTH_ERROR'
  | 'RATE_LIMITED'
  | 'INTERNAL_ERROR';

export interface Result {
  success: boolean;
  output: string;
  logs: string;
  artifacts: Artifact[];
  error?: string;
  code?: ErrorCode;
  fatal: boolean;
  retryMs?: number;
  attempts?: number;
  cached?: boolean;
  durationMs?: number;
  /** Causality chain: IDs of tasks that preceded this result */
  causalityChain?: string[];
  /** Parent task ID that dispatched this subtask */
  parentTaskId?: string;
  /** Arbitrary metadata from the adapter */
  metadata?: Record<string, unknown>;
}

export interface Adapter {
  id: string;
  type: 'opencli' | 'cli-anything' | 'multi-agent-hub';
  canHandle(step: Step): boolean;
  execute(step: Step, ctx: Context): Promise<Result>;
  checkAvailable(): Promise<boolean>;
  register?(): AdapterRegistration | null;
}

export interface AdapterRegistration {
  adapterId: string;
  keywords: string[];
  commands: string[];
  outputSlots?: string[];
  priority?: number;
}

export interface PlannerOutput {
  steps: Step[];
  errors: string[];
  warnings?: string[];
  matchedKeywords?: string[];
  /** Detailed match trace: keyword → rule that matched */
  matchedRules?: Array<{ keyword: string; ruleId: string; adapterId: string; command: string }>;
}

// ─── HTTP Adapter Schema ─────────────────────────────────────────────────────

export interface HttpRequest {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';
  url: string;
  headers?: Record<string, string>;
  queryParams?: Record<string, string | number | boolean>;
  body?: unknown;
  timeoutMs?: number;
  retries?: number;
  /** Follow redirects (default: true) */
  followRedirects?: boolean;
  /** Expected response content-type hint */
  accept?: string;
}

export interface HttpResponse {
  status: number;
  statusText: string;
  headers: Record<string, string>;
  body: unknown;
  /** Time in ms from request start to response headers received */
  latencyMs: number;
  /** Final URL after all redirects */
  finalUrl?: string;
}

export interface HttpAdapterResult {
  response: HttpResponse;
  error?: string;
  code?: ErrorCode;
  attempts: number;
  durationMs: number;
}

/** JSON Schema fragment for HTTP request validation (供 ajv / zod 使用) */
export const HTTP_REQUEST_SCHEMA = {
  type: 'object',
  properties: {
    method: { type: 'string', enum: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'] },
    url: { type: 'string', format: 'uri' },
    headers: { type: 'object', additionalProperties: { type: 'string' } },
    queryParams: { type: 'object', additionalProperties: { oneOf: [{ type: 'string' }, { type: 'number' }, { type: 'boolean' }] } },
    body: {},
    timeoutMs: { type: 'number', minimum: 0 },
    retries: { type: 'number', minimum: 0 },
    followRedirects: { type: 'boolean' },
    accept: { type: 'string' },
  },
  required: ['method', 'url'],
  additionalProperties: false,
} as const;

/** JSON Schema fragment for HTTP response validation */
export const HTTP_RESPONSE_SCHEMA = {
  type: 'object',
  properties: {
    status: { type: 'number', minimum: 100, maximum: 599 },
    statusText: { type: 'string' },
    headers: { type: 'object', additionalProperties: { type: 'string' } },
    body: {},
    latencyMs: { type: 'number', minimum: 0 },
    finalUrl: { type: 'string', format: 'uri' },
  },
  required: ['status', 'statusText', 'headers', 'body'],
  additionalProperties: false,
} as const;

```