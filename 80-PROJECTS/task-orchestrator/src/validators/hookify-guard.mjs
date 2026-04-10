#!/usr/bin/env node
/**
 * hookify-guard.mjs
 * 在executor执行command前，检查hookify规则是否拦截
 */
import { readFileSync, existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const HOOKIFY_DIR = join(__DIR, '..', '..', '..', '..', '.claude');

/** Load all enabled hookify rules that apply to bash events */
function loadRules() {
  const rules = [];
  if (!existsSync(HOOKIFY_DIR)) return rules;
  let files;
  try {
    files = readdirSync(HOOKIFY_DIR).filter(f => f.startsWith('hookify.') && f.endsWith('.local.md'));
  } catch {
    return rules;
  }
  for (const file of files) {
    try {
      const content = readFileSync(join(HOOKIFY_DIR, file), 'utf-8');
      const rule = parseFrontmatter(content);
      // Skip trivially broad patterns that match any command
      if (rule.enabled !== false && (rule.event === 'bash' || rule.event === 'all') && rule.pattern !== '.' && rule.pattern !== '.*') {
        rules.push({ name: rule.name, pattern: rule.pattern, message: extractMessage(content) });
      }
    } catch {
      // skip invalid rule files
    }
  }
  return rules;
}

function parseFrontmatter(content) {
  const fm = {};
  const match = content.match(/^---\n([\s\S]*?)\n---\n/);
  if (!match) return fm;
  for (const line of match[1].split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx === -1) continue;
    const key = line.slice(0, colonIdx).trim();
    const value = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, '');
    fm[key] = value;
  }
  return fm;
}

function extractMessage(content) {
  const parts = content.split(/^---\n[\s\S]*?\n---\n/);
  return parts.slice(1).join('\n').trim();
}

/** Check a command string against loaded rules. Returns { blocked, ruleName, message } */
export function checkCommand(command) {
  const rules = loadRules();
  for (const rule of rules) {
    try {
      const re = new RegExp(rule.pattern);
      if (re.test(command)) {
        return { blocked: true, ruleName: rule.name, message: rule.message };
      }
    } catch {
      // invalid regex, skip
    }
  }
  return { blocked: false };
}

class HookifyGuard {
  constructor() {
    this.rules = loadRules();
  }
  /** Synchronously check a command. Returns true if blocked. */
  check(command) {
    for (const rule of this.rules) {
      try {
        if (new RegExp(rule.pattern).test(command)) {
          return { blocked: true, ruleName: rule.name, message: rule.message };
        }
      } catch {
        // skip invalid regex
      }
    }
    return { blocked: false };
  }
}

export function createGuard() {
  return new HookifyGuard();
}

function demo() {
  const guard = new HookifyGuard();
  const tests = [
    'rm -rf /',
    'rm -rf /tmp/test',
    'mkdir /test',
    'git reset --hard HEAD~1',
    'chmod 777 file.txt',
  ];
  for (const cmd of tests) {
    const result = guard.check(cmd);
    if (result.blocked) {
      console.log(`BLOCKED: ${cmd} → ${result.ruleName}`);
    } else {
      console.log(`OK: ${cmd}`);
    }
  }
}

demo();
