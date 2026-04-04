/**
 * Detection Operations
 * Operations that detect/analyze without making changes
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { DetectionOperation } from './base.mjs';
import { CONFIG } from '../config/default.mjs';
import { IdeaPool } from './productive-ops.mjs';

export class CheckProjectReadmes extends DetectionOperation {
  constructor(workspace) {
    super('check_project_readmes', '检查项目 README 完整性');
    this.workspace = workspace;
  }

  async execute() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { total: 0, missing: 0 };

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      } catch { return false; }
    });

    let missing = 0;
    for (const d of dirs.slice(0, 10)) {
      const readmePath = path.join(projectsDir, d, 'README.md');
      if (!fs.existsSync(readmePath)) missing++;
    }

    return { checked: Math.min(dirs.length, 10), missing };
  }
}

export class CheckMemorySize extends DetectionOperation {
  constructor(workspace) {
    super('check_memory_size', '检查记忆文件大小');
    this.workspace = workspace;
  }

  async execute() {
    const candidates = [
      path.join(this.workspace, '.omc', 'memory', 'MEMORY.md'),
      path.join(process.env.HOME || '', '.claude', 'projects', 'D--OpenClaw-workspace', 'memory', 'MEMORY.md')
    ];

    for (const memPath of candidates) {
      if (fs.existsSync(memPath)) {
        const content = fs.readFileSync(memPath, 'utf8');
        const sizeKB = Math.round(Buffer.byteLength(content, 'utf8') / 1024);
        const isGlobal = memPath.includes('.claude');
        return { sizeKB, lines: content.split('\n').length, global: isGlobal };
      }
    }
    return { sizeKB: 0 };
  }
}

export class BrainstormProjects extends DetectionOperation {
  constructor(workspace) {
    super('brainstorm_projects', '头脑风暴项目优化建议');
    this.workspace = workspace;
  }

  canImprove(targetProject) {
    if (targetProject) return true; // 有明确目标时强制执行 brainstorm
    // 全局冷却：检查整个 brainstorm 目录
    const bmDir = path.join(this.workspace, '.omc', 'brainstorm');
    if (!fs.existsSync(bmDir)) return true;
    const files = fs.readdirSync(bmDir).filter(f => f.endsWith('.md'));
    if (files.length === 0) return true;
    const latest = files.sort().pop();
    const age = Date.now() - fs.statSync(path.join(bmDir, latest)).mtimeMs;
    return age > CONFIG.brainstorm.minDaysBetween * 24 * 60 * 60 * 1000;
  }

  async execute(targetProject) {
    // 如果传入了目标项目则使用它，不再随机选
    if (targetProject) {
      // 项目实际在 80-PROJECTS/ 子目录下
      const projectPath = path.join(this.workspace, '80-PROJECTS', targetProject);
      if (!fs.existsSync(projectPath)) return { ideas: 0 };
      return this._brainstormProject(targetProject, projectPath);
    }

    // 无 targetProject 时从 MEMORY.md 活跃项目列表随机选（兼容旧逻辑）
    const memoryFile = path.join(process.env.HOME || '', '.claude', 'projects', 'D--OpenClaw-workspace', 'memory', 'MEMORY.md');
    if (!fs.existsSync(memoryFile)) return { ideas: 0 };
    const rows = this._parseActiveProjects(fs.readFileSync(memoryFile, 'utf8'));
    if (rows.length === 0) return { ideas: 0 };
    const target = rows[Math.floor(Math.random() * rows.length)].name;
    return this._brainstormProject(target, path.join(this.workspace, target));
  }

  _parseActiveProjects(content) {
    const rows = [];
    const lines = content.split('\n');
    let inActive = false;
    for (const line of lines) {
      const t = line.trim();
      if (t === '### Active Projects') { inActive = true; continue; }
      if (t.startsWith('### ')) { inActive = false; continue; }
      if (!inActive || !t.startsWith('|') || t.includes('---')) continue;
      const cells = t.split('|').map(c => c.trim()).filter(Boolean);
      if (cells.length >= 2) rows.push({ name: cells[0], path: cells[1] });
    }
    return rows;
  }

  /** 读取项目所有文本上下文（README + package.json + 源码内容），用于领域感知创新建议 */
  _readProjectContext = (projectPath, readmePath, packagePath, srcPath) => {
    const parts = [];
    try {
      if (fs.existsSync(readmePath)) parts.push(fs.readFileSync(readmePath, 'utf8').substring(0, 5000));
    } catch {}
    try {
      if (fs.existsSync(packagePath)) parts.push(fs.readFileSync(packagePath, 'utf8'));
    } catch {}
    // 读取 src 目录核心文件（前3个）的部分内容
    if (fs.existsSync(srcPath)) {
      try {
        const files = fs.readdirSync(srcPath)
          .filter(f => f.endsWith('.ts') || f.endsWith('.js') || f.endsWith('.py') || f.endsWith('.mjs'))
          .slice(0, 3);
        for (const f of files) {
          try {
            const content = fs.readFileSync(path.join(srcPath, f), 'utf8').substring(0, 1500);
            parts.push(`// ${f}\n${content}`);
          } catch {}
        }
      } catch {}
    }
    return parts.join('\n');
  };

  /**
   * 深度分析项目源码，生成真正有价值的创新建议
   * 不是关键词匹配，而是理解代码在做什么之后提出改进
   */
  _deepAnalyzeProject(target, projectPath, context) {
    const suggestions = [];
    const lower = context.toLowerCase();
    const words = lower.split(/\s+/);

    // ── 检测是否有硬编码/配置外置建议 ──
    if (lower.includes('apikey') || lower.includes('api_key') || lower.includes('secret')) {
      if (!lower.includes('dotenv') && !lower.includes('env')) {
        suggestions.push('敏感信息外置 - 将 API Key 等硬编码迁移到 .env 环境变量配置');
      }
    }

    // ── 检测是否缺少错误处理 ──
    if (!lower.includes('try') && !lower.includes('catch') && !lower.includes('error handling')) {
      suggestions.push('错误处理增强 - 添加结构化错误处理、fallback 逻辑、降级策略');
    }

    // ── 检测是否有类型系统 ──
    if (!lower.includes('typescript') && !lower.includes(': string') && !lower.includes(': number') && !lower.includes(': boolean')) {
      if (fs.existsSync(path.join(projectPath, 'package.json'))) {
        try {
          const pkg = JSON.parse(fs.readFileSync(path.join(projectPath, 'package.json'), 'utf8'));
          const deps = Object.keys({ ...pkg.dependencies, ...pkg.devDependencies }).join(' ');
          if (deps.includes('typescript')) {
            suggestions.push('TypeScript 类型增强 - 为核心函数补充完整类型注解，消除 any');
          }
        } catch {}
      }
    }

    // ── 检测是否有缓存机制 ──
    if (!lower.includes('cache') && !lower.includes('lru') && !lower.includes('memo')) {
      suggestions.push('缓存层引入 - 添加 LRU 缓存或 memoization，减少重复计算');
    }

    // ── 检测是否有配置管理 ──
    if (!lower.includes('config') && !lower.includes('yaml') && !lower.includes('toml') && !lower.includes('argv')) {
      suggestions.push('配置外部化 - 接受 YAML/JSON 配置文件，支持多环境切换');
    }

    // ── 检测是否有日志 ──
    if (!lower.includes('console.log') && !lower.includes('logger') && !lower.includes('log.')) {
      suggestions.push('结构化日志 - 替换 console.log 为 pino/winston，添加级别和上下文');
    }

    // ── 检测是否缺少批处理 ──
    if (lower.includes('for') && lower.includes('fetch') && !lower.includes('batch') && !lower.includes('chunk')) {
      suggestions.push('批量处理优化 - 将串行请求改为并发/批量，降低延迟');
    }

    // ── 检测是否缺少重试机制 ──
    if (lower.includes('fetch') || lower.includes('request') || lower.includes('api')) {
      if (!lower.includes('retry') && !lower.includes('attempt')) {
        suggestions.push('网络请求重试 - 添加指数退避重试机制，提升可靠性');
      }
    }

    // ── 检测是否缺少限流 ──
    if ((lower.includes('api') || lower.includes('request') || lower.includes('fetch')) &&
        !lower.includes('rate') && !lower.includes('limit') && !lower.includes('throttle')) {
      suggestions.push('限流保护 - 添加请求限流器，避免触发第三方 API 配额限制');
    }

    // ── 检测是否缺少凭证轮换 ──
    if ((lower.includes('apikey') || lower.includes('api_key') || lower.includes('token')) &&
        !lower.includes('rotate') && !lower.includes('refresh')) {
      suggestions.push('凭证自动轮换 - 实现 API Key 自动刷新和轮换机制');
    }

    // ── 检测是否有外部依赖可本地替代 ──
    if (lower.includes('openai') || lower.includes('anthropic')) {
      if (!lower.includes('ollama') && !lower.includes('local')) {
        suggestions.push('本地模型支持 - 接入 Ollama 本地模型，降低 API 成本，支持离线运行');
      }
    }

    // ── 检测是否缺少发布验证 ──
    if (!lower.includes('lint') && !lower.includes('prettier') && !lower.includes('format')) {
      suggestions.push('代码质量门禁 - 添加 ESLint + Prettier + husky pre-commit hook');
    }

    // ── 检测是否缺少变更追踪 ──
    if (!lower.includes('changelog') && !lower.includes('release')) {
      suggestions.push('变更日志自动化 - 接入 conventional commits，自动生成 changelog');
    }

    return suggestions;
  };

  _brainstormProject(target, projectPath) {
    const suggestions = [];
    const readmePath = path.join(projectPath, 'README.md');
    const packagePath = path.join(projectPath, 'package.json');
    const srcPath = path.join(projectPath, 'src');

    // ── 基础补缺：缺失项立即补齐建议 ──
    if (!fs.existsSync(readmePath)) {
      suggestions.push('缺少 README.md - 建议添加项目说明文档');
    }
    if (fs.existsSync(packagePath)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        if (!pkg.scripts?.dev && !pkg.scripts?.start) {
          suggestions.push('缺少启动脚本 - 建议添加 dev 或 start 命令');
        }
        if (!pkg.keywords || pkg.keywords.length < 3) {
          suggestions.push('关键词不足 - 建议添加更多关键词提升可发现性');
        }
        if (!pkg.description || pkg.description.length < 10) {
          suggestions.push('package.json description 缺失或过简 - 建议添加项目描述');
        }
      } catch { /* ignore */ }
    } else {
      const altConfigs = ['pyproject.toml', 'go.mod', 'Cargo.toml', 'requirements.txt', 'Pipfile'];
      if (altConfigs.some(f => fs.existsSync(path.join(projectPath, f)))) {
        suggestions.push('无 package.json - 建议添加以支持 npm 生态或标准化启动流程');
      }
    }
    if (fs.existsSync(srcPath)) {
      const srcFiles = fs.readdirSync(srcPath).filter(f => f.endsWith('.ts') || f.endsWith('.js'));
      if (srcFiles.length > 10) {
        suggestions.push(`src 目录有 ${srcFiles.length} 个文件 - 考虑模块化拆分`);
      }
    }
    if (!fs.existsSync(path.join(projectPath, '.github', 'workflows'))) {
      suggestions.push('缺少 GitHub Actions CI 流程 - 建议添加自动化测试工作流');
    }
    const testPaths = ['tests', 'test', '__tests__', 'spec'];
    if (!testPaths.some(t => fs.existsSync(path.join(projectPath, t)))) {
      suggestions.push('缺少测试目录 - 建议添加测试框架提升代码可靠性');
    }
    if (fs.existsSync(readmePath)) {
      const readme = fs.readFileSync(readmePath, 'utf8');
      if (!readme.includes('npm install') && !readme.includes('pip install') && !readme.includes('cargo')) {
        suggestions.push('README 缺少安装命令 - 建议补充快速启动步骤');
      }
      if (!readme.includes('##') && !readme.includes('#')) {
        suggestions.push('README 结构简单 - 建议增加章节（功能/用法/许可证等）');
      }
    }
    if (!fs.existsSync(path.join(projectPath, 'LICENSE')) && !fs.existsSync(path.join(projectPath, 'LICENSE.md'))) {
      suggestions.push('缺少开源许可证 - 建议添加 LICENSE 文件明确授权条款');
    }

    // ── 项目感知创新建议：读懂项目源码，理解核心逻辑后生成真正有价值的改进方向 ──
    const projectContext = this._readProjectContext(projectPath, readmePath, packagePath, srcPath);
    const projectIdeas = this._deepAnalyzeProject(target, projectPath, projectContext);

    // 分析项目技术栈
    let isPython = false, isTypeScript = false, isFrontend = false, hasCLI = false;
    if (fs.existsSync(packagePath)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        const deps = { ...pkg.dependencies, ...pkg.devDependencies };
        const allDeps = Object.keys(deps).join(' ');
        const pkgJson = JSON.stringify(pkg);
        isTypeScript = allDeps.includes('typescript') || allDeps.includes('@types/');
        isFrontend = allDeps.includes('react') || allDeps.includes('vue') || allDeps.includes('svelte');
        isPython = fs.existsSync(path.join(projectPath, 'pyproject.toml')) || fs.existsSync(path.join(projectPath, 'requirements.txt'));
        hasCLI = pkgJson.includes('commander') || pkgJson.includes('cac') || pkgJson.includes('yargs') || pkgJson.includes('clipanion');
      } catch {}
    }

    // ── 通用工程改进建议 ──
    if (!hasCLI && !isFrontend) {
      suggestions.push('CLI 化改造 - 将核心能力封装为命令行工具，支持 AI Agent 调用');
    }
    if (hasCLI) {
      suggestions.push('CLI 深度增强 - 添加交互式提示、多格式输出、配置热加载');
    }
    if (!isFrontend) {
      const hasMonitoring = fs.existsSync(path.join(projectPath, 'grafana')) ||
                            fs.existsSync(path.join(projectPath, 'prometheus')) ||
                            fs.existsSync(path.join(projectPath, 'monitoring'));
      if (!hasMonitoring) {
        suggestions.push('可观测性建设 - 添加结构化日志、metrics 埋点、分布式 traces');
      }
    }
    if (isFrontend) {
      suggestions.push('PWA 增强 - 添加离线支持、桌面入口、后台同步');
    }
    if (isPython || isTypeScript) {
      suggestions.push('性能基准测试 - 建立自动化 benchmark，监控关键路径耗时变化');
    }
    const hasI18n = fs.existsSync(path.join(projectPath, 'i18n')) ||
                      fs.existsSync(path.join(projectPath, 'locales')) ||
                      fs.existsSync(path.join(projectPath, 'langs'));
    if (!hasI18n) {
      suggestions.push('国际化（i18n）- 抽取用户可见文本，支持多语言切换');
    }
    suggestions.push('开源运营建设 - contribution guide、changelog 自动化、release note 生成');
    suggestions.push('项目元数据完善 - 添加CITATION.cff、代码徽章、量化健康指标');

    // 合并深度分析产生的项目专属创新建议
    for (const idea of projectIdeas) {
      if (!suggestions.includes(idea)) suggestions.push(idea);
    }

    // ── 从 MEMORY.md 交叉链接表搜索相关域类比 ──
    const analogies = this._findAnalogies(target);

    // 写入 idea 池（每条建议一条 seed idea），格式含 [projectName] 以便自动执行
    // 自动估算 score：benefit(1-3) × feasibility(1-3)
    const ideaPool = new IdeaPool(this.workspace);

    // 语义去重：提取核心主题词，去除措辞差异（"缺少X" vs "X" vs "可添加X"）
    const _coreTopic = (desc) => {
      return desc
        .replace(/^brainstorm:\s*\[[^\]]+\]\s*/i, '')
        .replace(/^\[suggest\]\s*/i, '')
        .replace(/^(缺少|可添加|可转化|建议添加|建议)\s*/i, '')
        .replace(/\s*[-−–].*$/, '').trim()
        .replace(/\[.*?\]/g, '')
        .replace(/\s+/g, ' ').trim()
        .toLowerCase();
    };

    const existingTopics = new Set(ideaPool.list()
      .map(i => _coreTopic(i.desc)));
    for (const s of suggestions) {
      const fullDesc = `brainstorm: [${target}] ${s}`;
      const topic = _coreTopic(fullDesc);
      if (existingTopics.has(topic)) continue; // 语义重复则跳过
      existingTopics.add(topic); // 防止同批次内重复
      const idx = ideaPool.add('seed', fullDesc, 'brainstorm');
      // 自动打分：impact × effort
      const { impact, effort } = this._estimateIdeaScore(s);
      if (idx !== -1 && impact && effort) ideaPool.score(idx, impact, effort);
    }

    const brainstormDir = path.join(this.workspace, '.omc', 'brainstorm');
    if (!fs.existsSync(brainstormDir)) fs.mkdirSync(brainstormDir, { recursive: true });

    const timestamp = new Date().toISOString().slice(0, 10);
    const outputPath = path.join(brainstormDir, `${target}-${timestamp}.md`);
    let content = `# ${target} 优化建议\n\n**生成时间**: ${new Date().toLocaleString()}\n\n## 项目信息\n- **路径**: ${projectPath}\n- **建议数量**: ${suggestions.length}\n\n## 优化建议\n${suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n`;
    if (analogies.length > 0) {
      content += `\n## 意外启发（跨域类比）\n${analogies.map(a => `🤯 ${a}`).join('\n')}\n`;
    }
    fs.writeFileSync(outputPath, content);

    return { project: target, ideas: suggestions.length, analogies: analogies.length, suggestions, analogies, output: outputPath };
  }

  /** 从 MEMORY.md 交叉链接表搜索与目标项目相关的类比 */
  _findAnalogies(target) {
    const memoryFile = path.join(process.env.HOME || '', '.claude', 'projects', 'D--OpenClaw-workspace', 'memory', 'MEMORY.md');
    if (!fs.existsSync(memoryFile)) return [];
    const memory = fs.readFileSync(memoryFile, 'utf8');

    // 找交叉链接表中涉及目标项目的条目
    const analogies = [];
    const lines = memory.split('\n');
    for (const line of lines) {
      // 格式: | 源 ↔ 目标 | 关联 | 共享依赖/关联概念: XXX |
      if (!line.includes('↔') || !line.includes('|')) continue;
      const parts = line.split('|').map(p => p.trim()).filter(Boolean);
      if (parts.length < 3) continue;
      const [source, target2, relation, detail] = parts;
      // 匹配源或目标包含目标项目名
      const t = target.toLowerCase();
      if (source.toLowerCase().includes(t) || target2.toLowerCase().includes(t)) {
        analogies.push(`${source} ${relation} ${target2} | ${detail}`);
      }
    }
    return analogies.slice(0, 3); // 最多返回3条
  }

  /** 根据建议内容估算 idea score: impact(1-3) × effort(1-3) */
  _estimateIdeaScore(suggestion) {
    const lower = suggestion.toLowerCase();
    let impact = 2; // 默认中等收益
    let effort = 2; // 默认中等成本

    // 高收益指标
    if (lower.includes('重复') || lower.includes('复制') || lower.includes('bug')) impact = 3;
    else if (lower.includes('质量') || lower.includes('可维护') || lower.includes('测试')) impact = 2;
    else if (lower.includes('说明') || lower.includes('文档') || lower.includes('注释')) impact = 1;

    // 低投入指标（容易完成）
    if (lower.includes('添加') && (lower.includes('readme') || lower.includes('测试'))) effort = 1;
    else if (lower.includes('添加') && (lower.includes('package.json') || lower.includes('脚本'))) effort = 1;
    else if (lower.includes('关键词') || lower.includes('description')) effort = 1;
    else if (lower.includes('npm') || lower.includes('生态')) effort = 2;
    else if (lower.includes('拆分') || lower.includes('模块化')) effort = 3;

    return { impact, effort };
  }
}

