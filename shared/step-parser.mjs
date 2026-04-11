#!/usr/bin/env node
/**
 * shared/step-parser.mjs
 * Shared step parsing logic for run-seed.mjs and add-seed.mjs.
 * Single source of truth for step extraction regex and step-type classification.
 */

// ── Step-type classification ─────────────────────────────────────────────────

/** Shell commands that are read-only (no file modification intent) */
export const READONLY_PREFIXES = [
  /^ls\s/, /^grep\s/, /^cat\s/, /^head\s/, /^tail\s/, /^wc\s/,
  /^echo\s/, /^find\s/, /^which\s/, /^type\s/, /^stat\s/, /^pwd\s/,
  /^cd\s/,
];

/** Patterns that indicate file creation or modification */
export const FILE_CREATION_PATTERNS = [
  /\bEdit\s+/, /\bWrite\s+/, /\bCreate\s+/, /\bmkdir\s+/,
  /\btouch\s+/, /python\s+\S+\.py\b/, /node\s+\S+\.mjs\b/,
  /node\s+\S+\.js\b/, /bash\s+tee\b/, /#\s*!/,
];

/** Dangerous command patterns that fail on Windows Git Bash (order matters: longer patterns first) */
export const DANGEROUS_PATTERNS = [
  { pattern: /bash\s+node\s+-[epc]/i, name: 'bash node -e/p/c', alt: 'node script.mjs' },
  { pattern: /bash\s+tee\s+<<\s*EOF/i, name: 'heredoc tee', alt: 'python script.py or Write + node script.mjs' },
  { pattern: /node\s+-[epc]\s+/i, name: 'node -e/p/c inline', alt: 'node script.mjs or Write script then node script.mjs' },
  { pattern: /python\s+-c\s+["\'].*<<\s*EOF.*["\']/i, name: 'python heredoc in -c', alt: 'python script.py' },
];

/**
 * Classify a step as READONLY, IMPLEMENT, or INVALID.
 * @param {string} step - Step text (trimmed)
 * @returns {{ type: 'READONLY'|'IMPLEMENT'|'INVALID', dangerous: null|{name:string, alt:string} }}
 */
export function stepTypeClassification(step) {
  // Check for dangerous Windows Git Bash patterns first
  for (const { pattern, name, alt } of DANGEROUS_PATTERNS) {
    if (pattern.test(step)) {
      return { type: 'INVALID', dangerous: { name, alt } };
    }
  }
  // Check for readonly commands
  if (READONLY_PREFIXES.some(p => p.test(step))) {
    return { type: 'READONLY', dangerous: null };
  }
  // Check for implementation patterns
  if (FILE_CREATION_PATTERNS.some(p => p.test(step))) {
    return { type: 'IMPLEMENT', dangerous: null };
  }
  return { type: 'IMPLEMENT', dangerous: null };
}

/**
 * Check if a step is a read-only command.
 * @param {string} step
 * @returns {boolean}
 */
export function isReadOnlyStep(step) {
  const trimmed = step.trim();
  return READONLY_PREFIXES.some(p => p.test(trimmed));
}

/**
 * Check if any step after the first contains file creation.
 * @param {string} approach
 * @returns {boolean}
 */
export function hasFileCreation(approach) {
  const allSteps = extractAllSteps(approach);
  for (let i = 1; i < allSteps.length; i++) {
    const stepText = allSteps[i].stepText;
    if (FILE_CREATION_PATTERNS.some(p => p.test(stepText))) return true;
  }
  return false;
}

// ── Core step extraction ─────────────────────────────────────────────────────

export const STEP_REGEX = /(?:^|\n)\s*(\d+)\.\s+(.+?)(?:\n\s*\d+\.|$)/s;

/**
 * Extract the first numbered step from an approach text.
 * @param {string} approach
 * @returns {{ stepNum: string, firstStep: string } | null}
 */
export function extractFirstStep(approach) {
  const match = approach.match(STEP_REGEX);
  if (!match) return null;
  return {
    stepNum: match[1],
    firstStep: match[2].trim(),
  };
}

/**
 * Extract all numbered steps from an approach text.
 * @param {string} approach
 * @returns {Array<{ stepNum: string, stepText: string }>}
 */
export function extractAllSteps(approach) {
  const steps = [];
  const regex = /(?:^|\n)\s*(\d+)\.\s+(.+?)(?=\n\s*\d+\.|$)/gs;
  let match;
  while ((match = regex.exec(approach)) !== null) {
    steps.push({ stepNum: match[1], stepText: match[2].trim() });
  }
  return steps;
}
