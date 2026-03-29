/**
 * Agent Islands - 多Agent协作平台
 * 
 * 基于MCP协议的多Agent系统编排框架
 * 核心特性：
 * - 统一的Agent注册与发现机制
 * - 智能任务路由与负载均衡
 * - 跨Agent协作工作流
 * - 实时监控与可视化
 * - 错误恢复与重试机制
 */

export { AgentHub, agentHub } from './mcp-sdk/agent-hub.js';
export { NewsHubAdapter, newsHubAdapter } from './adapters/newshub-adapter.js';
export { WorkflowOrchestrator, workflowOrchestrator } from './workflows/orchestrator.js';
export type { AgentConfig, Task, TaskResult, AgentMetrics, TaskPriority, TaskStatus } from './mcp-sdk/agent-hub.js';
export type { NewsQuery, NewsItem, SentimentResult, TrendResult } from './adapters/newshub-adapter.js';
export type { Workflow, WorkflowStep, WorkflowResult } from './workflows/orchestrator.js';

// 示例用法
import { agentHub, workflowOrchestrator } from './index.js';

async function main() {
  console.log(`
🏝️ ═══════════════════════════════════════════════════════════
   Agent Islands - 多Agent协作平台 v1.0.0
   基于 MCP 协议的多Agent系统编排框架
═══════════════════════════════════════════════════════════
  `);

  // 1. 列出所有Agent
  console.log('📋 可用Agent:');
  const agents = agentHub.getAgents();
  agents.forEach(agent => {
    console.log(`  • ${agent.name} (${agent.id}) - ${agent.description}`);
  });
  console.log();

  // 2. 列出所有工作流
  console.log('📋 可用工作流:');
  const workflows = workflowOrchestrator.getWorkflows();
  workflows.forEach(wf => {
    console.log(`  • ${wf.name} - ${wf.description}`);
    console.log(`    步骤: ${wf.steps.map(s => s.agentId).join(' → ')}`);
  });
  console.log();

  // 3. 演示任务执行
  console.log('🚀 演示任务执行...');
  
  const task = {
    id: 'demo_task_1',
    type: 'research',
    targetAgents: ['ai-chat', 'newshub'],
    payload: {
      query: 'AI市场趋势',
      scope: ['news', 'analysis']
    },
    priority: 'medium' as const
  };

  await agentHub.dispatchTask(task);
  console.log('✅ 任务已提交');
  console.log();

  // 4. 获取统计信息
  console.log('📊 系统统计:');
  const stats = agentHub.getStats();
  console.log(`  • Agent数量: ${stats.totalAgents}`);
  console.log(`  • 活跃Agent: ${stats.activeAgents}`);
  console.log(`  • 任务总数: ${stats.totalTasks}`);
  console.log(`  • 成功率: ${stats.successRate.toFixed(1)}%`);
  console.log(`  • 平均延迟: ${stats.avgLatency.toFixed(0)}ms`);
  console.log();

  console.log(`
🏝️ ═══════════════════════════════════════════════════════════
   初始化完成！查看 dashboard/index.html 了解可视化界面
═══════════════════════════════════════════════════════════
  `);
}

// 运行演示
main().catch(console.error);

// 导出主类供外部使用
export default {
  AgentHub,
  NewsHubAdapter,
  WorkflowOrchestrator
};
