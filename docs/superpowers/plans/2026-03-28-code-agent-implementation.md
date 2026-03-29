# Code Intelligence Agent 实施计划

> **Selected Theme:** Code Intelligence + Agent Learning (方案 A + E)  
> **Date:** 2026-03-28  
> **Status:** Draft  
> **Estimated Time:** 4-5 天

---

## 1. 项目概述

### 1.1 目标

构建 **Code Intelligence Agent** — 一个基于 Semgrep + Tree-sitter 的智能代码分析代理，能够：
- 检测安全漏洞 (Semgrep 20k+ 规则)
- 分析代码质量 (Tree-sitter 自定义)
- 与 Patrol Agent/AI Roundtable 协作 (A2A)
- 学习优化分析策略 (Learning Engine)

### 1.2 与现有项目集成

```
Patrol Agent ──► 发现代码问题 ──► 委托 Code Agent
                                        │
                                        ▼
                                 Semgrep 扫描
                                        │
                                        ▼
                                 Tree-sitter 分析
                                        │
                                        ▼
                                 存储到 Memory Mesh
                                        │
                                        ▼
                                 返回结果给 Patrol
                                        │
                                        ▼
                                 Learning Engine 学习
```

---

## 2. 架构设计

### 2.1 组件架构

```
┌─────────────────────────────────────────────────────────┐
│                    Code Agent (MCP Server)               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │  Scanner        │───►│  Analyzer       │            │
│  │  ───────────    │    │  ───────────    │            │
│  │                 │    │                 │            │
│  │  • File Watcher │    │  • Semgrep      │            │
│  │  • Git Hook     │    │  • Tree-sitter  │            │
│  │  • A2A Trigger  │    │  • Custom Rules │            │
│  └─────────────────┘    └─────────────────┘            │
│           │                      │                      │
│           ▼                      ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │  Language       │    │  Reporter       │            │
│  │  Parsers        │    │  ───────────    │            │
│  │  ───────────    │    │                 │            │
│  │                 │    │  • A2A Output   │            │
│  │  • JavaScript   │    │  • Memory Store │            │
│  │  • TypeScript   │    │  • JSON Report  │            │
│  │  • Python       │    │  • Learning     │            │
│  │  • Go           │    │                 │            │
│  └─────────────────┘    └─────────────────┘            │
│                                                          │
│  ┌─────────────────────────────────────────┐            │
│  │              A2A Client                  │            │
│  │  ────────────────────────────────       │            │
│  │  • Register: code-agent                 │            │
│  │  • Capabilities: analyze, scan, security│            │
│  │  • Handlers: TASK, QUERY                │            │
│  └─────────────────────────────────────────┘            │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
输入:
  ├── 文件路径 (from Patrol Agent)
  ├── 代码内容 (from Git Hook)
  └── 分析请求 (from A2A TASK)
      │
      ▼
处理:
  ├── 识别语言 → 选择 Parser
  ├── Semgrep 扫描 → 安全漏洞
  ├── Tree-sitter 分析 → 代码质量
  ├── 合并结果 → Deduplicate
      │
      ▼
输出:
  ├── JSON Report
  ├── Memory 存储
  ├── A2A TASK_RESULT
  └── Learning 数据
```

---

## 3. Phase 1: 基础架构 (Day 1)

### 3.1 项目结构

```
80-PROJECTS/code-agent/
├── package.json
├── src/
│   ├── server.js           # MCP Server 入口
│   ├── agent.js            # Code Agent 核心
│   ├── scanner/
│   │   ├── fileScanner.js  # 文件扫描
│   │   └── gitScanner.js   # Git Hook 扫描
│   ├── analyzer/
│   │   ├── semgrepWrapper.js  # Semgrep 调用
│   │   ├── treeSitterAnalyzer.js  # Tree-sitter 分析
│   │   ├── ruleEngine.js      # 自定义规则
│   │   └── languageParser.js  # 语言选择
│   ├── reporter/
│   │   ├── resultFormatter.js  # 结果格式化
│   │   ├── memoryStore.js      # Memory 存储
│   │   └── a2aOutput.js        # A2A 输出
│   ├── a2a/
│   │   ├── a2aClient.js     # A2A Client
│   │   └── handlers.js      # TASK/QUERY 处理
│   └── learning/
│       ├── feedbackLoop.js  # 反馈收集
│       └── optimizer.js     # 策略优化
├── rules/
│   ├── security/           # 安全规则
│   ├── quality/            # 质量规则
│   └── custom/             # 自定义规则
├── tests/
│   ├── test-agent.js
│   ├── test-semgrep.js
│   └── test-treesitter.js
└── docs/
    ├── README.md
    └── RULES.md
```

