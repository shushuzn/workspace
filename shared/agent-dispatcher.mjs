#!/usr/bin/env node
/**
 * shared/agent-dispatcher.mjs
 * 读取agent-registry.json，根据任务描述匹配最佳agent模板
 * Usage: node shared/agent-dispatcher.mjs --task "设计multi-agent编排架构"
 */
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const REGISTRY_FILE = join(__DIR, 'agent-registry.json');

// 任务关键词 → agent name 映射
const KEYWORD_MAP = [
  { keywords: ['架构', '设计', 'architecture', 'design', '系统设计'], agent: 'architect', confidence: 0.9 },
  { keywords: ['代码审查', '审查代码', '代码review', 'review code', 'review', '审查'], agent: 'code-reviewer', confidence: 0.9 },
  { keywords: ['测试', 'test', 'testing', 'qa', '验证'], agent: 'qa-tester', confidence: 0.85 },
  { keywords: ['文档', 'docs', 'document', 'write docs'], agent: 'document-specialist', confidence: 0.8 },
  { keywords: ['安全', 'security', '安全审查', 'vulnerability'], agent: 'security-reviewer', confidence: 0.9 },
  { keywords: ['调试', 'debug', 'debugging', 'fix bug'], agent: 'debugger', confidence: 0.85 },
  { keywords: ['规划', 'plan', 'planning', 'roadmap'], agent: 'planner', confidence: 0.8 },
  { keywords: ['执行', 'implement', 'execute', '实现'], agent: 'executor', confidence: 0.7 },
  { keywords: ['分析', 'analyze', 'analysis', '研究'], agent: 'analyst', confidence: 0.8 },
  { keywords: ['写作', 'write', 'writing', '文档撰写'], agent: 'writer', confidence: 0.8 },
  { keywords: ['简化', 'simplify', 'refactor', '重构'], agent: 'code-simplifier', confidence: 0.85 },
  { keywords: ['tracer', 'trace', '追踪', '因果'], agent: 'tracer', confidence: 0.8 },
  { keywords: ['verifier', 'verify', '验证', '校验'], agent: 'verifier', confidence: 0.8 },
  { keywords: ['explore', 'explorer', '探索', '发现'], agent: 'explore', confidence: 0.7 },
  { keywords: ['scientist', '科学', 'research', '研究'], agent: 'scientist', confidence: 0.75 },
];

function wordTokenize(text) {
  return text.toLowerCase().match(/\b\w+\b/g) || [];
}

function cosineSimilarity(a, b) {
  const tokensA = wordTokenize(a);
  const tokensB = wordTokenize(b);
  const set = [...new Set([...tokensA, ...tokensB])];
  const vec = (arr) => set.map(w => arr.includes(w) ? 1 : 0);
  const vA = vec(tokensA);
  const vB = vec(tokensB);
  const dot = vA.reduce((s, v, i) => s + v * vB[i], 0);
  const normA = Math.sqrt(vA.reduce((s, v) => s + v * v, 0));
  const normB = Math.sqrt(vB.reduce((s, v) => s + v * v, 0));
  if (normA === 0 || normB === 0) return 0;
  return dot / (normA * normB);
}

function fuzzyMatch(task, agents) {
  const results = [];
  for (const agent of agents) {
    const desc = [agent.name, agent.description, ...(agent.keywords || [])].join(' ');
    const score = cosineSimilarity(task, desc);
    if (score > 0.1) {
      results.push({ agent: agent.name, score, description: agent.description || '' });
    }
  }
  return results.sort((a, b) => b.score - a.score);
}

function matchAgent(task) {
  const lower = task.toLowerCase();
  let best = null;
  for (const { keywords, agent, confidence } of KEYWORD_MAP) {
    if (keywords.some(k => lower.includes(k))) {
      if (!best || confidence > best.confidence) {
        best = { agent, confidence };
      }
    }
  }
  return best;
}

function main() {
  const args = process.argv.slice(2);
  const taskIdx = args.indexOf('--task');
  const jsonIdx = args.indexOf('--json');
  const helpIdx = args.indexOf('--help');
  const simIdx = args.indexOf('--similarity');

  if (helpIdx !== -1 || args.length === 0 || simIdx !== -1) {
    if (simIdx !== -1) {
      const simTask = args[simIdx + 1] || args.slice(simIdx + 1).join(' ');
      if (!existsSync(REGISTRY_FILE)) {
        console.error('[agent-dispatcher] registry not found');
        process.exit(1);
      }
      const registry = JSON.parse(readFileSync(REGISTRY_FILE, 'utf8'));
      const top = fuzzyMatch(simTask, registry.agents).slice(0, 5);
      if (top.length === 0) {
        console.log('[agent-dispatcher] No similar agents found');
      } else {
        console.log(`[agent-dispatcher] Top ${top.length} similar agents for: "${simTask}"`);
        for (const r of top) {
          console.log(`  ${r.agent} (score: ${r.score.toFixed(2)}) — ${r.description.slice(0, 60)}`);
        }
      }
      process.exit(0);
    }
    console.log(`Usage: node agent-dispatcher.mjs --task "任务描述" [--json]`);
    console.log(`  --task  任务描述`);
    console.log(`  --json  输出JSON格式`);
    console.log(`  --similarity "模糊描述"  模糊相似度匹配`);
    process.exit(0);
  }

  if (helpIdx !== -1 || args.length === 0) {
    console.log(`Usage: node agent-dispatcher.mjs --task "任务描述" [--json]`);
    console.log(`  --task  任务描述`);
    console.log(`  --json  输出JSON格式`);
    console.log(`Example: node agent-dispatcher.mjs --task "设计multi-agent编排架构"`);
    process.exit(0);
  }

  if (!existsSync(REGISTRY_FILE)) {
    console.error('[agent-dispatcher] registry not found, run scan-agent-templates.mjs first');
    process.exit(1);
  }

  const registry = JSON.parse(readFileSync(REGISTRY_FILE, 'utf-8'));
  const task = taskIdx !== -1 ? args[taskIdx + 1] : args.join(' ');
  const match = matchAgent(task);

  if (!match) {
    const result = { matched: null, suggestion: null, confidence: 0, availableAgents: registry.agents.length };
    if (jsonIdx !== -1) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      console.log(`[agent-dispatcher] No matching agent found (${registry.agents.length} agents available)`);
    }
    process.exit(0);
  }

  // 检查该agent是否在registry中
  const found = registry.agents.find(a => a.name === match.agent);
  if (!found) {
    const result = { matched: null, suggestion: null, confidence: match.confidence, note: `agent ${match.agent} not in registry` };
    console.log(jsonIdx !== -1 ? JSON.stringify(result) : `[agent-dispatcher] agent ${match.agent} found in keyword map but not in registry`);
    process.exit(0);
  }

  const result = {
    matched: match.agent,
    suggestion: `[spawn:${match.agent}]`,
    confidence: match.confidence,
    description: found.description || '',
    model: found.model,
    tools: found.tools || [],
  };

  if (jsonIdx !== -1) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    console.log(`[agent-dispatcher] matched: ${match.agent} (confidence: ${match.confidence})`);
    console.log(`  suggestion: [spawn:${match.agent}]`);
    if (found.description) console.log(`  description: ${found.description}`);
    console.log(`  model: ${found.model} | tools: ${(found.tools || []).join(', ')}`);
  }
}

main();
