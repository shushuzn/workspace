#!/usr/bin/env node
/**
 * Auto Brainstorm Loop - 每30分钟自动研究
 * 1. 搜索 GitHub/arxiv 找主题
 * 2. 用头脑风暴选出最优方案
 * 3. 必须与现有项目结合
 * 4. 跑通全流程
 */

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const https = require('https');

const CONFIG = {
  intervalMinutes: 30,
  projectsPath: 'D:\\OpenClaw\\workspace\\80-PROJECTS',
  logPath: 'D:\\OpenClaw\\workspace\\logs\\auto-brainstorm',
  researchTopics: ['AI Agent', 'LLM', 'RAG', 'MCP', 'autonomous agent', 'multi-agent'],
};

class AutoBrainstormLoop {
  constructor() {
    this.iteration = 0;
    this.running = true;
    this.ensureLogDir();
  }

  ensureLogDir() {
    if (!fs.existsSync(CONFIG.logPath)) {
      fs.mkdirSync(CONFIG.logPath, { recursive: true });
    }
  }

  log(msg, type = 'INFO') {
    const timestamp = new Date().toISOString();
    const logLine = `[${type}] ${msg}`;
    const logFile = path.join(CONFIG.logPath, `brainstorm-${new Date().toISOString().split('T')[0]}.log`);
    fs.appendFileSync(logFile, `[${timestamp}] ${logLine}\n`);
    console.log(logLine);
  }

  printSection(title) {
    console.log('\n' + '═'.repeat(60));
    console.log(`  ${title}`);
    console.log('═'.repeat(60));
  }