### 3.2 Task 1.1: 创建项目骨架

**文件清单:**
- [ ] `package.json` — 项目配置
- [ ] `src/server.js` — MCP Server
- [ ] `src/agent.js` — Agent 核心

**package.json:**
```json
{
  "name": "code-agent",
  "version": "1.0.0",
  "description": "Code Intelligence Agent - Semgrep + Tree-sitter",
  "type": "module",
  "main": "src/server.js",
  "scripts": {
    "start": "node src/server.js",
    "test": "node tests/test-agent.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "tree-sitter": "^0.21.0",
    "tree-sitter-javascript": "^0.21.0",
    "tree-sitter-typescript": "^0.21.0",
    "tree-sitter-python": "^0.21.0",
    "uuid": "^9.0.0",
    "yaml": "^2.3.0"
  },
  "keywords": ["mcp", "code-analysis", "semgrep", "tree-sitter"],
  "author": "Feishu",
  "license": "MIT"
}
```

### 3.3 Task 1.2: MCP Server 框架

**server.js (骨架):**
```javascript
#!/usr/bin/env node
/**
 * Code Agent MCP Server
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { CodeAgent } from './agent.js';

const agent = new CodeAgent();

const server = new Server(
  {
    name: 'code-agent',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Tools 定义 (后续完善)
const TOOLS = [
  { name: 'code_scan_file', description: 'Scan a file for issues' },
  { name: 'code_scan_project', description: 'Scan entire project' },
  { name: 'code_get_security', description: 'Get security findings' },
  { name: 'code_get_quality', description: 'Get quality metrics' },
];

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS.map(t => ({
    name: t.name,
    description: t.description,
    inputSchema: { type: 'object', properties: {} }
  }))
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  // 处理逻辑 (后续完善)
  return { content: [{ type: 'text', text: 'TODO' }] };
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.log('[Code Agent] MCP Server started');
}

main().catch(console.error);
```

### 3.4 Task 1.3: A2A Client 集成

**复制现有 A2A Client:**
- [ ] 复制 `.omc/patrol-agent/src/a2a/a2aClient.js`
- [ ] 修改 agentId 为 `code-agent`
- [ ] 修改 capabilities 为 `['analyze', 'scan', 'security', 'quality']`

---

## 4. Phase 2: Semgrep 集成 (Day 2)

### 4.1 Task 2.1: Semgrep Wrapper