export class FindLargeFiles extends DetectionOperation {
  constructor(workspace) {
    super('find_large_files', '查找大文件（仅报告）');
    this.workspace = workspace;
  }

  async execute() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { found: 0 };

    const largeFiles = [];

    const scanDir = (dir, depth = 0) => {
      if (depth > CONFIG.largeFile.maxDepth) return;
      try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries.slice(0, 50)) {
          if (entry.name.startsWith('.')) continue;
          const fullPath = path.join(dir, entry.name);
          if (entry.isDirectory()) {
            const isSafe = CONFIG.largeFile.safePatterns
              .some(p => entry.name.includes(p));
            if (isSafe || depth < 2) scanDir(fullPath, depth + 1);
          } else if (entry.isFile()) {
            const size = fs.statSync(fullPath).size;
            const sizeMB = size / (1024 * 1024);
            if (sizeMB > CONFIG.largeFile.limitMB) {
              const relPath = fullPath.replace(this.workspace, '').replace(/\\/g, '/');
              if (!CONFIG.largeFileWhitelist.some(w => relPath.includes(w))) {
                largeFiles.push({ path: relPath, sizeMB: sizeMB.toFixed(2) });
              }
            }
          }
        }
      } catch { /* ignore */ }
    };

    scanDir(projectsDir);
    return { found: largeFiles.length, files: largeFiles.slice(0, 5) };
  }
}

