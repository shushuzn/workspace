# Snyk Agent Scan 参考文档

> Snyk 官方安全扫描工具，用于发现和扫描 MCP servers、agent skills 的安全问题

## 概述

- **官网**: https://github.com/snyk/agent-scan
- **PyPI**: https://pypi.python.org/pypi/snyk-agent-scan
- **类型**: Python CLI 工具
- **用途**: 安全审计、漏洞检测

## 支持的 Agents

| Agent | Windows MCP | Windows Skills |
|-------|:-----------:|:--------------:|
| Windsurf | ✓ | ✓ |
| Cursor | ✓ | ✓ |
| VS Code | ✓ | ✓ |
| Claude Desktop | ✓ | ✗ |
| Claude Code | ✓ | ✓ |
| Gemini CLI | ✓ | ✓ |
| **OpenClaw** | ✗ | **✓** |
| Kiro | ✓ | ✗ |

## 检测的安全风险

### MCP Servers
- E001: Prompt Injection
- E002: Tool Shadowing
- E003: Tool Poisoning
- TF001: Toxic Flows

### Agent Skills
- E004: Prompt Injection
- E006: Malware Payloads
- W011: Untrusted Content
- W007: Credential Handling
- W008: Hardcoded Secrets

## 安装

### 前置要求
1. Python 3.x
2. [uv](https://docs.astral.sh/uv/getting-started/installation/) 包管理器

### 可选: Snyk API Token
```bash
# 注册获取 token: https://app.snyk.io/account
export SNYK_TOKEN=your-api-token-here
```

## 使用方法

### 扫描 OpenClaw Skills
```bash
# 扫描所有 OpenClaw skills (默认路径)
uvx snyk-agent-scan@latest --skills

# 扫描指定目录
uvx snyk-agent-scan@latest --skills "D:\OpenClaw\workspace\active_skills"

# 扫描单个 skill
uvx snyk-agent-scan@latest --skills "D:\OpenClaw\workspace\active_skills\pptx\SKILL.md"
```

### 其他命令
```bash
# 完整扫描（自动发现所有 agents + MCP + skills）
uvx snyk-agent-scan@latest --skills

# 只检查工具描述（不验证）
uvx snyk-agent-scan@latest inspect

# JSON 输出
uvx snyk-agent-scan@latest --skills --json

# 详细日志
uvx snyk-agent-scan@latest --skills --verbose
```

## 注意事项

- Agent Scan 会将 skill 名称、描述发送给 Snyk API 进行验证
- 使用 `--opt-out` 可拒绝发送匿名 ID
- 不存储 MCP 工具调用的内容和结果

## 风险

**极低** — 官方安全工具，只读扫描，无破坏性操作