**semgrepWrapper.js:**
```javascript
/**
 * Semgrep CLI Wrapper
 */

import { execSync } from 'child_process';
import path from 'path';

class SemgrepWrapper {
  constructor(options = {}) {
    this.timeout = options.timeout || 60000;
    this.rulesPath = options.rulesPath || './rules';
    this.configSets = options.configSets || [
      'p/security-audit',
      'p/owasp-top-ten',
      'p/javascript'
    ];
  }

  /**
   * 检查 Semgrep 是否可用
   */
  isAvailable() {
    try {
      execSync('semgrep --version', { encoding: 'utf-8', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * 扫描单个文件
   */
  scanFile(filePath, options = {}) {
    const configs = options.configs || this.configSets;
    const configArgs = configs.map(c => `--config=${c}`).join(' ');
    
    const cmd = `semgrep ${configArgs} ${filePath} --json --quiet`;
    
    try {
      const result = execSync(cmd, {
        encoding: 'utf-8',
        timeout: this.timeout,
        cwd: options.cwd || process.cwd()
      });
      
      return this.parseResult(JSON.parse(result));
    } catch (error) {
      if (error.stdout) {
        return this.parseResult(JSON.parse(error.stdout));
      }
      return { success: false, error: error.message };
    }
  }

  /**
   * 扫描项目
   */
  scanProject(projectPath, options = {}) {
    const configs = options.configs || this.configSets;
    const configArgs = configs.map(c => `--config=${c}`).join(' ');
    
    const cmd = `semgrep ${configArgs} ${projectPath} --json --quiet`;
    
    try {
      const result = execSync(cmd, {
        encoding: 'utf-8',
        timeout: this.timeout * 5, // 项目扫描更长时间
        cwd: projectPath
      });
      
      return this.parseResult(JSON.parse(result));
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * 解析 Semgrep JSON 结果
   */
  parseResult(jsonResult) {
    const findings = [];
    
    for (const result of jsonResult.results || []) {
      findings.push({
        ruleId: result.check_id,
        message: result.extra?.message || result.check_id,
        severity: result.extra?.severity || 'WARNING',
        category: 'security',
        location: {
          file: result.path,
          line: result.start?.line,
          column: result.start?.col,
          endLine: result.end?.line,
          endColumn: result.end?.col
        },
        code: result.extra?.lines || '',
        fix: result.extra?.fix || null,
        metadata: result.extra?.metadata || {}
      });
    }
    
    return {
      success: true,
      findings,
      summary: {
        total: findings.length,
        bySeverity: this.groupBySeverity(findings),
        byRule: this.groupByRule(findings)
      }
    };
  }

  groupBySeverity(findings) {
    return findings.reduce((acc, f) => {
      acc[f.severity] = (acc[f.severity] || 0) + 1;
      return acc;
    }, {});
  }

  groupByRule(findings) {
    return findings.reduce((acc, f) => {
      acc[f.ruleId] = (acc[f.ruleId] || 0) + 1;
      return acc;
    }, {});
  }
}

export default SemgrepWrapper;
```

### 4.2 Task 2.2: 安全规则配置

**rules/security/owasp.yaml:**
```yaml
rules:
  - id: sql-injection-risk
    languages: [javascript, typescript]
    message: "Potential SQL injection - use parameterized queries"
    severity: ERROR
    patterns:
      - pattern-either:
          - pattern: $DB.query($QUERY + ...)
          - pattern: $DB.query(`...${$X}...`)
    metadata:
      cwe: "CWE-89"
      owasp: "A01:2021"

  - id: xss-risk
    languages: [javascript, typescript]
    message: "Potential XSS - sanitize user input"
    severity: ERROR
    patterns:
      - pattern-either:
          - pattern: $EL.innerHTML = $X
          - pattern: document.write($X)
    metadata:
      cwe: "CWE-79"
      owasp: "A03:2021"
```

### 4.3 Task 2.3: MCP Tools 定义

**添加 Semgrep MCP Tools:**
```javascript
const TOOLS = [
  {
    name: 'code_scan_security',
    description: 'Scan file/project for security vulnerabilities using Semgrep',
    inputSchema: {
      type: 'object',
      properties: {
        path: { type: 'string', description: 'File or project path' },
        configs: { type: 'array', description: 'Semgrep config sets' }
      },
      required: ['path']
    }
  },
  {
    name: 'code_get_findings',
    description: 'Get security findings from last scan',
    inputSchema: {
      type: 'object',
      properties: {
        severity: { type: 'string', enum: ['ERROR', 'WARNING', 'INFO'] }
      }
    }
  }
];
```

---

## 5. Phase 3: Tree-sitter 集成 (Day 3)

### 5.1 Task 3.1: Tree-sitter 分析器