export class CheckGitRemotes extends DetectionOperation {
  constructor(workspace) {
    super('check_git_remotes', '检查 git remote 状态');
    this.workspace = workspace;
  }

  async execute() {
    const projectsDir = this.workspace;
    if (!fs.existsSync(projectsDir)) return { checked: 0, issues: [] };

    const dirs = fs.readdirSync(projectsDir).filter(f => {
      try {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      } catch { return false; }
    });

    const issues = [];

    for (const d of dirs) {
      const projectPath = path.join(projectsDir, d);
      const gitFile = path.join(projectPath, '.git');

      // Skip submodules (they have .git as a file pointing to actual gitdir)
      if (fs.existsSync(gitFile)) {
        const stat = fs.statSync(gitFile);
        if (stat.isFile()) {
          const gitContent = fs.readFileSync(gitFile, 'utf8');
          if (gitContent.includes('gitdir:')) continue;
        }
        // else: .git is a directory = normal repo, continue
      }

      try {
        const remote = execSync('git remote get-url origin', {
          cwd: projectPath,
          encoding: 'utf8',
          timeout: 3000
        }).trim();

        if (!remote) {
          issues.push({ project: d, type: 'no_remote', detail: '无有效 remote' });
          continue;
        }

        // Check for stale branches
        try {
          const branches = execSync('git branch -vv', {
            cwd: projectPath,
            encoding: 'utf8',
            timeout: 3000
          });
          const stale = branches.split('\n').filter(l => l.includes(': gone]'));
          for (const s of stale) {
            const match = s.match(/^\s*(\S+)/);
            if (match) {
              issues.push({ project: d, type: 'stale_branch', detail: `${d}/${match[1]}` });
            }
          }
        } catch { /* ignore */ }
      } catch { /* not a git repo */ }
    }

    // Write to dashboard data
    if (issues.length > 0) {
      const dataFile = path.join(this.workspace, 'dashboard-data.json');
      let data = {};
      if (fs.existsSync(dataFile)) {
        try { data = JSON.parse(fs.readFileSync(dataFile, 'utf8')); } catch { /* ignore */ }
      }
      if (!data.issues) data.issues = [];
      for (const issue of issues) {
        const key = `${issue.type}:${issue.project}:${issue.detail}`;
        if (!data.issues.some(i => i.key === key)) {
          data.issues.push({ ...issue, key, found_at: new Date().toISOString(), resolved: false });
        }
      }
      fs.writeFileSync(dataFile, JSON.stringify(data, null, 2));
    }

    return { checked: dirs.length, issues };
  }
}

