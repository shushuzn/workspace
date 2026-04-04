/**
 * Token bucket rate limiter for API calls.
 *
 * Each bucket holds up to `maxTokens` tokens. Tokens replenish at
 * `refillRate` per second. When `acquire()` is called, it waits until
 * a token is available or the timeout expires.
 */

export class RateLimiter {
  /**
   * @param {Object} options
   * @param {number} options.maxTokens - Maximum bucket size (default 60)
   * @param {number} options.refillRate - Tokens per second (default 30)
   * @param {string} [options.name] - Label for logging (default 'default')
   */
  constructor(options = {}) {
    this.maxTokens = options.maxTokens ?? 60;
    this.refillRate = options.refillRate ?? 30;
    this.name = options.name ?? 'default';
    this._tokens = this.maxTokens;
    this._lastRefill = Date.now();
    this._queue = [];
    this._running = false;
  }

  _refill() {
    const now = Date.now();
    const elapsed = (now - this._lastRefill) / 1000;
    const added = elapsed * this.refillRate;
    this._tokens = Math.min(this.maxTokens, this._tokens + added);
    this._lastRefill = now;
  }

  /**
   * Acquire a token. Returns a promise that resolves when a token is available.
   * @param {number} [timeoutMs=30000] - Max wait time
   * @param {AbortSignal} [signal] - AbortSignal to cancel waiting
   * @returns {Promise<void>}
   */
  async acquire(timeoutMs = 30000, signal = null) {
    this._refill();

    if (this._tokens >= 1) {
      this._tokens -= 1;
      return;
    }

    // Need to wait for a token
    return new Promise((resolve, reject) => {
      const startTime = Date.now();

      const timer = setInterval(() => {
        if (signal?.aborted) {
          clearInterval(timer);
          reject(new Error('Aborted'));
          return;
        }

        const elapsed = Date.now() - startTime;
        if (elapsed > timeoutMs) {
          clearInterval(timer);
          reject(new Error(`RateLimiter timeout after ${timeoutMs}ms for ${this.name}`));
          return;
        }

        this._refill();
        if (this._tokens >= 1) {
          this._tokens -= 1;
          clearInterval(timer);
          resolve();
        }
      }, 50);
    });
  }

  /** Sync check — returns true if a token is available without waiting */
  tryAcquire() {
    this._refill();
    if (this._tokens >= 1) {
      this._tokens -= 1;
      return true;
    }
    return false;
  }

  /** Current token level (for debugging/monitoring) */
  get availableTokens() {
    this._refill();
    return this._tokens;
  }
}

// Shared limiters per provider
export const limiters = {
  minimax: new RateLimiter({ maxTokens: 60, refillRate: 30, name: 'minimax' }),
  openai: new RateLimiter({ maxTokens: 500, refillRate: 250, name: 'openai' }),
  anthropic: new RateLimiter({ maxTokens: 50, refillRate: 25, name: 'anthropic' }),
  ollama: new RateLimiter({ maxTokens: 10, refillRate: 5, name: 'ollama' }),
};