**treeSitterAnalyzer.js:**
```javascript
/**
 * Tree-sitter Code Analyzer
 */

import Parser from 'tree-sitter';
import JavaScript from 'tree-sitter-javascript';
import TypeScript from 'tree-sitter-typescript';
import Python from 'tree-sitter-python';

class TreeSitterAnalyzer {
  constructor() {
    this.parsers = new Map();
    this.initParsers();
    this.rules = this.loadRules();
  }

  initParsers() {
    const jsParser = new Parser();
    jsParser.setLanguage(JavaScript);
    this.parsers.set('javascript', jsParser);
    this.parsers.set('js', jsParser);

    const tsParser = new Parser();
    tsParser.setLanguage(TypeScript.typescript);
    this.parsers.set('typescript', tsParser);
    this.parsers.set('ts', tsParser);

    const pyParser = new Parser();
    pyParser.setLanguage(Python);
    this.parsers.set('python', pyParser);
    this.parsers.set('py', pyParser);
  }

  /**
   * 识别文件语言
   */
  detectLanguage(filePath) {
    const ext = filePath.split('.').pop().toLowerCase();
    return this.parsers.has(ext) ? ext : null;
  }

  /**
   * 分析文件
   */
  analyzeFile(filePath, sourceCode, options = {}) {
    const language = this.detectLanguage(filePath);
    if (!language) {
      return { success: false, error: 'Unsupported language' };
    }

    const parser = this.parsers.get(language);
    const tree = parser.parse(sourceCode);

    const metrics = {
      complexity: this.calculateComplexity(tree.rootNode),
      structure: this.analyzeStructure(tree.rootNode),
      quality: this.analyzeQuality(tree.rootNode, language)
    };

    const issues = this.detectIssues(tree.rootNode, language, options);

    return {
      success: true,
      language,
      metrics,
      issues,
      astSummary: this.summarizeAST(tree.rootNode)
    };
  }

  /**
   * 计算圈复杂度
   */
  calculateComplexity(node) {
    const branches = ['if_statement', 'else_clause', 'for_statement', 
                      'while_statement', 'switch_case', 'catch_clause'];
    
    let count = 1; // Base path
    const traverse = (n) => {
      if (branches.includes(n.type)) count++;
      for (const child of n.children || []) traverse(child);
    };
    traverse(node);
    
    return { cyclomatic: count, rating: this.rateComplexity(count) };
  }

  rateComplexity(count) {
    if (count <= 10) return 'low';
    if (count <= 20) return 'medium';
    if (count <= 50) return 'high';
    return 'very-high';
  }

  /**
   * 分析代码结构
   */
  analyzeStructure(node) {
    const structure = {
      functions: 0,
      classes: 0,
      imports: 0,
      exports: 0,
      maxNesting: 0,
      avgFunctionLength: 0
    };

    const functionLengths = [];
    const traverse = (n, depth = 0) => {
      structure.maxNesting = Math.max(structure.maxNesting, depth);
      
      if (n.type === 'function_declaration' || n.type === 'function_expression') {
        structure.functions++;
        const lines = n.endPosition.row - n.startPosition.row;
        functionLengths.push(lines);
      }
      if (n.type === 'class_declaration') structure.classes++;
      if (n.type === 'import_statement') structure.imports++;
      if (n.type === 'export_statement') structure.exports++;
      
      for (const child of n.children || []) traverse(child, depth + 1);
    };
    traverse(node);

    if (functionLengths.length > 0) {
      structure.avgFunctionLength = Math.round(
        functionLengths.reduce((a, b) => a + b, 0) / functionLengths.length
      );
    }

    return structure;
  }

  /**
   * 检测代码问题
   */
  detectIssues(node, language, options) {
    const issues = [];
    const rules = options.rules || this.rules;
    
    for (const rule of rules) {
      if (rule.languages.includes(language)) {
        const matches = rule.detect(node);
        issues.push(...matches);
      }
    }
    
    return issues;
  }

  /**
   * 加载规则
   */
  loadRules() {
    return [
      {
        id: 'long-function',
        languages: ['javascript', 'typescript', 'python'],
        detect: (node) => this.detectLongFunctions(node)
      },
      {
        id: 'deep-nesting',
        languages: ['javascript', 'typescript', 'python'],
        detect: (node) => this.detectDeepNesting(node)
      },
      {
        id: 'unused-variable',
        languages: ['javascript', 'typescript'],
        detect: (node) => this.detectUnusedVariables(node)
      }
    ];
  }

  detectLongFunctions(node, maxLines = 50) {
    const issues = [];
    const traverse = (n) => {
      if (n.type === 'function_declaration' || n.type === 'function_expression') {
        const lines = n.endPosition.row - n.startPosition.row;
        if (lines > maxLines) {
          issues.push({
            ruleId: 'long-function',
            severity: 'WARNING',
            message: `Function is ${lines} lines (max ${maxLines})`,
            location: { line: n.startPosition.row + 1 }
          });
        }
      }
      for (const child of n.children || []) traverse(child);
    };
    traverse(node);
    return issues;
  }

  detectDeepNesting(node, maxDepth = 4) {
    const issues = [];
    const traverse = (n, depth = 0) => {
      if (depth > maxDepth) {
        issues.push({
          ruleId: 'deep-nesting',
          severity: 'WARNING',
          message: `Nesting depth ${depth} (max ${maxDepth})`,
          location: { line: n.startPosition.row + 1 }
        });
      }
      for (const child of n.children || []) traverse(child, depth + 1);
    };
    traverse(node);
    return issues;
  }

  summarizeAST(node) {
    return {
      nodeCount: this.countNodes(node),
      nodeTypes: this.getNodeTypes(node),
      depth: this.getMaxDepth(node)
    };
  }

  countNodes(node) {
    let count = 1;
    for (const child of node.children || []) count += this.countNodes(child);
    return count;
  }

  getNodeTypes(node) {
    const types = new Set();
    const traverse = (n) => {
      types.add(n.type);
      for (const child of n.children || []) traverse(child);
    };
    traverse(node);
    return Array.from(types);
  }

  getMaxDepth(node) {
    let max = 0;
    const traverse = (n, depth) => {
      max = Math.max(max, depth);
      for (const child of n.children || []) traverse(child, depth + 1);
    };
    traverse(node, 0);
    return max;
  }
}

export default TreeSitterAnalyzer;
```