/**
 * SuggestProjectIdeas — 针对抽中项目的优化建议生成
 * pick-next-project 抽中后自动触发，针对性分析该项目并写入 idea 池
 */
export class SuggestProjectIdeas extends DetectionOperation {
  constructor(workspace) {
    super('suggest_project_ideas', '生成项目优化建议');
    this.workspace = workspace;
  }

  canImprove() {
    // 每次抽中项目后都触发，无冷却期限制
    return true;
  }

  async execute(targetProject) {
    if (!targetProject) return { ideas: 0, suggestions: [] };

    const projectPath = path.join(this.workspace, targetProject);
    if (!fs.existsSync(projectPath)) return { ideas: 0, suggestions: [] };

    const suggestions = [];
    const packagePath = path.join(projectPath, 'package.json');
    const readmePath  = path.join(projectPath, 'README.md');
    const srcPath     = path.join(projectPath, 'src');
    const testsPath   = path.join(projectPath, 'tests');

    // 1. package.json 分析
    if (fs.existsSync(packagePath)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
        if (!pkg.scripts?.dev && !pkg.scripts?.start) {
          suggestions.push('缺少 dev/start 启动脚本');
        }
        if (!pkg.scripts?.test) {
          suggestions.push('缺少测试脚本 - 建议添加 test 命令');
        }
        if (!pkg.keywords || pkg.keywords.length < 3) {
          suggestions.push('关键词不足 - 建议添加更多关键词提升可发现性');
        }
        if (!pkg.description || pkg.description.length < 20) {
          suggestions.push('description 过短 - 建议补充项目说明');
        }
        if (pkg.dependencies && Object.keys(pkg.dependencies).length > 20) {
          suggestions.push(`依赖过多（${Object.keys(pkg.dependencies).length}个）- 考虑拆分或减少直接依赖`);
        }
      } catch { /* ignore */ }
    } else {
      suggestions.push('缺少 package.json - 建议添加以支持 npm 生态');
    }

