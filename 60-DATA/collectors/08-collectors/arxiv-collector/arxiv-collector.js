#!/usr/bin/env node
/**
 * arXiv 论文自动收集器
 * 
 * 功能:
 * - 根据关键词订阅抓取 arXiv 论文
 * - 存储论文元数据到 JSON 文件
 * - 自动去重
 * - 支持批量抓取
 */

const fetch = require('node-fetch');
const fs = require('fs');
const path = require('path');

// 加载配置
const config = require('./config.json');

// arXiv API 基础 URL
const ARXIV_API = 'http://export.arxiv.org/api/query';

/**
 * 构建 arXiv API 查询 URL
 */
function buildQueryUrl(keyword, maxResults = 50) {
    const searchQuery = encodeURIComponent(`all:${keyword}`);
    const sortBy = config.sortBy || 'submittedDate';
    const sortOrder = config.sortOrder || 'descending';
    
    return `${ARXIV_API}?search_query=${searchQuery}&start=0&max_results=${maxResults}&sortBy=${sortBy}&sortOrder=${sortOrder}`;
}

/**
 * 解析 arXiv XML 响应
 */
function parseArxivResponse(xml) {
    const entries = [];
    const entryRegex = /<entry>([\s\S]*?)<\/entry>/g;
    let match;
    
    while ((match = entryRegex.exec(xml)) !== null) {
        const entry = match[1];
        
        // 提取字段
        const id = extractField(entry, 'id');
        const title = extractField(entry, 'title').replace(/\n/g, ' ').trim();
        const summary = extractField(entry, 'summary').replace(/\n/g, ' ').trim();
        const published = extractField(entry, 'published');
        const updated = extractField(entry, 'updated');
        
        // 提取作者
        const authors = [];
        const authorRegex = /<author>[\s\S]*?<name>([\s\S]*?)<\/name>[\s\S]*?<\/author>/g;
        let authorMatch;
        while ((authorMatch = authorRegex.exec(entry)) !== null) {
            authors.push(authorMatch[1].trim());
        }
        
        // 提取分类
        const categories = [];
        const categoryRegex = /<category term="([^"]*)"/g;
        let categoryMatch;
        while ((categoryMatch = categoryRegex.exec(entry)) !== null) {
            categories.push(categoryMatch[1]);
        }
        
        entries.push({
            id,
            title,
            summary,
            authors,
            categories,
            published,
            updated,
            collectedAt: new Date().toISOString()
        });
    }
    
    return entries;
}

/**
 * 提取 XML 字段
 */
function extractField(xml, fieldName) {
    const regex = new RegExp(`<${fieldName}>([\\s\\S]*?)<\\/${fieldName}>`);
    const match = xml.match(regex);
    return match ? match[1] : '';
}

/**
 * 抓取单个关键词的论文
 */
async function fetchPapers(keyword, maxResults = 50) {
    console.log(`📡 抓取关键词 "${keyword}"...`);
    
    try {
        const url = buildQueryUrl(keyword, maxResults);
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'OpenClaw-Arxiv-Collector/1.0'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const xml = await response.text();
        const papers = parseArxivResponse(xml);
        
        console.log(`  ✅ 获取 ${papers.length} 篇论文`);
        return papers;
    } catch (error) {
        console.error(`  ❌ 错误：${error.message}`);
        return [];
    }
}

/**
 * 保存论文到 JSON 文件
 */
function savePapers(papers, keyword) {
    const dataDir = config.dataDir || './data/papers';
    
    // 创建目录
    if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
    }
    
    // 生成文件名
    const safeKeyword = keyword.replace(/[^a-zA-Z0-9]/g, '_');
    const filename = path.join(dataDir, `${safeKeyword}.json`);
    
    // 读取已有论文（去重）
    let existingPapers = [];
    if (fs.existsSync(filename)) {
        const existing = JSON.parse(fs.readFileSync(filename, 'utf-8'));
        existingPapers = existing.papers || [];
    }
    
    // 去重：基于 arXiv ID
    const existingIds = new Set(existingPapers.map(p => p.id));
    const newPapers = papers.filter(p => !existingIds.has(p.id));
    
    // 合并
    const allPapers = [...newPapers, ...existingPapers];
    
    // 保存
    const data = {
        keyword,
        lastUpdated: new Date().toISOString(),
        totalPapers: allPapers.length,
        newPapers: newPapers.length,
        papers: allPapers
    };
    
    fs.writeFileSync(filename, JSON.stringify(data, null, 2), 'utf-8');
    
    console.log(`  💾 保存 ${newPapers.length} 篇新论文 (共 ${allPapers.length} 篇)`);
    
    return {
        total: allPapers.length,
        new: newPapers.length
    };
}

/**
 * 主函数
 */
async function main() {
    console.log('╔════════════════════════════════════════════════╗');
    console.log('║  arXiv 论文自动收集器 v1.0                     ║');
    console.log('╚════════════════════════════════════════════════╝');
    console.log('');
    
    const keywords = config.keywords || [];
    const maxResults = config.maxResults || 50;
    
    console.log(`📋 关键词数量：${keywords.length}`);
    console.log(`📊 每关键词最多：${maxResults} 篇`);
    console.log('');
    
    const results = [];
    
    for (let i = 0; i < keywords.length; i++) {
        const keyword = keywords[i];
        console.log(`[${i + 1}/${keywords.length}]`);
        
        const papers = await fetchPapers(keyword, maxResults);
        const stats = savePapers(papers, keyword);
        
        results.push({
            keyword,
            papers: papers.length,
            new: stats.new,
            total: stats.total
        });
        
        // 延迟避免 API 限制 (arXiv: 每 3 秒 1 次)
        if (i < keywords.length - 1) {
            console.log('  ⏱️  等待 3 秒...');
            await new Promise(resolve => setTimeout(resolve, 3000));
        }
    }
    
    // 输出总结
    console.log('');
    console.log('═══════════════════════════════════════════════');
    console.log('📊 抓取总结:');
    console.log('═══════════════════════════════════════════════');
    
    let totalPapers = 0;
    let totalNew = 0;
    
    results.forEach(r => {
        console.log(`  ${r.keyword.padEnd(40)} ${r.new.toString().padStart(3)} 新 / ${r.total.toString().padStart(3)} 总`);
        totalPapers += r.total;
        totalNew += r.new;
    });
    
    console.log('───────────────────────────────────────────────');
    console.log(`  总计：${totalNew} 新 / ${totalPapers} 总`);
    console.log('═══════════════════════════════════════════════');
    console.log('');
    console.log('✅ 完成！');
    
    return results;
}

// 运行
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { fetchPapers, parseArxivResponse, buildQueryUrl };
