# OpenViking MCP Server

Context database MCP server for AI agents, providing cross-project knowledge sharing, session persistence, and context retrieval.

## Features

- **Session Management**: Create, persist, and recover conversation sessions
- **Tiered Context**: L0 (abstract), L1 (overview), L2 (full) context loading
- **Semantic Search**: Search across all stored context
- **Resource Tree**: Hierarchical view of knowledge base
- **Relation Links**: Connect related contexts

## Installation

```bash
cd 80-PROJECTS/openviking-mcp
pip install -e .
```

## Configuration

Add to Claude Code settings (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "openviking": {
      "command": "py",
      "args": ["D:/OpenClaw/workspace/80-PROJECTS/openviking-mcp/src/server.py"]
    }
  }
}
```

Or using the installed script:

```json
{
  "mcpServers": {
    "openviking": {
      "command": "openviking-mcp"
    }
  }
}
```

## Available Tools

### Session Tools

| Tool | Description |
|------|-------------|
| `session_create` | Create new session |
| `session_info` | Get session details |
| `session_add_message` | Add message to session |
| `session_commit` | Persist session |
| `session_list` | List all sessions |

### Context Tools

| Tool | Description |
|------|-------------|
| `search` | Search context |
| `context_abstract` | L0 summary (~100 tokens) |
| `context_overview` | L1 overview (~2k tokens) |
| `context_read` | L2 full content |
| `context_write` | Store context |

### Resource Tools

| Tool | Description |
|------|-------------|
| `resource_ls` | List resources |
| `resource_tree` | Tree view |
| `relation_link` | Link contexts |
| `relation_list` | Get relations |

## Requirements

- Python 3.10+
- OpenViking (installed via `pip install openviking`)

## Local Deployment

OpenViking requires a local deployment with PostgreSQL + Qdrant. See [OpenViking Docs](https://www.openviking.ai/docs) for setup.
