# Tree-sitter 技术调研报告

> **Date:** 2026-03-28  
> **Purpose:** Code Intelligence Agent 技术选型  
> **Researcher:** Feishu

---

## 1. Tree-sitter 概述

### 1.1 什么是 Tree-sitter

**Tree-sitter** 是一个增量解析系统，用于构建程序的语法树。

| 特性 | 说明 |
|------|------|
| **增量解析** | 只重新解析修改的部分，性能极高 |
| **通用性** | 支持 100+ 编程语言 |
| **容错性** | 即使代码有语法错误也能解析 |
| **速度** | 每秒可解析数千行代码 |
| **内存** | 语法树内存占用小 |

### 1.2 核心概念

```
源代码 → Parser → 语法树 (CST - Concrete Syntax Tree)
                           ↓
                    遍历/查询/分析
```

**关键组件:**
- **Grammar** — 语言语法定义
- **Parser** — 解析器生成器
- **Tree** — 语法树
- **Node** — 树节点
- **Query** — 模式查询语言

---

## 2. Node.js 集成方案

### 2.1 官方绑定: node-tree-sitter

**仓库:** `tree-sitter/node-tree-sitter`  
**Stars:** 835  
**License:** MIT

```bash
npm install tree-sitter
```

**基本用法:**
```javascript
const Parser = require('tree-sitter');
const JavaScript = require('tree-sitter-javascript');

const parser = new Parser();
parser.setLanguage(JavaScript);

const sourceCode = 'function hello() { console.log("world"); }';
const tree = parser.parse(sourceCode);

// 遍历语法树
const rootNode = tree.rootNode;
console.log(rootNode.type);  // "program"
console.log(rootNode.children[0].type);  // "function_declaration"
```

### 2.2 语言支持

| 语言 | Parser 包 | Stars |
|------|-----------|-------|
| JavaScript | tree-sitter-javascript | 800+ |
| TypeScript | tree-sitter-typescript | 600+ |
| Python | tree-sitter-python | 500+ |
| Rust | tree-sitter-rust | 400+ |
| Go | tree-sitter-go | 300+ |
| Java | tree-sitter-java | 250+ |
| C/C++ | tree-sitter-c/cpp | 400+ |
| JSON | tree-sitter-json | 200+ |
| Markdown | tree-sitter-markdown | 150+ |

### 2.3 Query 语言

Tree-sitter 提供强大的模式匹配查询语言:

```javascript
// 查找所有函数定义
const query = new Query(JavaScript, `
  (function_declaration
    name: (identifier) @function.name)
`);

const matches = query.matches(tree.rootNode);
for (const match of matches) {
  console.log('Function:', match.captures[0].node.text);
}
```

**常用查询模式:**

```scheme
; 所有函数调用
(call_expression
  function: (identifier) @function.call)

; 所有变量声明
(variable_declaration
  (variable_declarator
    name: (identifier) @variable.name))

; 所有类定义
(class_declaration
  name: (identifier) @class.name)

; 所有导入语句
(import_statement
  source: (string) @import.source)
```

---

## 3. 代码分析应用场景

### 3.1 代码坏味道检测

**长函数检测:**
```javascript
const query = new Query(JavaScript, `
  (function_declaration
    body: (statement_block) @function.body)
`);

// 检查函数体行数 > 50
for (const match of matches) {
  const body = match.captures[0].node;
  const lines = body.endPosition.row - body.startPosition.row;
  if (lines > 50) {
    report('long-function', body);
  }
}
```

**嵌套层级检测:**
```javascript
// 检测嵌套超过 4 层的代码
function getNestingDepth(node, depth = 0) {
  if (depth > 4) return depth;
  let maxDepth = depth;
  for (const child of node.children) {
    maxDepth = Math.max(maxDepth, getNestingDepth(child, depth + 1));
  }
  return maxDepth;
}
```

### 3.2 安全漏洞检测

