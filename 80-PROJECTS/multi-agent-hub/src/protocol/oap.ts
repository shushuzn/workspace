/**
 * OpenClaw Agent Protocol (OAP) — Unified Agent Communication Protocol
 * Version 1.0.0
 *
 * Enables seamless task dispatch and result aggregation between:
 * - opencli (browser automation)
 * - task-orchestrator (workflow execution)
 * - multi-agent-hub (cognitive annealing + debate)
 *
 * Usage:
 *   import { OAPClient, OAPHub, createTask } from './protocol/oap';
 */

export type OAPVersion = '1.0.0';

export type TaskPriority = 'low' | 'normal' | 'high' | 'critical';

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

export type ResultFormat = 'json' | 'text' | 'html' | 'screenshot';

/** Task intent classification */
export type TaskIntent =
  | 'browse'        // opencli handles
  | 'execute'       // task-orchestrator handles
  | 'debate'        // multi-agent-hub handles
  | 'analyze'       // multi-agent-hub handles
  | 'orchestrate';  // task-orchestrator handles

export interface Capability {
  name: string;
  version: string;
  inputSlots: string[];
  outputSlots: string[];
  adapterType?: 'opencli' | 'task-orchestrator' | 'multi-agent-hub';
}

export interface TaskHeader {
  id: string;
  version: OAPVersion;
  intent: TaskIntent;
  priority: TaskPriority;
  deadline?: number;      // Unix timestamp
  correlationId?: string;  // For tracing across agents
  sourceAgent: string;
  targetAgent?: string;   // Unicast; if absent → broadcast
}

export interface OAPEnvelope<T = unknown> {
  header: TaskHeader;
  body: OAPBody<T>;
}

export interface OAPBody<T = unknown> {
  action: 'dispatch' | 'result' | 'error' | 'negotiate' | 'heartbeat' | 'cancel';
  targetCapability?: string;
  negotiateCapabilities?: Capability[];
  task?: OAPTask<T>;
  result?: OAPResult<T>;
  error?: OAPError;
  cancelReason?: string;
}

export interface OAPTask<T = unknown> {
  id: string;
  intent: TaskIntent;
  description: string;
  input: T;
  outputFormat?: ResultFormat;
  maxDuration?: number;  // ms
  retries?: number;
  metadata?: Record<string, unknown>;
}

export interface OAPResult<T = unknown> {
  taskId: string;
  status: 'success' | 'partial' | 'failed';
  output?: T;
  format: ResultFormat;
  metrics?: ResultMetrics;
  partialResults?: OAPResult<T>[];  // For federated tasks
  metadata?: Record<string, unknown>;
}

export interface ResultMetrics {
  durationMs: number;
  tokensUsed?: number;
  rounds?: number;
  intermediateSteps?: number;
}

export interface OAPError {
  code: string;
  message: string;
  recoverable: boolean;
  retryAfter?: number;  // ms
  details?: unknown;
}

/** Negotiate with target agents about capabilities before dispatching */
export interface CapabilityNegotiation {
  offered: Capability[];
  required: string[];  // Required capability names
  preferred: string[];  // Preferred but not required
}

export interface OAPRouter {
  /** Route a task to the best-fit agent based on intent + capabilities */
  route(intent: TaskIntent, input: unknown, capabilities: Capability[]): string | null;
  /** Check if an agent claims to handle a given intent */
  canHandle(agentId: string, intent: TaskIntent, capabilities: Capability[]): boolean;
}

/** Built-in intent → adapter type mapping */
export const INTENT_ADAPTER_MAP: Record<TaskIntent, string> = {
  browse: 'opencli',
  execute: 'task-orchestrator',
  debate: 'multi-agent-hub',
  analyze: 'multi-agent-hub',
  orchestrate: 'task-orchestrator',
};

// ─── Factory helpers ────────────────────────────────────────────────────────

let _idCounter = 0;
export function generateOAPId(prefix = 'oap'): string {
  return `${prefix}-${Date.now()}-${++_idCounter}`;
}

export function createTask<T = unknown>(
  intent: TaskIntent,
  description: string,
  input: T,
  opts: Partial<OAPTask<T>> & { sourceAgent: string; priority?: TaskPriority; targetCapability?: string } = {} as any
): OAPEnvelope<T> {
  return {
    header: {
      id: generateOAPId(),
      version: '1.0.0',
      intent,
      priority: opts.priority ?? 'normal',
      sourceAgent: opts.sourceAgent,
    },
    body: {
      action: 'dispatch',
      targetCapability: opts.targetCapability,
      task: {
        id: generateOAPId('task'),
        intent,
        description,
        input,
        outputFormat: opts.outputFormat ?? 'json',
        maxDuration: opts.maxDuration,
        retries: opts.retries,
        metadata: opts.metadata,
      },
    },
  };
}

export function createResult<T = unknown>(
  taskId: string,
  status: OAPResult<T>['status'],
  output: T,
  opts: Partial<OAPResult<T>> & { format?: ResultFormat; durationMs?: number } = {}
): OAPEnvelope<T> {
  return {
    header: {
      id: generateOAPId(),
      version: '1.0.0',
      intent: 'orchestrate',
      priority: 'normal',
      sourceAgent: 'local',
    },
    body: {
      action: 'result',
      result: {
        taskId,
        status,
        output,
        format: opts.format ?? 'json',
        metrics: opts.durationMs ? { durationMs: opts.durationMs } : undefined,
        partialResults: opts.partialResults,
        metadata: opts.metadata,
      },
    },
  };
}

export function createError(
  taskId: string,
  code: string,
  message: string,
  recoverable = false
): OAPEnvelope {
  return {
    header: {
      id: generateOAPId(),
      version: '1.0.0',
      intent: 'orchestrate',
      priority: 'normal',
      sourceAgent: 'local',
    },
    body: {
      action: 'error',
      error: { code, message, recoverable },
    },
  };
}

/** Simple default router using intent → adapter type mapping */
export class DefaultOAPRouter implements OAPRouter {
  private agents = new Map<string, { intent: TaskIntent; capabilities: Capability[] }>();

  registerAgent(agentId: string, intent: TaskIntent, capabilities: Capability[] = []) {
    this.agents.set(agentId, { intent, capabilities });
  }

  route(intent: TaskIntent, _input: unknown, _capabilities: Capability[]): string | null {
    const target = INTENT_ADAPTER_MAP[intent];
    for (const [agentId, info] of this.agents) {
      if (info.intent === intent) return agentId;
    }
    return null;  // No agent registered for this intent
  }

  canHandle(agentId: string, intent: TaskIntent, _capabilities: Capability[]): boolean {
    const info = this.agents.get(agentId);
    if (!info) return false;
    return info.intent === intent;
  }
}
