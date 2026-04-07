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
  dryRun?: boolean;
}

export interface Step {
  adapterId: string;
  adapterType: 'opencli' | 'cli-anything' | 'multi-agent-hub' | 'swarm' | 'wikipedia';
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
  /** Distributed trace ID for cross-project request tracing */
  traceId?: string;
  /** Arbitrary metadata from the adapter */
  metadata?: Record<string, unknown>;
  /** Sequence number for ordering (stream.ts) */
  seq?: number;
}

export interface Adapter {
  id: string;
  type: 'opencli' | 'cli-anything' | 'multi-agent-hub' | 'swarm' | 'wikipedia';
  canHandle(step: Step): boolean;
  execute(step: Step, ctx: Context): Promise<Result>;
  checkAvailable(): Promise<boolean>;
  register?(): AdapterRegistration | null;
}

/** OAP protocol result envelope */
export interface OAPResult<T = unknown> {
  id: string;
  version: string;
  status: 'ok' | 'error';
  result?: T;
  error?: string;
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

// ─── CLI Adapter Registry Schema ───────────────────────────────────────────────

/**
 * Canonical registry entry for CLI-Anything adapters.
 * Consumed by: task-orchestrator, opencli, and any tool that wants to
 * discover/use CLI-Anything adapters without maintaining its own registry copy.
 */
export interface CliAdapterEntry {
  name: string;
  display_name: string;
  description: string;
  install_cmd: string;
  entry_point: string;
  skill_md: string | null;
  category: string;
  keywords?: string[];
}

/** Raw registry JSON format produced by CLI-Anything */
export interface CliAdapterRegistry {
  meta?: {
    repo?: string;
    description?: string;
    updated?: string;
  };
  clis: CliAdapterEntry[];
}

/** Normalized adapter registration for planner routing */
export interface CliAdapterRegistration {
  adapterId: string;       // maps to entry_point (e.g. "cli-anything-wiremock")
  keywords: string[];
  displayName: string;
  description: string;
  category: string;
  commands: string[];
  outputSlots?: string[];
  priority?: number;
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

// ─── Task Dispatch Schema ─────────────────────────────────────────────────────

export interface StepSpec {
  stepId?: string;
  adapterType: 'opencli' | 'cli-anything' | 'multi-agent-hub' | 'swarm' | 'wikipedia';
  command: string;
  args?: string[];
  inputSlots?: string[];
  outputSlots?: string[];
  timeoutMs?: number;
  maxRetries?: number;
}

export interface TaskDispatchExt {
  taskId: string;
  prompt?: string;
  steps?: StepSpec[];
}