### 5.2 Task 3.2: MCP Tools 扩展

**添加 Tree-sitter MCP Tools:**
```javascript
{
  name: 'code_analyze_quality',
  description: 'Analyze code quality metrics using Tree-sitter',
  inputSchema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: 'File path' },
      content: { type: 'string', description: 'File content (optional)' }
    },
    required: ['path']
  }
},
{
  name: 'code_get_metrics',
  description: 'Get code complexity and structure metrics',
  inputSchema: {
    type: 'object',
    properties: {}
  }
}
```

---

## 6. Phase 4: A2A 集成 (Day 4)

### 6.1 Task 4.1: A2A Handlers

**a2a/handlers.js:**
```javascript
/**
 * A2A Message Handlers
 */

import { v4 as uuidv4 } from 'uuid';

export function setupHandlers(a2aClient, codeAgent) {
  
  // 处理 TASK 消息
  a2aClient.on('TASK', async (message) => {
    console.log(`[A2A] TASK from ${message.from}: ${message.payload.task}`);
    
    const { task, filePath, projectPath, options } = message.payload;
    
    let result;
    
    switch (task) {
      case 'analyze_file':
        result = await codeAgent.analyzeFile(filePath, options);
        break;
      
      case 'scan_project':
        result = await codeAgent.scanProject(projectPath, options);
        break;
      
      case 'security_check':
        result = await codeAgent.securityScan(filePath, options);
        break;
      
      case 'quality_check':
        result = await codeAgent.qualityCheck(filePath, options);
        break;
      
      default:
        result = { success: false, error: 'Unknown task' };
    }
    
    // 发送结果
    await a2aClient.send({
      type: 'TASK_RESULT',
      to: message.from,
      priority: 'NORMAL',
      payload: {
        taskId: message.id,
        success: result.success,
        findings: result.findings,
        metrics: result.metrics,
        summary: result.summary
      },
      metadata: {
        correlationId: message.metadata?.correlationId
      }
    });
    
    // 存储到 Memory
    if (result.success && result.findings?.length > 0) {
      await codeAgent.storeFindings(result, message.from);
    }
  });
  
  // 处理 QUERY 消息
  a2aClient.on('QUERY', async (message) => {
    const { query } = message.payload;
    
    let response;
    
    switch (query) {
      case 'capabilities':
        response = {
          agentId: 'code-agent',
          capabilities: ['analyze', 'scan', 'security', 'quality', 'complexity'],
          status: 'idle',
          supportedLanguages: ['javascript', 'typescript', 'python']
        };
        break;
      
      case 'status':
        response = codeAgent.getStatus();
        break;
      
      case 'last_results':
        response = codeAgent.getLastResults();
        break;
      
      default:
        response = { error: 'Unknown query' };
    }
    
    await a2aClient.send({
      type: 'RESPONSE',
      to: message.from,
      payload: response,
      metadata: { correlationId: message.metadata?.correlationId }
    });
  });
  
  // 处理 EVENT 消息
  a2aClient.on('EVENT', async (message) => {
    const { event } = message.payload;
    
    if (event === 'file_changed') {
      // 自动分析变更的文件
      const { filePath } = message.payload;
      await codeAgent.analyzeFile(filePath);
    }
    
    if (event === 'git_commit') {
      // 分析最近提交的文件
      const { files } = message.payload;
      for (const file of files) {
        await codeAgent.analyzeFile(file);
      }
    }
  });
}
```

