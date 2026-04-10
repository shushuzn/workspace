#!/usr/bin/env node
/**
 * debate-adapter.mjs
 * 封装multi-agent-hub的辩论框架为task-orchestrator adapter
 * 调用: node debate-adapter.mjs --topic "AI是否应该取代人类工作" --rounds 3
 */
import { spawn } from 'child_process';
import { join } from 'path';

const HUB_PATH = join('80-PROJECTS', 'multi-agent-hub', 'index.js');

export async function runDebate(topic, rounds = 3) {
  return new Promise((resolve, reject) => {
    const proc = spawn('node', [HUB_PATH, '--topic', topic, '--rounds', String(rounds), '--silent'], {
      cwd: 'D:/OpenClaw/workspace',
      stdio: ['pipe', 'pipe', 'pipe']
    });
    let stdout = '';
    let stderr = '';
    proc.stdout.on('data', d => stdout += d.toString());
    proc.stderr.on('data', d => stderr += d.toString());
    proc.on('close', code => {
      if (code === 0) resolve({ success: true, output: stdout });
      else reject(new Error(`debate failed: ${stderr || 'exit ' + code}`));
    });
    proc.on('error', reject);
  });
}

async function main() {
  const args = process.argv.slice(2);
  const topicIdx = args.indexOf('--topic');
  const topic = topicIdx >= 0 ? args[topicIdx + 1] : 'AI是否能自主进化';
  const roundsIdx = args.indexOf('--rounds');
  const rounds = roundsIdx >= 0 ? parseInt(args[roundsIdx + 1]) : 3;

  try {
    const result = await runDebate(topic, rounds);
    console.log('[debate-adapter] debate completed');
    console.log(result.output.slice(0, 500));
  } catch (e) {
    console.error('[debate-adapter] ERROR:', e.message);
    process.exit(1);
  }
}

main();