**SQL 注入检测:**
```javascript
const query = new Query(JavaScript, `
  (call_expression
    function: (member_expression
      object: (identifier) @db
      property: (property_identifier) @method)
    arguments: (arguments
      (template_string) @sql)
    (#match? @method "query|execute"))
`);
```

**XSS 检测:**
```javascript
// 检测 innerHTML 赋值
(call_expression
  function: (member_expression
    property: (property_identifier) @prop)
  (#eq? @prop "innerHTML"))
```

### 3.3 代码复杂度分析

**圈复杂度计算:**
```javascript
// 统计分支数量
const branchQuery = new Query(JavaScript, `
  [
    "if"
    "else"
    "while"
    "for"
    "switch_case"
    "catch"
    "?"
  ] @branch
`);

const matches = branchQuery.matches(node);
const complexity = matches.length + 1; // +1 for base path
```

### 3.4 代码搜索

**语义搜索 vs 文本搜索:**

```javascript
// 文本搜索: 可能误匹配注释中的 "function"
// 语义搜索: 只匹配真正的函数定义
const functionQuery = new Query(JavaScript, `
  [
    (function_declaration)
    (function_expression)
    (arrow_function)
    (method_definition)
  ] @function
`);
```

---

## 4. 与现有项目集成方案

### 4.1 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                  Code Intelligence Agent                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │   Parser    │───►│   Analyzer  │───►│   Reporter  │ │
│  │  (Tree-sitter)│   │  (Rules)    │   │  (Results)  │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │  Language   │    │   Rules     │    │   A2A/      │ │
│  │   Parsers   │    │   Engine    │    │   Memory    │ │
│  │  (10+ langs)│    │ (Semgrep-like)│   │   Output   │ │
│  └─────────────┘    └─────────────┘    └─────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 4.2 与 Patrol Agent 集成

```javascript
// Patrol Agent 发现问题时委托
async function analyzeCode(filePath) {
  const codeAgent = getCodeAgent();
  
  // A2A 委托
  const result = await a2aClient.call('code-agent', {
    task: 'analyze_file',
    filePath,
    checks: ['complexity', 'security', 'style']
  });
  
  // 存储结果
  await storeSharedMemory('code-analysis', result);
  
  return result;
}
```

### 4.3 与 Memory Mesh 集成

```javascript
// 存储代码模式
await sharedMemoryManager.storeSharedMemory('code-pattern', {
  pattern: 'long-function',
  file: 'src/index.js',
  location: { line: 45, column: 0 },
  severity: 'medium',
  suggestion: 'Extract into smaller functions'
}, {
  sourceAgent: 'code-agent',
  tags: ['code-quality', 'refactoring']
});
```

---

## 5. 技术选型决策

### 5.1 Tree-sitter vs 替代方案

| 方案 | 优点 | 缺点 | 选择 |
|------|------|------|------|
| **Tree-sitter** | 快、增量、多语言、容错 | 需学习 Query 语言 | ✅ 推荐 |
| **Babel** | JS/TS 生态好 | 仅 JS、内存占用大 | ❌ 局限 |
| **TypeScript Compiler** | 类型信息 | 仅 TS、慢 | ❌ 局限 |
| **Semgrep** | 规则丰富、即用 | 外部依赖、定制难 | ⚠️ 辅助 |
| **ESLint** | 成熟、插件多 | 仅 JS、非语义分析 | ⚠️ 辅助 |

### 5.2 推荐技术栈

```javascript
// 核心解析
"tree-sitter": "^0.21.0"
"tree-sitter-javascript": "^0.21.0"
"tree-sitter-typescript": "^0.21.0"

// 规则引擎 (轻量级)
"@semgrep/semgrep": "^1.0.0" // 可选，用于复杂规则

// 代码度量
"complexity-report": "^1.0.0" // 圈复杂度
```

---

## 6. 实现计划

### Phase 1: 基础解析 (Day 1)

- [ ] 安装 tree-sitter 和语言 parsers
- [ ] 实现文件解析器
- [ ] 实现基础 AST 遍历

### Phase 2: 查询引擎 (Day 2)

- [ ] 实现 Query 构建器
- [ ] 支持常用查询模式
- [ ] 实现结果格式化

### Phase 3: 规则系统 (Day 3)

- [ ] 定义代码坏味道规则
- [ ] 实现安全检测规则
- [ ] 集成到 A2A

### Phase 4: 集成测试 (Day 4)

- [ ] 与 Patrol Agent 联动
- [ ] 存储结果到 Memory
- [ ] 端到端测试

---

## 7. 代码示例

### 7.1 完整分析流程

```javascript
// codeAgent.js
import Parser from 'tree-sitter';
import JavaScript from 'tree-sitter-javascript';

class CodeAgent {
  constructor() {
    this.parser = new Parser();
    this.parser.setLanguage(JavaScript);
    this.rules = this.loadRules();
  }

  analyze(sourceCode, options = {}) {
    const tree = this.parser.parse(sourceCode);
    const results = [];

    for (const rule of this.rules) {
      const matches = rule.check(tree.rootNode);
      results.push(...matches);
    }

    return {
      file: options.filePath,
      issues: results,
      summary: this.summarize(results)
    };
  }

  loadRules() {
    return [
      new LongFunctionRule(),
      new DeepNestingRule(),
      new UnusedVariableRule(),
      new SecurityRiskRule()
    ];
  }

  summarize(issues) {
    return {
      total: issues.length,
      bySeverity: issues.reduce((acc, i) => {
        acc[i.severity] = (acc[i.severity] || 0) + 1;
        return acc;
      }, {})
    };
  }
}

// 规则示例: 长函数检测
class LongFunctionRule {
  constructor(maxLines = 50) {
    this.maxLines = maxLines;
    this.query = new Query(JavaScript, `
      (function_declaration
        name: (identifier) @name
        body: (statement_block) @body)
    `);
  }

  check(node) {
    const matches = this.query.matches(node);
    const issues = [];

    for (const match of matches) {
      const nameNode = match.captures.find(c => c.name === 'name').node;
      const bodyNode = match.captures.find(c => c.name === 'body').node;
      
      const lines = bodyNode.endPosition.row - bodyNode.startPosition.row;
      
      if (lines > this.maxLines) {
        issues.push({
          rule: 'long-function',
          severity: 'medium',
          message: `Function "${nameNode.text}" is ${lines} lines (max ${this.maxLines})`,
          location: {
            line: nameNode.startPosition.row + 1,
            column: nameNode.startPosition.column
          }
        });
      }
    }

    return issues;
  }
}

export default CodeAgent;
```

---

## 8. 结论

### 推荐方案

**✅ 采用 Tree-sitter 作为 Code Intelligence Agent 的核心解析引擎**

**理由:**
1. **性能** — 增量解析，适合实时监控
2. **多语言** — 支持 Patrol Agent 扫描的所有项目
3. **生态** — 官方维护，文档完善
4. **集成** — 与现有 Node.js 栈无缝集成
5. **扩展** — Query 语言强大，支持复杂分析

### 下一步

1. **创建 Code Agent 项目** — `80-PROJECTS/code-agent/`
2. **实现基础解析** — Tree-sitter 集成
3. **定义规则集** — 代码坏味道 + 安全规则
4. **A2A 集成** — 与 Patrol Agent 联动

---

**状态:** ✅ 调研完成，技术选型确定

**推荐:** 立即开始 Code Agent 实现