  async httpGet(url) {
    return new Promise((resolve, reject) => {
      const options = {
        headers: {
          'User-Agent': 'AutoBrainstorm/1.0',
          'Accept': 'application/json'
        }
      };
      https.get(url, options, res => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => resolve(data));
      }).on('error', reject);
    });
  }

  async fetchGitHubTrending() {
    this.log('获取 GitHub Trending...');
    try {
      // GitHub API 需要 token，失败时用缓存或返回空
      const apiUrl = 'https://api.github.com/search/repositories?q=stars:>1000+pushed:>' + this.getDateNDaysAgo(7) + '&sort=updated&per_page=10';
      const data = await this.httpGet(apiUrl);
      if (data.startsWith('{"message')) {
        // Rate limited - 返回空，不阻塞
        this.log('GitHub API 限速，跳过');
        return [];
      }
      const json = JSON.parse(data);
      const repos = (json.items || []).map(r => `${r.owner.login}/${r.name}`);
      this.log(`GitHub Hot: ${repos.slice(0,5).join(', ')}`);
      return repos;
    } catch (err) {
      this.log(`GitHub 获取失败: ${err.message}`, 'WARN');
      return [];
    }
  }

  getDateNDaysAgo(n) {
    const d = new Date();
    d.setDate(d.getDate() - n);
    return d.toISOString().split('T')[0];
  }

  async fetchHackerNews() {
    this.log('获取 HackerNews Top...');
    try {
      const topStories = await this.httpGet('https://hacker-news.firebaseio.com/v0/topstories.json');
      const ids = JSON.parse(topStories).slice(0, 10);
      const stories = await Promise.all(ids.map(id =>
        this.httpGet(`https://hacker-news.firebaseio.com/v0/item/${id}.json`)
      ));
      const parsed = stories.map(s => {
        try {
          const j = JSON.parse(s);
          return j ? j.title : '';
        } catch { return ''; }
      }).filter(Boolean);
      this.log(`HackerNews: ${parsed.slice(0,3).join(' | ')}`);
      return parsed;
    } catch (err) {
      this.log(`HN 获取失败: ${err.message}`, 'WARN');
      return [];
    }
  }

  async fetchArxivRecent() {
    this.log('获取 Arxiv 最新论文...');
    try {
      // 搜索 AI 相关最新论文
      const url = 'https://export.arxiv.org/api/query?search_query=cs.AI+OR+cs.LG&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending';
      const xml = await this.httpGet(url);
      const titles = xml.match(/<title>([^<]+)<\/title>/g) || [];
      return titles.slice(0, 10).map(t => t.replace(/<[^>]+>/g, '').trim()).filter(t => t && t !== 'arXiv');
    } catch (err) {
      this.log(`Arxiv 获取失败: ${err.message}`, 'WARN');
      return [];
    }
  }

  getExistingProjects() {
    try {
      return fs.readdirSync(CONFIG.projectsPath).filter(p => {
        const stat = fs.statSync(path.join(CONFIG.projectsPath, p));
        return stat.isDirectory() && !p.startsWith('.');
      });
    } catch {
      return [];
    }
  }

  analyzeAndSelect(research, projects) {
    this.log(`分析 ${research.flat().length} 个主题与 ${projects.length} 个项目...`);

    // 简单匹配逻辑 - 实际应该用 LLM
    const matches = [];
    const topics = research.flat();

    for (const project of projects) {
      let foundForProject = false;
      for (const topic of topics) {
        const pLower = project.toLowerCase();
        const tLower = topic.toLowerCase();
        let score = 0;

        // 关键词匹配
        if (pLower.includes('agent') && (tLower.includes('agent') || tLower.includes('llm'))) {
          score = 90;
        } else if (pLower.includes('multi') && (tLower.includes('multi') || tLower.includes('agent'))) {
          score = 85;
        } else if (pLower.includes('a2a') && (tLower.includes('agent') || tLower.includes('protocol'))) {
          score = 80;
        } else if (pLower.includes('orchestrator') && tLower.includes('orchestrat')) {
          score = 88;
        } else if ((pLower.includes('brain') || pLower.includes('mind')) && (tLower.includes('ai') || tLower.includes('model'))) {
          score = 75;
        }

        if (score > 0) {
          matches.push({ project, topic, score });
          if (!foundForProject) {
            this.log(`  ✓ ${project} 匹配到: "${topic.substring(0, 50)}..."`);
            foundForProject = true;
          }
        }
      }
    }

    // 按分数排序
    matches.sort((a, b) => b.score - a.score);

    this.log(`共找到 ${matches.length} 个匹配`);

    return matches.slice(0, 3); // Top 3
  }

  saveResults(gitHub, hn, arxiv, matches) {
    const timestamp = new Date().toISOString();
    const result = {
      timestamp,
      iteration: this.iteration,
      gitHubTrending: gitHub,
      hackerNews: hn,
      arxivRecent: arxiv,
      recommendations: matches,
    };

    const resultFile = path.join(CONFIG.logPath, `result-${Date.now()}.json`);
    fs.writeFileSync(resultFile, JSON.stringify(result, null, 2));

    // 生成报告
    const reportFile = path.join(CONFIG.logPath, `report-${new Date().toISOString().split('T')[0]}.md`);
    let report = `# 自动头脑风暴报告 - ${timestamp}\n\n`;
    report += `## 第 ${this.iteration} 轮研究\n\n`;
    report += `### GitHub 热点\n${gitHub.slice(0, 5).map(p => `- ${p}`).join('\n')}\n\n`;
    report += `### HackerNews\n${hn.slice(0, 5).map(p => `- ${p}`).join('\n')}\n\n`;
    report += `### Arxiv 最新\n${arxiv.slice(0, 5).map(p => `- ${p}`).join('\n')}\n\n`;
    report += `### 推荐项目结合\n`;
    if (matches.length > 0) {
      for (const m of matches) {
        report += `**${m.project}** + "${m.topic}" (匹配度: ${m.score}%)\n`;
      }
    } else {
      report += `未找到明确匹配\n`;
    }

    fs.appendFileSync(reportFile, report + '\n---\n\n');

    return resultFile;
  }

  async runCycle() {
    this.iteration++;
    this.printSection(`第 ${this.iteration} 轮研究`);

    this.printSection('1. GitHub 热点');
    const gitHub = await this.fetchGitHubTrending();

    this.printSection('2. HackerNews Top');
    const hn = await this.fetchHackerNews();

    this.printSection('3. Arxiv 最新论文');
    const arxiv = await this.fetchArxivRecent();

    this.printSection('4. 匹配分析');
    const projects = this.getExistingProjects();
    this.log(`扫描 ${projects.length} 个项目`);
    const matches = this.analyzeAndSelect([gitHub, hn, arxiv], projects);

    this.printSection('5. 推荐结果');
    if (matches.length > 0) {
      matches.forEach((m, i) => {
        console.log(`\n  [${i+1}] ${m.project}`);
        console.log(`      + "${m.topic}"`);
        console.log(`      匹配度: ${m.score}%`);
      });
    } else {
      this.log('无明确匹配');
    }

    // 保存并显示下次运行时间
    const nextRun = new Date(Date.now() + CONFIG.intervalMinutes * 60 * 1000);
    this.log(`\n下次研究: ${nextRun.toLocaleTimeString()}`);

    return matches;
  }

  async start() {
    this.log('自动头脑风暴循环启动');
    this.log(`间隔: ${CONFIG.intervalMinutes} 分钟`);
    this.log(`项目路径: ${CONFIG.projectsPath}`);

    // 立即执行第一次
    await this.runCycle();

    // 循环
    while (this.running) {
      await new Promise(r => setTimeout(r, CONFIG.intervalMinutes * 60 * 1000));
      if (this.running) {
        await this.runCycle();
      }
    }
  }

  stop() {
    this.log('收到停止信号');
    this.running = false;
  }
}

// 主程序
const loop = new AutoBrainstormLoop();

process.on('SIGINT', () => loop.stop());
process.on('SIGTERM', () => loop.stop());

loop.start().catch(err => {
  console.error('Fatal:', err);
  process.exit(1);
});
