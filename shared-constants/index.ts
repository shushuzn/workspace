/**
 * shared-constants/index.ts — Shared constants across 80-PROJECTS
 * Usage: import { ERROR_CODES, CONFIG_KEYS } from 'shared-constants';
 */

// Standard HTTP status codes used across projects
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  ACCEPTED: 202,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  TIMEOUT: 408,
  CONFLICT: 409,
  PAYLOAD_TOO_LARGE: 413,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  BAD_GATEWAY: 502,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

// Common environment/config keys
export const CONFIG_KEYS = {
  OLLAMA_BASE_URL: 'OLLAMA_BASE_URL',
  OPENAI_API_KEY: 'OPENAI_API_KEY',
  OPENAI_BASE_URL: 'OPENAI_BASE_URL',
  MINIMAX_API_KEY: 'MINIMAX_API_KEY',
  MINIMAX_BASE_URL: 'MINIMAX_BASE_URL',
  ANTHROPIC_API_KEY: 'ANTHROPIC_API_KEY',
  GITHUB_TOKEN: 'GITHUB_TOKEN',
  NODE_ENV: 'NODE_ENV',
  LOG_LEVEL: 'LOG_LEVEL',
  PORT: 'PORT',
  HOST: 'HOST',
  DATABASE_URL: 'DATABASE_URL',
  REDIS_URL: 'REDIS_URL',
} as const;

// ─── Result Schema (mirrors AI task result structure) ────────────────────────

export type ResultStatus = 'success' | 'error' | 'timeout' | 'cancelled';

export interface Result<T = unknown> {
  success: boolean;
  output: T | null;
  artifacts: unknown[];
  fatal: boolean;
  error: string | null;
  durationMs: number;
  statusCode?: number;
  causalityChain?: string[];
  parentTaskId?: string;
}

// ─── Log Levels ────────────────────────────────────────────────────────────

export enum LogLevel {
  DEBUG = 10,
  INFO = 20,
  WARN = 30,
  ERROR = 40,
  FATAL = 50,
}

export const LOG_LEVEL_NAMES: Record<LogLevel, string> = {
  [LogLevel.DEBUG]: 'DEBUG',
  [LogLevel.INFO]: 'INFO',
  [LogLevel.WARN]: 'WARN',
  [LogLevel.ERROR]: 'ERROR',
  [LogLevel.FATAL]: 'FATAL',
};

// ─── Event Types ───────────────────────────────────────────────────────────

export const EVENT_TYPES = {
  TASK_START: 'task:start',
  TASK_COMPLETE: 'task:complete',
  TASK_FAIL: 'task:fail',
  TASK_TIMEOUT: 'task:timeout',
  AGENT_INVOKE: 'agent:invoke',
  AGENT_RESULT: 'agent:result',
  MCP_CALL: 'mcp:call',
  MCP_RESULT: 'mcp:result',
  BROWSER_ACTION: 'browser:action',
  HTTP_REQUEST: 'http:request',
  HTTP_RESPONSE: 'http:response',
} as const;

export type EventType = (typeof EVENT_TYPES)[keyof typeof EVENT_TYPES];

// ─── Error Codes ───────────────────────────────────────────────────────────

export const ERROR_CODES = {
  TASK_TIMEOUT: 'TASK_TIMEOUT',
  TASK_CANCELLED: 'TASK_CANCELLED',
  TASK_NOT_FOUND: 'TASK_NOT_FOUND',
  BRIDGE_NOT_FOUND: 'BRIDGE_NOT_FOUND',
  ADAPTER_ERROR: 'ADAPTER_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
  AUTH_ERROR: 'AUTH_ERROR',
  PERMISSION_DENIED: 'PERMISSION_DENIED',
  RATE_LIMITED: 'RATE_LIMITED',
  INTERNAL_ERROR: 'INTERNAL_ERROR',
} as const;