### 6.2 Task 4.2: 与 Patrol Agent 联动

**Patrol Agent 委托调用:**
```javascript
// 在 Patrol Agent 中添加代码分析委托
async function delegateCodeAnalysis(filePath) {
  if (!a2aClient || !a2aClient.isMcpAvailable()) {
    log(`[A2A] MCP not available, skipping code analysis`);
    return null;
  }

  try {
    log(`📡 A2A: Delegating code analysis for ${filePath}...`);
    
    const result = await a2aClient.call('code-agent', {
      task: 'analyze_file',
      filePath,
      options: {
        checkSecurity: true,
        checkQuality: true,
        checkComplexity: true
      }
    }, {
      priority: 'HIGH',
      timeout: 60000
    });

    if (result.success) {
      log(`📡 A2A: Found ${result.findings?.length || 0} issues`);
      
      // 存储结果到共享记忆
      await storeSharedProblem({
        title: `Code Issues in ${filePath}`,
        description: `Found ${result.findings?.length} code quality/security issues`,
        severity: result.summary?.bySeverity?.ERROR > 0 ? 'high' : 'medium',
        project: filePath.split('/')[0],
        location: filePath,
        tags: ['code-analysis', 'quality', 'security'],
        context: JSON.stringify(result.summary)
      });
    }
    
    return result;
  } catch (error) {
    log(`[A2A] Code analysis failed: ${error.message}`);
    return null;
  }
}
```

### 6.3 Task 4.3: MCP 配置更新

**更新 `~/.openclaw/openclaw.json`:**
```json
{
  "mcp": {
    "servers": {
      "code-agent": {
        "command": "node",
        "args": ["D:/OpenClaw/workspace/80-PROJECTS/code-agent/src/server.js"]
      }
    }
  }
}
```

---

## 7. Phase 5: Learning Engine (Day 5)

### 7.1 Task 5.1: 反馈循环

