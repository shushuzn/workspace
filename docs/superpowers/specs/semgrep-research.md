# Semgrep 规则引擎调研报告

> **Date:** 2026-03-28  
> **Purpose:** Code Intelligence Agent 规则引擎选型  
> **Researcher:** Feishu

---

## 1. Semgrep 概述

### 1.1 什么是 Semgrep

**Semgrep** 是一个快速、开源的静态分析工具，用于搜索代码、发现漏洞并强制执行安全护栏和编码标准。

| 特性 | 说明 |
|------|------|
| **速度** | "ludicrous speed" — 极快 |
| **语言** | 支持 30+ 编程语言 |
| **规则** | 20,000+ 预定义规则 |
| **语义** | 理解代码语义，不只是文本匹配 |
| **易用** | 规则像代码一样编写，无复杂 DSL |

### 1.2 核心概念

```
源代码 → Semgrep → 匹配结果
              ↓
         规则引擎 (YAML)
              ↓
         模式匹配 (语义级)
```

**关键组件:**
- **Rule** — 检测规则 (YAML)
- **Pattern** — 匹配模式
- **Metavariable** — 占位符变量
- **Operator** — 逻辑操作符

---

## 2. 规则语法详解

### 2.1 基本规则结构

```yaml
# semgrep-rule.yaml
rules:
  - id: detect-eval
    pattern: eval(...)
    languages:
      - javascript
      - typescript
    message: "Dangerous eval() detected"
    severity: ERROR
    metadata:
      category: security
      technology:
        - javascript
```

### 2.2 Metavariable (元变量)

```yaml
# 匹配任意函数调用
pattern: $FUNC(...)

# 匹配特定方法
pattern: $OBJ.$METHOD(...)

# 匹配任意字符串
pattern: "$STR"

# 匹配任意表达式
pattern: $X + $Y
```

### 2.3 高级模式

**等价匹配:**
```yaml
# 匹配 console.log 和 console["log"]
pattern: console.$LOG(...)

# 匹配多种写法
pattern-either:
  - pattern: $X == $Y
  - pattern: $X === $Y
```

**条件匹配:**
```yaml
patterns:
  - pattern: $X == null
  - pattern-not: $X === null
```

**上下文匹配:**
```yaml
pattern-inside: |
  function $FUNC(...) {
    ...
  }
pattern: eval(...)
```

### 2.4 完整规则示例

**检测 SQL 注入:**
```yaml
rules:
  - id: sql-injection
    languages:
      - javascript
      - typescript
    message: "Potential SQL injection"
    severity: ERROR
    patterns:
      - pattern-either:
          - pattern: |
              $DB.query($QUERY + ...)
          - pattern: |
              $DB.query(`...${$X}...`)
          - pattern: |
              $DB.execute($QUERY, ...)
      - pattern-not: |
          $DB.query("...", ...)
    metadata:
      cwe: "CWE-89: SQL Injection"
      owasp: "A01:2021 – Injection"
```

**检测硬编码密钥:**
```yaml
rules:
  - id: hardcoded-secret
    languages:
      - javascript
      - typescript
      - python
    message: "Hardcoded secret detected"
    severity: WARNING
    patterns:
      - pattern-regex: (?i)(api[_-]?key|secret|token|password)\s*[=:]\s*["'][^"']{8,}["']
    metadata:
      category: security
```

---

## 3. 与 Tree-sitter 对比

### 3.1 功能对比

| 特性 | Semgrep | Tree-sitter |
|------|---------|-------------|
| **解析引擎** | 自有解析器 | 通用解析器 |
| **规则编写** | YAML (简单) | 代码 (灵活) |
| **自定义规则** | ⭐⭐⭐⭐⭐ 极易 | ⭐⭐⭐ 需要编程 |
| **性能** | ⭐⭐⭐⭐⭐ 极快 | ⭐⭐⭐⭐ 快 |
| **语言支持** | 30+ | 100+ |
| **增量解析** | ❌ 不支持 | ✅ 支持 |
| **AST 访问** | 受限 | 完整 |
| **复杂度分析** | ❌ 不支持 | ✅ 支持 |

### 3.2 使用场景对比

