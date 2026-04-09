#!/usr/bin/env node
/** Run task-orchestrator with timeout wrapper */
import { execSync } from 'child_process';

const t = parseInt(process.argv[2] || 5);
const cmd = process.argv.slice(3);
try {
  execSync(cmd.join(' '), { stdio: 'inherit', timeout: t * 60000 });
} catch (e) {
  console.error(e.message);
  process.exit(1);
}
