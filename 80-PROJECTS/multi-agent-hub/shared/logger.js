/**
 * Structured logger backed by pino.
 *
 * Log levels: trace(10) < debug(20) < info(30) < warn(40) < error(50)
 *
 * Colour output to console is preserved via pino-pretty (dev dependency).
 * In production, JSON logs are written to file via transport.
 */
import pino from 'pino';

const isTest = process.env.NODE_ENV === 'test';
const isProd = process.env.NODE_ENV === 'production';

export const logger = pino({
  level: isTest ? 'silent' : isProd ? 'info' : 'debug',
  formatters: {
    level: label => ({ level: label }),
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

/**
 * Wrap a value with a colour code for console output.
 * Returns ANSI-escaped string for terminal colours.
 */
export function color(msg, colorCode) {
  return `\x1b[${colorCode}m${msg}\x1b[0m`;
}