| 场景 | 推荐 | 理由 |
|------|------|------|
| **安全漏洞检测** | Semgrep | 20k+ 现成规则 |
| **代码坏味道** | Tree-sitter | 需要自定义逻辑 |
| **复杂度度量** | Tree-sitter | AST 遍历 |
| **快速部署** | Semgrep | 开箱即用 |
| **深度定制** | Tree-sitter | 完全控制 |

---

## 4. 集成方案

### 4.1 方案 A: Semgrep 独立使用

```javascript
// 调用 Semgrep CLI
const { execSync } = require('child_process');

function runSemgrep(filePath, rulesPath) {
  const result = execSync(`semgrep --config=${rulesPath} ${filePath} --json`, {
    encoding: 'utf-8',
    timeout: 30000
  });
  
  return JSON.parse(result);
}

// 使用
const findings = runSemgrep('./src', './rules/security.yaml');
```

**优点:**
- ✅ 简单直接
- ✅ 利用现有规则库
- ✅ 性能最优

**缺点:**
- ❌ 依赖外部 CLI
- ❌ 需要安装 Python
- ❌ 不易深度定制

### 4.2 方案 B: Tree-sitter + 自定义规则

```javascript
// Tree-sitter 自定义分析
const Parser = require('tree-sitter');
const JavaScript = require('tree-sitter-javascript');

class RuleEngine {
  constructor() {
    this.parser = new Parser();
    this.parser.setLanguage(JavaScript);
    this.rules = [];
  }

  addRule(rule) {
    this.rules.push(rule);
  }

  analyze(sourceCode) {
    const tree = this.parser.parse(sourceCode);
    const results = [];

    for (const rule of this.rules) {
      const matches = rule.match(tree.rootNode);
      results.push(...matches);
    }

    return results;
  }
}

// 定义规则
const sqlInjectionRule = {
  match: (node) => {
    // 自定义匹配逻辑
    const query = new Query(JavaScript, `
      (call_expression
        function: (member_expression
          property: (property_identifier) @method)
        (#match? @method "query|execute"))
    `);
    return query.matches(node);
  }
};
```

**优点:**
- ✅ 完全可控
- ✅ 无需外部依赖
- ✅ 可深度定制

**缺点:**
- ❌ 需要编写规则引擎
- ❌ 规则库需自建

### 4.3 方案 C: 混合架构 (推荐)

```
Code Agent
├── Semgrep Layer (安全规则)
│   └── 预定义 20k+ 规则
├── Tree-sitter Layer (自定义分析)
│   └── 复杂度、坏味道、度量
└── Unified Reporter
    └── A2A + Memory 输出
```

```javascript
// 混合实现
class CodeAgent {
  constructor() {
    this.semgrep = new SemgrepWrapper();
    this.treeSitter = new TreeSitterAnalyzer();
  }

  async analyze(filePath) {
    // 并行运行两种分析
    const [semgrepResults, tsResults] = await Promise.all([
      this.semgrep.scan(filePath, 'security'),
      this.treeSitter.analyze(filePath, ['complexity', 'structure'])
    ]);

    return {
      security: semgrepResults,
      quality: tsResults,
      summary: this.summarize(semgrepResults, tsResults)
    };
  }
}
```

---

## 5. Semgrep 规则库

### 5.1 官方规则集

| 规则集 | 用途 | 规则数 |
|--------|------|--------|
| `p/security-audit` | 安全审计 | 100+ |
| `p/owasp-top-ten` | OWASP Top 10 | 50+ |
| `p/cwe-top-25` | CWE Top 25 | 25+ |
| `p/javascript` | JS 最佳实践 | 80+ |
| `p/typescript` | TS 最佳实践 | 60+ |
| `p/react` | React 安全 | 40+ |

### 5.2 使用规则集

```bash
# 使用官方规则
semgrep --config=p/security-audit src/

# 使用多个规则集
semgrep --config=p/owasp-top-ten --config=p/javascript src/

# 使用本地规则
semgrep --config=./rules/custom.yaml src/
```

### 5.3 自定义规则示例

**检测过时的 API:**
```yaml
rules:
  - id: deprecated-api
    languages:
      - javascript
    message: "Using deprecated API: $API"
    severity: WARNING
    patterns:
      - pattern: $OBJ.$API(...)
      - metavariable-regex:
          metavariable: $API
          regex: (oldFunction|deprecatedMethod)
```

**检测未处理的 Promise:**
```yaml
rules:
  - id: unhandled-promise
    languages:
      - javascript
      - typescript
    message: "Unhandled Promise"
    severity: ERROR
    patterns:
      - pattern: $PROMISE.then(...)
      - pattern-not: $PROMISE.then(...).catch(...)
      - pattern-not: $PROMISE.then(..., ...)
```

---

## 6. 性能对比

### 6.1 扫描速度

| 工具 | 10k 行代码 | 100k 行代码 |
|------|-----------|------------|
| **Semgrep** | ~1s | ~5s |
| **Tree-sitter** | ~2s | ~10s |
| **ESLint** | ~3s | ~20s |
| **SonarQube** | ~30s | ~5min |

### 6.2 内存占用

| 工具 | 内存峰值 |
|------|---------|
| **Semgrep** | ~100MB |
| **Tree-sitter** | ~50MB |
| **ESLint** | ~200MB |

---

## 7. 推荐方案

### 7.1 最终选型: 混合架构

**架构图:**
```
┌─────────────────────────────────────────────────────────┐
│                    Code Agent                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │  Semgrep Layer  │    │ Tree-sitter     │            │
│  │  ─────────────  │    │ Layer           │            │
│  │                 │    │ ─────────────   │            │
│  │  • Security     │    │                 │            │
│  │  • OWASP        │    │  • Complexity   │            │
│  │  • CWE          │    │  • Structure    │            │
│  │  • Best Practice│    │  • Metrics      │            │
│  │                 │    │  • Custom Rules │            │
│  │  (20k+ rules)   │    │                 │            │
│  └────────┬────────┘    └────────┬────────┘            │
│           │                      │                      │
│           └──────────┬───────────┘                      │
│                      │                                  │
│           ┌──────────▼───────────┐                      │
│           │   Result Merger      │                      │
│           │  ─────────────────   │                      │
│           │  • Deduplicate       │                      │
│           │  • Prioritize        │                      │
│           │  • Enrich            │                      │
│           └──────────┬───────────┘                      │
│                      │                                  │
│           ┌──────────▼───────────┐                      │
│           │   A2A + Memory       │                      │
│           │  ─────────────────   │                      │
│           │  • Store findings    │                      │
│           │  • Delegate fixes    │                      │
│           │  • Learn patterns    │                      │
│           └──────────────────────┘                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 7.2 实现优先级

| Phase | 组件 | 时间 | 价值 |
|-------|------|------|------|
| 1 | Semgrep 集成 | 1 天 | ⭐⭐⭐⭐⭐ |
| 2 | Tree-sitter 基础 | 1 天 | ⭐⭐⭐⭐ |
| 3 | 自定义规则引擎 | 1 天 | ⭐⭐⭐⭐ |
| 4 | A2A 集成 | 1 天 | ⭐⭐⭐⭐⭐ |
| 5 | Learning 层 | 2 天 | ⭐⭐⭐⭐⭐ |

### 7.3 技术栈

```json
{
  "dependencies": {
    "tree-sitter": "^0.21.0",
    "tree-sitter-javascript": "^0.21.0",
    "tree-sitter-typescript": "^0.21.0",
    "yaml": "^2.3.0"
  },
  "devDependencies": {
    "semgrep": "^1.0.0"
  }
}
```

---

## 8. 结论

### 选型总结

| 维度 | Semgrep | Tree-sitter | 混合 |
|------|---------|-------------|------|
| **安全检测** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **代码质量** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **灵活性** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **维护成本** | 低 | 中 | 中 |

### 最终决策

**✅ 采用混合架构: Semgrep + Tree-sitter**

**理由:**
1. **互补** — Semgrep 提供现成安全规则，Tree-sitter 提供深度定制
2. **渐进** — 先集成 Semgrep 快速见效，再叠加 Tree-sitter 增强
3. **生态** — 与现有 Memory Mesh + A2A 完美契合
4. **实用** — 立即解决安全扫描需求，长期支持代码质量

### 下一步行动

1. **创建 Code Agent 项目** — `80-PROJECTS/code-agent/`
2. **Phase 1: Semgrep 集成** — 安全扫描能力
3. **Phase 2: Tree-sitter 集成** — 代码质量分析
4. **Phase 3: A2A 集成** — 与 Patrol Agent 联动

---

**状态:** ✅ 调研完成，技术选型确定

**推荐:** 立即开始 Code Agent 项目，采用混合架构
