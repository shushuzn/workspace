#!/usr/bin/env node
/**
 * Auto-Research Loop
 * 不间断研究科技热点，自动优化 OpenClaw 项目
 *
 * 运行方式: node auto-research-loop.js
 * 停止: Ctrl+C
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  intervalHours: 1,  // 每小时研究一次
  newsSources: [
    'https://www.36kr.com',
    'https://www.36kr.com/information/technology'
  ],
  projectPath: 'D:\\OpenClaw\\workspace\\80-PROJECTS',
  logPath: 'D:\\OpenClaw\\workspace\\logs\\auto-research',
  keywords: ['AI', 'Agent', 'Claude', 'GPT', '模型', 'OpenAI', 'Anthropic', '语音']
};

class AutoResearchLoop {
  constructor() {
    this.running = true;
    this.iteration = 0;
    this.ensureLogDir();
  }

  ensureLogDir() {
    if (!fs.existsSync(CONFIG.logPath)) {
      fs.mkdirSync(CONFIG.logPath, { recursive: true });
    }
  }

  log(msg, type = 'INFO') {
    const timestamp = new Date().toISOString();
    const logLine = `[${timestamp}] [${type}] ${msg}\n`;
    const logFile = path.join(CONFIG.logPath, `research-${new Date().toISOString().split('T')[0]}.log`);
    fs.appendFileSync(logFile, logLine);
    console.log(logLine.trim());
  }

  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async runAgentBrowser(cmd) {
    return new Promise((resolve, reject) => {
      const proc = spawn('agent-browser', cmd.split(' '), {
        stdio: ['pipe', 'pipe', 'pipe'],
        shell: true
      });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', d => stdout += d.toString());
      proc.stderr.on('data', d => stderr += d.toString());
      proc.on('close', code => resolve({ stdout, stderr, code }));
      proc.on('error', reject);

      // 30秒超时
      setTimeout(() => {
        proc.kill();
        resolve({ stdout, stderr, code: -1, timeout: true });
      }, 30000);
    });
  }

  async researchNews() {
    this.iteration++;
    this.log(`===== 开始第 ${this.iteration} 轮研究 =====`);

    try {
      // 打开科技新闻
      this.log('打开 36kr 科技频道...');
      await this.runAgentBrowser('open https://www.36kr.com/information/technology');
      await this.sleep(5000);

      // 获取快照
      const snapshot = await this.runAgentBrowser('snapshot -c -d 2');

      // 分析关键词
      const content = snapshot.stdout;
      const found = CONFIG.keywords.filter(k => content.includes(k));

      if (found.length > 0) {
        this.log(`发现热点: ${found.join(', ')}`);

        // 保存研究结果
        const resultFile = path.join(CONFIG.logPath, `inspiration-${Date.now()}.txt`);
        fs.writeFileSync(resultFile, `时间: ${new Date().toISOString()}\n热点: ${found.join(', ')}\n\n内容摘要:\n${content.substring(0, 5000)}`);

        this.log(`灵感已保存: ${resultFile}`);
      } else {
        this.log('未发现预设热点关键词');
      }

      this.log('===== 研究完成 =====\n');

    } catch (err) {
      this.log(`研究出错: ${err.message}`, 'ERROR');
    }
  }

  async start() {
    this.log('自动研究循环启动');
    this.log(`研究间隔: ${CONFIG.intervalHours} 小时`);
    this.log(`项目路径: ${CONFIG.projectPath}`);

    // 立即执行第一次
    await this.researchNews();

    // 循环执行
    while (this.running) {
      const msInterval = CONFIG.intervalHours * 60 * 60 * 1000;
      await this.sleep(msInterval);
      if (this.running) {
        await this.researchNews();
      }
    }
  }

  stop() {
    this.log('收到停止信号，正在关闭...');
    this.running = false;
  }
}

// 主程序
const loop = new AutoResearchLoop();

// 处理退出信号
process.on('SIGINT', () => loop.stop());
process.on('SIGTERM', () => loop.stop());

// 启动
loop.start().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
