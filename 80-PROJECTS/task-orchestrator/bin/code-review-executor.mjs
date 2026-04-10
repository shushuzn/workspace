#!/usr/bin/env node
/**
 * code-review-executor.mjs
 * 用code-reviewer agent扫描executor.mjs
 */
import { readFileSync } from 'fs';

const TARGET = new URL('./../src/executor.mjs', import.meta.url).href;
const content = readFileSync(new URL('./../src/executor.mjs', import.meta.url), 'utf8');

const issues = [];

// 1. 未处理的Promise rejection
if (!content.includes('unhandledRejection')) issues.push({ severity: 'high', type: '未处理Promise rejection', line: content.match(/reject\(/)?.[0]?.line });
// 2. execSync without timeout
if (content.includes('execSync') && !content.includes('timeout')) issues.push({ severity: 'medium', type: 'execSync缺少timeout参数' });
// 3. Hardcoded path
if (content.match(/\bD:\[\w\]+/)) issues.push({ severity: 'low', type: '硬编码路径' });
// 4. Error swallowed
if (content.match(/catch.*\{\s*\}/s)) issues.push({ severity: 'high', type: '空catch块吞掉错误' });
// 5. Missing null check before usage
if (content.includes('options.') && !content.includes('options ??')) issues.push({ severity: 'medium', type: 'options使用前无空值检查' });

console.log('[code-review] executor.mjs 审查结果');
console.log('='.repeat(40));
console.log(`文件: executor.mjs (${content.split('\n').length}行)`);
console.log(`发现 ${issues.length} 个问题:\n`);
issues.forEach((issue, i) => {
  console.log(`${i+1}. [${issue.severity.toUpperCase()}] ${issue.type}`);
});
if (issues.length === 0) console.log('未发现明显问题');

process.exit(issues.filter(i => i.severity === 'high').length > 0 ? 1 : 0);