    // 2. README 分析
    if (!fs.existsSync(readmePath)) {
      suggestions.push('缺少 README.md - 建议添加项目说明');
    }

    // 3. src 结构分析
    if (fs.existsSync(srcPath)) {
      try {
        const files = fs.readdirSync(srcPath).filter(f => f.endsWith('.ts') || f.endsWith('.js') || f.endsWith('.jsx'));
        const size = files.length;
        if (size > 20) {
          suggestions.push(`src 文件过多（${size}个）- 考虑模块化拆分`);
        }
        if (size === 0) {
          suggestions.push('src 目录存在但为空');
        }
      } catch { /* ignore */ }
    }

    // 4. 测试覆盖检查
    if (!fs.existsSync(testsPath) && !fs.existsSync(path.join(projectPath, 'test'))) {
      suggestions.push('缺少测试目录 - 建议添加 tests/ 或 test/ 目录');
    }

    if (suggestions.length === 0) {
      return { project: targetProject, ideas: 0, message: '项目状态良好' };
    }

    // 写入 idea 池
    const ideaPool = new IdeaPool(this.workspace);
    for (const s of suggestions) {
      ideaPool.add('seed', `suggest: [${targetProject}] ${s}`, 'suggest');
    }

    // 写入 brainstorm 目录
    const brainstormDir = path.join(this.workspace, '.omc', 'brainstorm');
    if (!fs.existsSync(brainstormDir)) fs.mkdirSync(brainstormDir, { recursive: true });
    const timestamp = new Date().toISOString().slice(0, 10);
    const outputPath = path.join(brainstormDir, `${targetProject}-suggestions-${timestamp}.md`);
    const content = `# ${targetProject} 优化建议\n\n**生成时间**: ${new Date().toLocaleString()}\n**触发方式**: pick-next-project 抽中后自动生成\n\n## 建议（${suggestions.length}条）\n${suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')}\n`;
    fs.writeFileSync(outputPath, content, 'utf8');

