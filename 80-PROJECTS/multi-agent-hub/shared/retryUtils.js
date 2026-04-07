/**
 * Exponential backoff retry utility for API calls.
 */

const DEFAULT_MAX_RETRIES = 3;
const DEFAULT_BASE_DELAY_MS = 1000;
const DEFAULT_MAX_DELAY_MS = 16000;

export class RetryError extends Error {
  constructor(message, attempts, lastError) {
    super(message);
    this.name = 'RetryError';
    this.attempts = attempts;
    this.lastError = lastError;
  }
}

/**
 * Retry a function with exponential backoff.
 * @param {Function} fn - Async function to retry
 * @param {Object} options
 * @param {number} options.maxRetries - Max retry attempts (default 3)
 * @param {number} options.baseDelayMs - Base delay in ms (default 1000)
 * @param {number} options.maxDelayMs - Max delay cap in ms (default 16000)
 * @param {Function} [options.shouldRetry] - (err) => boolean, whether to retry on this error
 * @param {Function} [options.onRetry] - (err, attempt, delay) => void, called before each retry
 * @param {AbortSignal} [options.signal] - AbortSignal to cancel retry loop
 */
export async function withRetry(fn, options = {}) {
  const {
    maxRetries = DEFAULT_MAX_RETRIES,
    baseDelayMs = DEFAULT_BASE_DELAY_MS,
    maxDelayMs = DEFAULT_MAX_DELAY_MS,
    shouldRetry = defaultShouldRetry,
    onRetry = null,
    signal = null,
  } = options;

  let lastError;
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    if (signal?.aborted) throw new RetryError('Aborted', attempt, lastError);

    try {
      return await fn();
    } catch (err) {
      lastError = err;

      if (attempt === maxRetries) break;

      if (!shouldRetry(err)) {
        throw new RetryError(
          `Non-retryable error: ${err.message}`,
          attempt + 1,
          err
        );
      }

      // Check if signal is aborted before delay
      if (signal?.aborted) throw new RetryError('Aborted', attempt, lastError);

      const delay = Math.min(baseDelayMs * Math.pow(2, attempt), maxDelayMs);
      // Add jitter (±20%)
      const jitter = delay * 0.2 * (Math.random() * 2 - 1);
      const actualDelay = delay + jitter;

      if (onRetry) onRetry(err, attempt + 1, actualDelay);

      await sleep(actualDelay);
    }
  }

  throw new RetryError(
    `All ${maxRetries + 1} attempts failed. Last error: ${lastError.message}`,
    maxRetries + 1,
    lastError
  );
}

function defaultShouldRetry(err) {
  // Retry on network errors and 5xx / 429 status codes
  if (err.message.includes('network') || err.message.includes('fetch'))
    return true;
  if (err.status === 429 || err.status === 503 || err.status === 504)
    return true;
  return false;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