**learning/feedbackLoop.js:**
```javascript
/**
 * Learning Feedback Loop
 */

class FeedbackLoop {
  constructor(memoryManager) {
    this.memory = memoryManager;
    this.feedbackHistory = [];
  }

  /**
   * 记录分析结果
   */
  recordAnalysis(analysisResult, context) {
    const feedback = {
      timestamp: Date.now(),
      result: analysisResult,
      context: {
        file: context.file,
        language: context.language,
        project: context.project
      },
      outcomes: []
    };
    
    this.feedbackHistory.push(feedback);
    return feedback;
  }

  /**
   * 记录用户反馈
   */
  recordUserFeedback(feedbackId, userAction) {
    const feedback = this.feedbackHistory.find(f => f.id === feedbackId);
    if (feedback) {
      feedback.outcomes.push({
        type: 'user_action',
        action: userAction, // 'fixed', 'ignored', 'modified'
        timestamp: Date.now()
      });
    }
  }

  /**
   * 分析反馈趋势
   */
  analyzeTrends() {
    const trends = {
      ignoredRules: new Map(),
      fixedRules: new Map(),
      accuracyByRule: new Map()
    };

    for (const feedback of this.feedbackHistory) {
      for (const finding of feedback.result.findings || []) {
        const ruleId = finding.ruleId;
        const outcome = feedback.outcomes.find(o => o.type === 'user_action');
        
        if (outcome) {
          if (outcome.action === 'ignored') {
            trends.ignoredRules.set(ruleId, (trends.ignoredRules.get(ruleId) || 0) + 1);
          }
          if (outcome.action === 'fixed') {
            trends.fixedRules.set(ruleId, (trends.fixedRules.get(ruleId) || 0) + 1);
          }
        }
      }
    }

    // 计算准确率
    for (const [ruleId, ignored] of trends.ignoredRules) {
      const fixed = trends.fixedRules.get(ruleId) || 0;
      const total = ignored + fixed;
      trends.accuracyByRule.set(ruleId, fixed / total);
    }

    return trends;
  }

  /**
   * 获取优化建议
   */
  getOptimizationSuggestions() {
    const trends = this.analyzeTrends();
    const suggestions = [];

    for (const [ruleId, accuracy] of trends.accuracyByRule) {
      if (accuracy < 0.3) {
        suggestions.push({
          ruleId,
          action: 'disable',
          reason: `Low accuracy (${accuracy.toFixed(2)}) - mostly ignored`
        });
      }
      if (accuracy > 0.8) {
        suggestions.push({
          ruleId,
          action: 'increase_priority',
          reason: `High accuracy (${accuracy.toFixed(2)}) - frequently fixed`
        });
      }
    }

    return suggestions;
  }
}

export default FeedbackLoop;
```

### 7.2 Task 5.2: 策略优化

**learning/optimizer.js:**
```javascript
/**
 * Strategy Optimizer
 */

class StrategyOptimizer {
  constructor(feedbackLoop, ruleEngine) {
    this.feedback = feedbackLoop;
    this.rules = ruleEngine;
    this.optimizations = [];
  }

  /**
   * 应用优化建议
   */
  applyOptimizations() {
    const suggestions = this.feedback.getOptimizationSuggestions();
    
    for (const suggestion of suggestions) {
      if (suggestion.action === 'disable') {
        this.rules.disableRule(suggestion.ruleId);
        this.optimizations.push({
          timestamp: Date.now(),
          ruleId: suggestion.ruleId,
          action: 'disabled',
          reason: suggestion.reason
        });
      }
      
      if (suggestion.action === 'increase_priority') {
        this.rules.setRulePriority(suggestion.ruleId, 'HIGH');
        this.optimizations.push({
          timestamp: Date.now(),
          ruleId: suggestion.ruleId,
          action: 'priority_increased',
          reason: suggestion.reason
        });
      }
    }

    return this.optimizations;
  }

  /**
   * 学习新的代码模式
   */
  learnPattern(patternData) {
    // 存储新发现的代码模式
    // 用于后续自动生成规则
    return {
      patternId: uuidv4(),
      pattern: patternData.pattern,
      occurrences: patternData.occurrences,
      learnedAt: Date.now()
    };
  }

  /**
   * 获取学习报告
   */
  getLearningReport() {
    return {
      totalAnalyses: this.feedback.feedbackHistory.length,
      optimizationsApplied: this.optimizations.length,
      topIgnoredRules: this.getTopIgnoredRules(),
      topFixedRules: this.getTopFixedRules(),
      recentOptimizations: this.optimizations.slice(-10)
    };
  }

  getTopIgnoredRules() {
    const trends = this.feedback.analyzeTrends();
    return Array.from(trends.ignoredRules.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([ruleId, count]) => ({ ruleId, count }));
  }

  getTopFixedRules() {
    const trends = this.feedback.analyzeTrends();
    return Array.from(trends.fixedRules.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([ruleId, count]) => ({ ruleId, count }));
  }
}

export default StrategyOptimizer;
```

---

## 8. 测试计划

### 8.1 单元测试

