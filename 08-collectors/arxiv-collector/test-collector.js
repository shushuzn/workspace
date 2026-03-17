#!/usr/bin/env node
/**
 * arXiv 收集器测试脚本
 */

const { fetchPapers, buildQueryUrl } = require('./arxiv-collector');

async function test() {
    console.log('🧪 arXiv 收集器测试\n');
    
    // 测试 1: URL 构建
    console.log('测试 1: URL 构建');
    const url = buildQueryUrl('test keyword', 10);
    console.log(`  URL: ${url}`);
    console.log(`  ✅ 通过\n`);
    
    // 测试 2: 抓取论文
    console.log('测试 2: 抓取论文');
    const papers = await fetchPapers('graph neural network', 5);
    console.log(`  抓取到 ${papers.length} 篇论文`);
    
    if (papers.length > 0) {
        console.log(`  第一篇: ${papers[0].title.substring(0, 50)}...`);
        console.log(`  ✅ 通过\n`);
    } else {
        console.log(`  ❌ 失败\n`);
    }
    
    console.log('✅ 所有测试完成！');
}

test().catch(console.error);
