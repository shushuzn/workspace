/**
 * Safety guardrails for AI roundtable.
 *
 * Checks:
 * - Input sanitization (strip control chars, limit length)
 * - Jailbreak pattern detection (simple heuristic)
 * - Output filtering (basic sensitive content detection)
 */

const MAX_INPUT_LENGTH = 4000;
const MAX_TOPIC_LENGTH = 200;

// Simple jailbreak keyword patterns (heuristic, not exhaustive)
const JAILBREAK_PATTERNS = [
  /ignore (all )?(previous|prior|above|earlier) (instructions?|rules?|constraints?)/i,
  /(disregard|forget) (all )?(your|previous) (instructions?|rules?)/i,
  /you are now (?:a |an )?different/i,
  /forget (?:your )?(?:system |ethical )?(?:constraints?|guidelines?|instructions?)/i,
  /pretend (?:you are |to be )/i,
  /do (?:anything|whatever) (?:I|you) (?:say|tell)/i,
  /disable (?:your |the )?(?:safety |content )?(?:filters?|restrictions?|moderation)/i,
  /override (?:your |the )?(?:safety |content )?(?:filters?|restrictions?)/i,
];

// Sensitive content patterns (basic detection)
const SENSITIVE_PATTERNS = [
  /[A-Z]{10,}/, // Long all-caps (credit card-like)
  /\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}/, // Credit card format
];

export class SafetyResult {
  constructor({ allowed, reason, sanitized }) {
    this.allowed = allowed;
    this.reason = reason;
    this.sanitized = sanitized;
  }
}

/**
 * Check a user input string.
 * @param {string} input
 * @returns {SafetyResult}
 */
export function checkInput(input) {
  if (!input || typeof input !== 'string') {
    return new SafetyResult({
      allowed: false,
      reason: 'empty input',
      sanitized: '',
    });
  }

  // Length check
  if (input.length > MAX_INPUT_LENGTH) {
    return new SafetyResult({
      allowed: false,
      reason: `input too long (${input.length} > ${MAX_INPUT_LENGTH})`,
      sanitized: input.slice(0, MAX_INPUT_LENGTH),
    });
  }

  // Control character check
  // eslint-disable-next-line no-control-regex
  const sanitized = input.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
  if (sanitized.length < input.length) {
    // stripped some control chars, but still proceed with sanitized
  }

  // Jailbreak detection
  for (const pattern of JAILBREAK_PATTERNS) {
    if (pattern.test(sanitized)) {
      return new SafetyResult({
        allowed: false,
        reason: 'potential jailbreak prompt detected',
        sanitized,
      });
    }
  }

  return new SafetyResult({ allowed: true, reason: null, sanitized });
}

/**
 * Check a discussion topic.
 * @param {string} topic
 * @returns {SafetyResult}
 */
export function checkTopic(topic) {
  if (!topic || typeof topic !== 'string') {
    return new SafetyResult({
      allowed: false,
      reason: 'empty topic',
      sanitized: '',
    });
  }

  if (topic.length > MAX_TOPIC_LENGTH) {
    return new SafetyResult({
      allowed: false,
      reason: `topic too long (${topic.length} > ${MAX_TOPIC_LENGTH})`,
      sanitized: topic.slice(0, MAX_TOPIC_LENGTH),
    });
  }

  // eslint-disable-next-line no-control-regex
  const sanitized = topic.replace(/[\x00-\x1F\x7F]/g, '').trim();

  return new SafetyResult({ allowed: true, reason: null, sanitized });
}

/**
 * Check LLM output for sensitive content.
 * @param {string} output
 * @returns {SafetyResult}
 */
export function checkOutput(output) {
  if (!output || typeof output !== 'string') {
    return new SafetyResult({ allowed: true, reason: null, sanitized: '' });
  }

  for (const pattern of SENSITIVE_PATTERNS) {
    if (pattern.test(output)) {
      return new SafetyResult({
        allowed: true, // flag but don't block
        reason: 'sensitive pattern detected in output',
        sanitized: output,
      });
    }
  }

  return new SafetyResult({ allowed: true, reason: null, sanitized: output });
}