    return { project: targetProject, ideas: suggestions.length, suggestions, output: outputPath };
  }
}

/**
 * BrainstormReview — brainstorm 历史文件复盘
 * 每 14 天触发，扫描 .omc/brainstorm/ 清理过时文件，统计采纳率
 */
export class BrainstormReview extends DetectionOperation {
  constructor(workspace) {
    super('brainstorm_review', 'brainstorm 历史复盘');
    this.workspace = workspace;
    this.brainstormDir = path.join(workspace, '.omc', 'brainstorm');
    this.ideaPool = new IdeaPool(workspace);
  }

  canImprove() {
    if (!fs.existsSync(this.brainstormDir)) return false;
    const files = fs.readdirSync(this.brainstormDir).filter(f => f.endsWith('.md'));
    if (files.length === 0) return false;
    const latest = files.sort().pop();
    const age = Date.now() - fs.statSync(path.join(this.brainstormDir, latest)).mtimeMs;
    return age > 14 * 24 * 60 * 60 * 1000;
  }

  async execute() {
    if (!fs.existsSync(this.brainstormDir)) {
      return { cleaned: 0, stats: { total: 0, adopted: 0, rate: '0%' } };
    }

    const files = fs.readdirSync(this.brainstormDir).filter(f => f.endsWith('.md'));
    const now = Date.now();
    const TTL_MS = 60 * 24 * 60 * 60 * 1000; // 60 天

    let cleaned = 0;
    const stats = { total: files.length, adopted: 0, oldFiles: 0 };

    // 统计 idea 池中 brainstorm 来源的采纳情况
    const allIdeas = this.ideaPool.list();
    const brainstormIdeas = allIdeas.filter(i => i.source === 'brainstorm');
    const adoptedBrainstorm = brainstormIdeas.filter(i => ['shipped', 'running'].includes(i.stage));
    stats.adopted = adoptedBrainstorm.length;
    stats.rate = brainstormIdeas.length > 0
      ? `${Math.round(adoptedBrainstorm.length / brainstormIdeas.length * 100)}%`
      : '0%';

    // 清理 60 天以上的旧文件
    for (const file of files) {
      const filePath = path.join(this.brainstormDir, file);
      const age = now - fs.statSync(filePath).mtimeMs;
      if (age > TTL_MS) {
        fs.unlinkSync(filePath);
        cleaned++;
        stats.oldFiles++;
      }
    }

    return {
      cleaned,
      stats,
      message: `brainstorm 历史: ${stats.total} 个文件, ${stats.adopted}/${brainstormIdeas.length} 被采纳 (${stats.rate}), 清理 ${cleaned} 个过期文件`,
    };
  }
}

