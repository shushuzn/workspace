# code-agent

Code Intelligence Agent - Semgrep + Tree-sitter 代码分析。

## 技术栈

- JavaScript/TypeScript
- Node.js
- @modelcontextprotocol/sdk ^1.0.0
- tree-sitter (JavaScript, TypeScript, Python)
- uuid, yaml

## 开始使用

```bash
npm install
npm start
```

## MCP Tools

### code_get_ast

Query AST structure by node type — 其他 MCP Server 可通过此工具查询代码 AST：

```json
{
  "name": "code_get_ast",
  "arguments": {
    "path": "src/server.js",
    "nodeType": "function_declaration",
    "language": "javascript"
  }
}
```

支持 nodeType：`function_declaration`, `class`, `method_definition`, `arrow_function`, `variable_declarator` 等 tree-sitter 支持的所有节点类型。
