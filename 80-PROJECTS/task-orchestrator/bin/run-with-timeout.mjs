#!/usr/bin/env node
/** Run task-orchestrator with timeout wrapper */
import { execSync } from 'child_process';

if (process.argv.includes('--help') || process.argv.includes('-h')) {
  console.log('Usage: node run-with-timeout.mjs <timeout_minutes> <command...>');
  console.log('  timeout_minutes  Timeout in minutes (default: 5)');
  console.log('  command         Command to run with timeout');
  process.exit(0);
}

const t = parseInt(process.argv[2] || 5);
const cmd = process.argv.slice(3);
try {
  execSync(cmd.join(' '), { stdio: 'inherit', timeout: t * 60000 });
} catch (e) {
  console.error(e.message);
  process.exit(1);
}
