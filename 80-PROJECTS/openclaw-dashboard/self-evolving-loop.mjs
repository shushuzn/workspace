/**
 * Entry point wrapper - redirects to modular architecture
 * Previous monolithic self-evolving-loop.mjs
 */
export * from './src/index.mjs';
import { Agent } from './src/core/agent.mjs';
import path from 'path';

const workspace = process.cwd();
const agent = new Agent(workspace);

agent.runIteration().then(record => {
  console.log('\n[完成] 迭代结果:', JSON.stringify(record, null, 2));
  process.exit(0);
}).catch(e => {
  console.error('[错误]', e);
  process.exit(1);
});
