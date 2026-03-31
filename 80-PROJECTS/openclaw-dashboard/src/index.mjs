/**
 * Self-Evolving Workspace Optimizer
 * New Architecture - Core/Agent based orchestration
 *
 * Entry point for the self-optimization loop
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { Agent } from './core/agent.mjs';
import { MetaCognizer } from './core/meta-cognizer.mjs';
import { STM } from './memory/stm.mjs';
import { CONFIG } from './config/default.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORKSPACE = path.join(__dirname, '..');

async function main() {
  const args = process.argv.slice(2);

  // Initialize new architecture components
  const stm = new STM(path.join(WORKSPACE, '.omc', 'loop-history.json'));
  const metaCognizer = new MetaCognizer(WORKSPACE, stm);

  // Create Agent with all components wired up
  const agent = new Agent(WORKSPACE);
  agent.setMetaCognizer(metaCognizer);

  if (args.includes('--status')) {
    const status = agent.getStatus();

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

  if (args.includes('--analyze')) {
    // Just run meta-cognition analysis
    const gaps = await metaCognizer.analyze();
    console.log('\n╔══════════════════════════════════════╗');
    console.log('║     元认知分析报告                 ║');
    console.log('╠══════════════════════════════════════╣');

    if (gaps.length === 0) {
      console.log('║  未发现明显能力缺口               ║');
    } else {
      console.log(`║  发现 ${gaps.length} 个能力缺口:`);
      for (const gap of gaps.slice(0, 10)) {
        const name = gap.name.substring(0, 15);
        console.log(`║  • [${gap.priority.toUpperCase()}] ${name}`);
        console.log(`║    ${gap.metric}`);
      }
    }
    console.log('╚══════════════════════════════════════╝');

    const boundary = metaCognizer.getCapabilityBoundary();
    console.log('\n╔══════════════════════════════════════╗');
    console.log('║     能力边界                       ║');
    console.log('╠══════════════════════════════════════╣');
    console.log(`║  强项 (${boundary.strong.length}): ${boundary.strong.slice(0, 3).map(s => s.name.substring(0, 10)).join(', ') || '无'}`);
    console.log(`║  中等 (${boundary.moderate.length}): ${boundary.moderate.slice(0, 3).map(s => s.name.substring(0, 10)).join(', ') || '无'}`);
    console.log(`║  弱项 (${boundary.weak.length}): ${boundary.weak.slice(0, 3).map(s => s.name.substring(0, 10)).join(', ') || '无'}`);
    console.log('╚══════════════════════════════════════╝');
    return;
  }

  await agent.runIteration();
}

main().catch(console.error);
