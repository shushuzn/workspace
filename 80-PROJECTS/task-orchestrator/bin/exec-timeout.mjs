#!/usr/bin/env node
/**
 * exec-timeout.mjs — run a command with a timeout wrapper
 * Usage: node exec-timeout.mjs <timeout_minutes> <command...>
 */
import { execSync, spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __DIR = dirname(fileURLToPath(import.meta.url));

function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.log('Usage: node exec-timeout.mjs <timeout_minutes> <command...>');
    process.exit(0);
  }
  // Parse timeout value and --json flag
  let timeoutIdx = args.findIndex(a => !isNaN(parseInt(a)));
  const timeoutMin = parseInt(args[timeoutIdx], 10);
  const isJson = args.includes('--json');
  // Build command: skip timeout arg and --json
  const cmd = args.slice(timeoutIdx + 1).filter(a => a !== '--json');
  const timeoutMs = timeoutMin * 60 * 1000;

  try {
    const result = execSync(cmd.join(' '), {
      cwd: __DIR,
      stdio: 'inherit',
      timeout: timeoutMs,
    });
    process.exit(result || 0);
  } catch (e) {
    if (isJson) {
      console.log(JSON.stringify({type: 'timeout', timeoutMin, message: `Command timed out after ${timeoutMin} minute(s)`}));
    } else {
      console.error(`[TIMEOUT] Command timed out after ${timeoutMin} minute(s)`);
    }
    process.exit(e.status || 1);
  }
}

main();
