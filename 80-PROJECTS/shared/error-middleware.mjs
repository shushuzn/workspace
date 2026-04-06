/**
 * Shared Error Middleware for 80-PROJECTS Node.js packages.
 *
 * Features:
 *   - Request ID generation (UUID v4)
 *   - Request/response logging hook (pino-compatible)
 *   - Error boundary wrapper
 *   - HTTP error class hierarchy
 *
 * Usage:
 *   import { reqID, logRequest, logError, errorBoundary, HttpError } from '../shared/error-middleware.js';
 *
 *   // In your HTTP handler:
 *   const id = reqID();
 *   logRequest(logger, { method, url, headers }, id);
 *   try {
 *     const result = await errorBoundary(myAsyncHandler, req, res, id);
 *   } catch (err) {
 *     logError(logger, err, id);
 *   }
 */

import { randomUUID } from 'crypto';

/** Generate a short request ID (8 hex chars). */
export function reqID() {
  return randomUUID().split('-')[0];
}

// ─── HTTP Errors ─────────────────────────────────────────────────────────────

export class HttpError extends Error {
  constructor(statusCode, message, code) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.name = 'HttpError';
  }
}

export const BadRequest = (msg = 'Bad Request') => new HttpError(400, msg, 'BAD_REQUEST');
export const Unauthorized = (msg = 'Unauthorized') => new HttpError(401, msg, 'UNAUTHORIZED');
export const Forbidden = (msg = 'Forbidden') => new HttpError(403, msg, 'FORBIDDEN');
export const NotFound = (msg = 'Not Found') => new HttpError(404, msg, 'NOT_FOUND');
export const Conflict = (msg = 'Conflict') => new HttpError(409, msg, 'CONFLICT');
export const InternalError = (msg = 'Internal Server Error') => new HttpError(500, msg, 'INTERNAL_ERROR');

// ─── Logging helpers ─────────────────────────────────────────────────────────

/**
 * Log an incoming HTTP request.
 * @param logger - pino logger instance
 * @param req - { method, url, headers }
 * @param id - request ID from reqID()
 */
export function logRequest(logger, req, id) {
  logger.info({ reqId: id, method: req.method, url: req.url, ua: req.headers?.['user-agent'] }, '→ request');
}

/**
 * Log a response.
 * @param logger - pino logger instance
 * @param res - { statusCode }
 * @param id - request ID
 * @param extra - additional fields
 */
export function logResponse(logger, res, id, extra = {}) {
  logger.info({ reqId: id, status: res.statusCode, ...extra }, '← response');
}

/**
 * Log an error with request ID context.
 * @param logger - pino logger instance
 * @param err - Error or HttpError
 * @param id - request ID
 */
export function logError(logger, err, id) {
  if (err instanceof HttpError) {
    logger.warn({ reqId: id, statusCode: err.statusCode, code: err.code, message: err.message }, 'http error');
  } else {
    logger.error({ reqId: id, error: err.message, stack: err.stack }, 'unhandled error');
  }
}

/**
 * Wrap an async HTTP handler to catch exceptions and send JSON error responses.
 * Returns the handler's result on success, or sends a JSON error response and returns null.
 *
 * @param handler - async function(req, res, id) returning a value
 * @param res - http.ServerResponse
 * @param id - request ID
 * @param defaultStatus - HTTP status for non-HttpError errors (default 500)
 */
export async function errorBoundary(handler, res, id, defaultStatus = 500) {
  try {
    return await handler();
  } catch (err) {
    if (err instanceof HttpError) {
      res.statusCode = err.statusCode;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ error: err.message, code: err.code, reqId: id }));
    } else {
      res.statusCode = defaultStatus;
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ error: 'Internal Server Error', reqId: id }));
    }
    return null;
  }
}

// ─── Express/Koa adapter hint ─────────────────────────────────────────────────
/**
 * Express middleware factory (for projects that use Express).
 * Usage: app.use(errorMiddleware(logger))
 *
 * @param logger - pino logger instance
 * @returns Express error handler middleware
 */
export function expressErrorMiddleware(logger) {
  return (err, req, res, _next) => {
    const id = req.headers['x-req-id'] ?? reqID();
    logError(logger, err, id);
    const status = err instanceof HttpError ? err.statusCode : 500;
    res.status(status).json({ error: err.message, code: err.code, reqId: id });
  };
}