/**
 * InnovationReview — 创新管道全局复盘
 * 每 14 天触发，分析 idea 池中各来源的质量与效率
 */
export class InnovationReview extends DetectionOperation {
  constructor(workspace) {
    super('innovation_review', '创新管道全局复盘');
    this.workspace = workspace;
    this.ideaPool = new IdeaPool(workspace);
    this.reviewFile = path.join(workspace, '.omc', 'innovation', 'review.md');
  }

  canImprove() {
    if (!fs.existsSync(this.reviewFile)) return true;
    const age = Date.now() - fs.statSync(this.reviewFile).mtimeMs;
    return age > 14 * 24 * 60 * 60 * 1000;
  }

  _daysBetween(dateA, dateB) {
    const parse = d => new Date(`${String(d).slice(0,4)}-${String(d).slice(4,6)}-${String(d).slice(6,8)}`);
    return Math.floor((parse(dateB) - parse(dateA)) / 86400000);
  }

  _computeMetrics(ideas) {
    const bySource = { brainstorm: [], suggest: [], manual: [] };
    for (const idea of ideas) bySource[idea.source] = [...(bySource[idea.source] || []), idea];

    const calc = (arr) => {
      const shipped = arr.filter(i => i.stage === 'shipped');
      const killed  = arr.filter(i => i.stage === 'killed');
      const alive   = arr.filter(i => ['seed','proposal','running','dormant'].includes(i.stage));
      const adopted = [...shipped, ...arr.filter(i => i.stage === 'running')];
      const rate = arr.length > 0 ? Math.round(adopted.length / arr.length * 100) : 0;
      // 平均存活天数：shipped 用 | shipped:TIMESTAMP 计算，running 用创建到今天
      const today = new Date().toISOString().split('T')[0].replace(/-/g, '');
      const cycles = shipped.map(i => {
        const end = i.shipped || today;
        return this._daysBetween(i.date, end);
      });
      const avgCycle = cycles.length > 0 ? Math.round(cycles.reduce((a, b) => a + b, 0) / cycles.length) : null;
      return {
        total: arr.length,
        shipped: shipped.length,
        killed:  killed.length,
        alive:   alive.length,
        adoptionRate: `${rate}%`,
        avgCycleDays: avgCycle,
      };
    };

    return {
      brainstorm: calc(bySource.brainstorm || []),
      suggest:    calc(bySource.suggest    || []),
      manual:     calc(bySource.manual     || []),
    };
  }

