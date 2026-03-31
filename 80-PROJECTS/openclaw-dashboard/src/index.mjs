/**
 * Self-Evolving Workspace Optimizer
 * Modular rewrite using epsilon-greedy algorithm
 *
 * Entry point for the self-optimization loop
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { LoopEngine } from './core/loop-engine.mjs';
import { CONFIG } from './config/default.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORKSPACE = path.join(__dirname, '..');

async function main() {
  const args = process.argv.slice(2);
  const engine = new LoopEngine(WORKSPACE);

  if (args.includes('--status')) {
    const status = engine.getStatus();

    console.log('\n╔══════════════════════════════════════╗');
    console.log('║     自我进化 Loop - 状态报告       ║');
    console.log('╠══════════════════════════════════════╣');
    console.log(`║  健康度: ${status.score}/100`);
    console.log(`║  探索率 (ε): ${(status.epsilon * 100).toFixed(0)}%`);
    console.log(`║  历史记录: ${status.records} 条`);
    console.log(`║  连续成功: ${status.streak.success} 次`);
    console.log(`║  连续失败: ${status.streak.fail} 次`);
    console.log('╠══════════════════════════════════════╣');
    console.log('║     TOP 5 最有效操作               ║');

    for (const r of status.topOperations) {
      const rate = ((r.success / r.total) * 100).toFixed(0);
      console.log(`║  • ${r.name}: ${rate}% (${r.success}/${r.total})`);
    }
    console.log('╚══════════════════════════════════════╝');
    return;
  }

  await engine.runIteration();
}

main().catch(console.error);
