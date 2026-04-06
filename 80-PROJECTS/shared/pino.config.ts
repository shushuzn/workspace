/**
 * Shared pino logger configuration for 80-PROJECTS TypeScript projects.
 *
 * Log levels: trace(10) < debug(20) < info(30) < warn(40) < error(50)
 *
 * Usage in other projects:
 *   import { createLogger } from '../shared/pino.config.js';
 *   const logger = createLogger(import.meta.url);
 *
 * Or with a custom name:
 *   import { createLogger } from '../shared/pino.config.js';
 *   const logger = createLogger(import.meta.url, 'my-app');
 */
import pino from 'pino';

const isTest = process.env.NODE_ENV === 'test';
const isProd = process.env.NODE_ENV === 'production';

export interface LoggerOptions {
  name?: string;
  level?: string;
}

/**
 * Create a configured pino logger instance.
 * @param metaUrl - Pass `import.meta.url` from the calling module for correct file resolution.
 * @param options - Optional logger name and level override.
 */
export function createLogger(metaUrl: string, options: LoggerOptions = {}): pino.Logger {
  const label = options.name ?? metaUrl.split('/').pop()?.replace(/\.[cm]?ts$/, '') ?? 'app';

  return pino({
    name: label,
    level: options.level ?? (isTest ? 'silent' : isProd ? 'info' : 'debug'),
    formatters: {
      level: (label) => ({ level: label }),
    },
    timestamp: pino.stdTimeFunctions.isoTime,
    ...(isProd
      ? {
          transport: {
            targets: [{ target: 'pino/file', level: 'info', destination: 1 }],
          },
        }
      : {}),
  });
}

/**
 * Default logger instance for projects that don't need per-module loggers.
 */
export const logger = createLogger(import.meta.url);