```javascript
// tests/test-agent.js

import CodeAgent from '../src/agent.js';
import SemgrepWrapper from '../src/analyzer/semgrepWrapper.js';
import TreeSitterAnalyzer from '../src/analyzer/treeSitterAnalyzer.js';

async function runTests() {
  console.log('=== Code Agent Tests ===\n');

  // Test 1: Language Detection
  console.log('Test 1: Language Detection');
  const analyzer = new TreeSitterAnalyzer();
  const langs = ['js', 'ts', 'py', 'go'];
  for (const lang of langs) {
    const detected = analyzer.detectLanguage(`test.${lang}`);
    console.log(`  .${lang} → ${detected || 'unsupported'}`);
  }

  // Test 2: Complexity Calculation
  console.log('\nTest 2: Complexity');
  const testCode = `
function test() {
  if (a) {
    if (b) {
      for (let i = 0; i < 10; i++) {
        console.log(i);
      }
    }
  }
}
`;
  const result = analyzer.analyzeFile('test.js', testCode);
  console.log(`  Cyclomatic: ${result.metrics.complexity.cyclomatic}`);
  console.log(`  Rating: ${result.metrics.complexity.rating}`);

  // Test 3: Long Function Detection
  console.log('\nTest 3: Long Function');
  const longCode = Array(60).fill('console.log(1);').join('\n');
  const wrapped = `function long() {\n${longCode}\n}`;
  const result2 = analyzer.analyzeFile('long.js', wrapped);
  console.log(`  Issues: ${result2.issues.length}`);

  // Test 4: Semgrep (if available)
  console.log('\nTest 4: Semgrep');
  const semgrep = new SemgrepWrapper();
  if (semgrep.isAvailable()) {
    console.log('  Semgrep: Available');
  } else {
    console.log('  Semgrep: Not installed (skip)');
  }

  console.log('\n=== Tests Complete ===');
}

runTests();
```

### 8.2 集成测试

- [ ] 与 Patrol Agent 联动测试
- [ ] A2A 通信测试
- [ ] Memory 存储测试
- [ ] Learning 反馈测试

---

## 9. 成功标准

| 标准 | 验证方法 |
|------|---------|
| ✅ Semgrep 扫描可用 | `semgrep.isAvailable()` 返回 true |
| ✅ Tree-sitter 解析成功 | AST 生成并可遍历 |
| ✅ 复杂度计算正确 | 测试代码复杂度匹配预期 |
| ✅ A2A 通信正常 | Patrol Agent 可委托任务 |
| ✅ Memory 存储成功 | 分析结果存储到 OpenViking |
| ✅ Learning 生效 | 反馈优化规则优先级 |

---

## 10. 文件清单

### 新建文件 (15 个)

```
80-PROJECTS/code-agent/
├── package.json
├── src/
│   ├── server.js
│   ├── agent.js
│   ├── scanner/
│   │   ├── fileScanner.js
│   │   └── gitScanner.js
│   ├── analyzer/
│   │   ├── semgrepWrapper.js
│   │   ├── treeSitterAnalyzer.js
│   │   ├── ruleEngine.js
│   │   └── languageParser.js
│   ├── reporter/
│   │   ├── resultFormatter.js
│   │   ├── memoryStore.js
│   │   └── a2aOutput.js
│   ├── a2a/
│   │   ├── a2aClient.js
│   │   └── handlers.js
│   └── learning/
│       ├── feedbackLoop.js
│       └── optimizer.js
├── rules/
│   └── security/
│       └── owasp.yaml
└── tests/
    └── test-agent.js
```

### 修改文件 (3 个)

```
.omc/patrol-agent/src/index.js       # 添加代码分析委托
C:\Users\adm\.openclaw\openclaw.json  # 添加 code-agent MCP
docs/superpowers/plans/...-PROGRESS.md # 进度追踪
```

---

## 11. 时间估算

| Phase | 任务 | 时间 | 状态 |
|-------|------|------|------|
| 1 | 基础架构 | 1 天 | ⬜ 未开始 |
| 2 | Semgrep 集成 | 1 天 | ⬜ 未开始 |
| 3 | Tree-sitter 集成 | 1 天 | ⬜ 未开始 |
| 4 | A2A 集成 | 1 天 | ⬜ 未开始 |
| 5 | Learning Engine | 1 天 | ⬜ 可选 |

**总计: 4-5 天**

---

**状态:** ✅ 实施计划完成

**下一步:** 创建项目并开始 Phase 1