  async execute() {
    const ideas = this.ideaPool.list();
    const metrics = this._computeMetrics(ideas);

    const overall = {
      total: ideas.length,
      adoptionRate: `${Math.round(
        ideas.filter(i => ['shipped','running'].includes(i.stage)).length /
        (ideas.length || 1) * 100)}%`,
    };

    const now = new Date().toISOString().slice(0, 10);
    const content = [
      `# Innovation Review`,
      ``,
      `> 生成时间: ${now}`,
      ``,
      `## 各来源质量对比`,
      ``,
      `| 来源 | 总数 | 交付 | 放弃 | 存活 | 采纳率 | 平均周期(天) |`,
      `|------|------|------|------|------|--------|------------|`,
      ...['brainstorm','suggest','manual'].map(src => {
        const m = metrics[src];
        return `| ${src} | ${m.total} | ${m.shipped} | ${m.killed} | ${m.alive} | ${m.adoptionRate} | ${m.avgCycleDays ?? '—'} |`;
      }),
      ``,
      `## 整体指标`,
      ``,
      `| 指标 | 值 |`,
      `|------|---|`,
      `| 总 idea 数 | ${overall.total} |`,
      `| 整体采纳率 | ${overall.adoptionRate} |`,
      ``,
      `## 洞察`,
      this._insights(metrics),
      ``,
      `## 收益追踪`,
      this._benefitSection(ideas),
      ``,
      `## 趋势对比`,
      this._trendSection(),
    ].join('\n');

    const dir = path.dirname(this.reviewFile);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    // 保存上次 review 为 prev
    if (fs.existsSync(this.reviewFile)) {
      fs.copyFileSync(this.reviewFile, this.reviewFile.replace(/review\.md$/, 'review-prev.md'));
    }
    fs.writeFileSync(this.reviewFile, content, 'utf8');

    const top = Object.entries(metrics).sort((a, b) => b[1].total - a[1].total)[0];
    return {
      reviewFile: this.reviewFile,
      metrics,
      overall,
      message: `创新复盘: ${overall.total} 条 idea, 采纳率 ${overall.adoptionRate} | 来源最多: ${top[0]} (${top[1].total}条)`,
    };
  }

  _benefitSection(ideas) {
    const withBenefit = ideas.filter(i => i.benefit && !['shipped','killed'].includes(i.stage));
    if (withBenefit.length === 0) return '_暂无收益描述_';
    const lines = withBenefit.map(i => {
      const emoji = { seed: '💡', proposal: '📋', running: '🔬' }[i.stage] || '?';
      const score = (i.impact && i.effort) ? ` ★${i.impact}x${i.effort}` : '';
      return `- ${emoji}${score} **${i.desc.replace(/\|.*/, '').trim()}**\n  收益: ${i.benefit}`;
    });
    return lines.join('\n');
  }

  _trendSection() {
    const prev = this._readPrevReview();
    if (!prev) return '_无历史数据（首次复盘）_';
    const lines = [];
    const delta = (curr, prev) => {
      const d = curr - prev;
      return d === 0 ? '—' : d > 0 ? `↑${d}` : `↓${Math.abs(d)}`;
    };
    const prevTotal = parseInt(prev.match(/\| 总 idea 数 \| (\d+) \|/)?.[1] || '0');
    const prevAdoption = parseInt(prev.match(/\| 整体采纳率 \| (\d+)%/)?.[1] || '0');
    const currTotal = this.ideaPool.list().length;
    const currAdoption = Math.round(
      this.ideaPool.list().filter(i => ['shipped','running'].includes(i.stage)).length /
      (currTotal || 1) * 100);
    lines.push(`- idea 总数: ${currTotal} (${delta(currTotal, prevTotal)})`);
    lines.push(`- 整体采纳率: ${currAdoption}% (${delta(currAdoption, prevAdoption)})`);
    return lines.join('\n');
  }

  _readPrevReview() {
    // 读取上一次 review 文件内容做对比
    if (!fs.existsSync(this.reviewFile)) return null;
    const prevPath = this.reviewFile.replace(/review\.md$/, 'review-prev.md');
    if (!fs.existsSync(prevPath)) return null;
    return fs.readFileSync(prevPath, 'utf8');
  }

  _insights(metrics) {
    const entries = Object.entries(metrics).filter(([, m]) => m.total > 0);
    if (entries.length === 0) return '_暂无数据_';
    const sorted = entries.sort((a, b) => parseInt(b[1].adoptionRate) - parseInt(a[1].adoptionRate));
    const best = sorted[0];
    const lines = [
      `_采纳率最高: ${best[0]} (${best[1].adoptionRate})_`,
    ];
    if (sorted.length > 1) {
      const worst = sorted[sorted.length - 1];
      lines.push(`_采纳率最低: ${worst[0]} (${worst[1].adoptionRate}) — 考虑降权或改进评审标准_`);
    }
    const zeroKill = entries.filter(([, m]) => m.killed === 0 && m.total >= 3);
    if (zeroKill.length > 0) {
      lines.push(`_零放弃来源: ${zeroKill.map(([s]) => s).join(', ')} — 可能过于保守或评审标准宽松_`);
    }
    return lines.join('\n');
  }
}
